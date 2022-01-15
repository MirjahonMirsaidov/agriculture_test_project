import jwt
import environ
import requests
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import generics, permissions, status
from rest_framework.response import Response


from agriculture_test_project import settings
from .models import User, Location
from .serializers import UserSerializer, UserCreateSerializer, EmailVerificationSerializer, EmailSerializer, \
    EmailRecoverySerializer, LocationSerializer
from .utils import send_change_password

env = environ.Env()
environ.Env.read_env()


class UserApiView(generics.ListCreateAPIView):
    """
    A view to create user
    """
    serializer_class = UserCreateSerializer


class UserRetireveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """
    A view to get, update user data, and delete it
    """
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_object(self):
        return self.request.user

    def patch(self, request, *args, **kwargs):
        password = request.data.get('password', None)
        user = self.request.user
        self.partial_update(request, *args, **kwargs)
        if password:
            user.set_password(password)
            user.save()
        return Response("User successfully updated", status=status.HTTP_200_OK)


class EmailVerifyView(generics.GenericAPIView):
    """
    A view to verify user email after registration. When user registers it will create user but is_active will be False,
    so only after email verification user will be active and can login
    """
    serializer_class = EmailVerificationSerializer

    def get(self, request):
        token = request.GET.get('token', None)
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if not user.is_active:
                user.is_active = True
                user.save()
                return Response({'email': 'Successfully activated'}, status=status.HTTP_200_OK)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class PasswordRecoveryEmailSentView(generics.GenericAPIView):
    """
    A view to reset user password via email address.
    """
    serializer_class = EmailSerializer

    def post(self, request):
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            send_change_password(user)
            return Response('Password Recovery link has been sent to your email address.', status=status.HTTP_200_OK)
        except ObjectDoesNotExist:
            return Response({'error': 'Wrong email address.'}, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(generics.GenericAPIView):
    """
    After user clicking link which send to email address, user will enter new password and password confirmation.
    """
    serializer_class = EmailRecoverySerializer

    def post(self, request):
        token = request.GET.get('token')
        password1 = request.data.get('password')
        password2 = request.data.get('password_confirm')
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            user = User.objects.get(id=payload['user_id'])
            if password1 == password2:
                user.set_password(password1)
                user.save()
                return Response({'password': 'Password successfully changed'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Passwords does not match!'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.ExpiredSignatureError:
            return Response({'error': 'Activation Expired'}, status=status.HTTP_400_BAD_REQUEST)
        except jwt.exceptions.DecodeError:
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


class LocationCreateListView(generics.ListCreateAPIView):
    """
    A view to create and get list of locations of user
    """
    serializer_class = LocationSerializer
    queryset = Location.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(user_id=self.request.user.pk)


class LocationRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    """
    A view to retrieve, update and delete locations of user
    """
    serializer_class = LocationSerializer
    queryset = Location.objects.all()
    permission_classes = (permissions.IsAuthenticated,)

    def patch(self, request, *args, **kwargs):
        self.partial_update(request, *args, **kwargs)
        return Response("Location successfully updated", status=status.HTTP_200_OK)


class GetWeatherDataView(generics.GenericAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request):
        apiKey = env('OpenWeatherAPIKey')
        location = Location.objects.get(user=request.user)
        serializer = LocationSerializer(location)
        lat, lon = serializer.data.get('geometry').get('coordinates')
        url = f'http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={apiKey}'

        city_weather = requests.get(url).json()
        return Response(city_weather, status=status.HTTP_200_OK)



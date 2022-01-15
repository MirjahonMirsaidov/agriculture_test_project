from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from main.utils import send_email_verification
from main.models import Location


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ('name', 'email', 'password')
        extra_kwargs = {
            'password': {'write_only': True, 'min_length': 5}
        }

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        send_email_verification(user)
        return user


class EmailVerificationSerializer(serializers.ModelSerializer):
    token = serializers.CharField(max_length=256)

    class Meta:
        model = get_user_model()
        fields = ('token', )


class EmailRecoverySerializer(serializers.Serializer):
    password = serializers.CharField(max_length=20)
    password_confirm = serializers.CharField(max_length=20)

    def validate(self, attrs):
        if attrs.get('password') != attrs.get('password_confirm'):
            msg = 'Password confirm does not match.Please make sure password and password confirmation are the same'
            raise serializers.ValidationError(msg)


class EmailSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length=256)


class LocationSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Location
        geo_field = "point"
        fields = ('address', 'city', 'state', 'point')


class UserSerializer(serializers.ModelSerializer):
    region = LocationSerializer(required=False)

    class Meta:
        model = get_user_model()
        fields = ('email', 'name', 'password', 'region', 'company_name')


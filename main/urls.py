from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserApiView, UserRetireveUpdateDeleteView, EmailVerifyView, PasswordRecoveryEmailSentView, ChangePasswordView, \
                   LocationCreateListView, LocationRetrieveUpdateDestroyView, GetWeatherDataView

app_name = 'main'

urlpatterns = [
    path('register/', UserApiView.as_view(), name='create'),
    path('me/', UserRetireveUpdateDeleteView.as_view(), name='me'),
    path('password-reset/', PasswordRecoveryEmailSentView.as_view(), name='password-reset'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('email-verify/', EmailVerifyView.as_view(), name='email-verify'),
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('login/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('region/', LocationCreateListView.as_view()),
    path('region/<int:pk>', LocationRetrieveUpdateDestroyView.as_view()),
    path('weather/', GetWeatherDataView.as_view())
]

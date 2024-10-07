from django.urls import path
from authentication.views import CustomTokenObtainPairView, TwoFactorVerifyView
from authentication.views import UserRegistrationView


urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/verify-2fa/', TwoFactorVerifyView.as_view(), name='verify_2fa'),
]

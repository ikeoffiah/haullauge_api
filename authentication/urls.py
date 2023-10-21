from django.urls import path
from .views import *

urlpatterns = [
    path('register', RegistrationView.as_view()),
    path('verify-otp', OTPVerificationView.as_view()),
    path('login', LoginView.as_view()),
    path('register-driver', DriverRegisterView.as_view()),
    path('agent-verify', AgentVerificationView.as_view()),
    path('forgot-password', ForgotPasswordView.as_view()),
    path('change-password', CompletePasswordChange.as_view()),
    path('resend-otp', ResendOTPView.as_view()),
    path('update-name', UpdateNameView.as_view()),
    path('driver-register', SingleDriverRegistrationView.as_view())
]


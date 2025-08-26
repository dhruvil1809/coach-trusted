from django.urls import path

from authentication.views import LoginView
from authentication.views import LoginWithGoogleView
from authentication.views import PasswordResetConfirmView
from authentication.views import PasswordResetRequestView
from authentication.views import RefreshTokenView
from authentication.views import RegisterConfirmationView
from authentication.views import RegisterView
from authentication.views import ResendVerificationCodeView
from authentication.views import ValidateTokenView

urlpatterns = [
    path("refresh/", RefreshTokenView.as_view(), name="refresh-token"),
    path("validate/", ValidateTokenView.as_view(), name="validate-token"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/google/", LoginWithGoogleView.as_view(), name="login-google"),
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "register/confirm/",
        RegisterConfirmationView.as_view(),
        name="register-confirmation",
    ),
    path(
        "register/resend-code/",
        ResendVerificationCodeView.as_view(),
        name="resend-verification-code",
    ),
    path(
        "password/reset/",
        PasswordResetRequestView.as_view(),
        name="password-reset-request",
    ),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password-reset-confirm",
    ),
]

app_name = "authentication"

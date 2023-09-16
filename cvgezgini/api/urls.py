from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .auth import views as auth
app_name = 'api'

router = DefaultRouter()

urlpatterns = [
    path("register/", auth.RegisterView.as_view(), name="register"),
    path("login/", auth.LoginWithEmailView.as_view(), name="login"),
    path(
        'update-password/',
        auth.UpdatePassword.as_view(),
        name='update-password',
    ),
    path(
        'forgot-password/email/first-step/',
        auth.ForgotPasswordWithEmailFirstStep.as_view(),
        name='forgot-password-with-email-first-step',
    ),
    path(
        'forgot-password/email/second-step/',
        auth.ForgotPasswordWithEmailSecondStep.as_view(),
        name='forgot-password-with-email-second-step',
    ),
] + router.urls

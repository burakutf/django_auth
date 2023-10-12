from rest_framework.routers import DefaultRouter
from django.urls import path
from .auth import views as auth
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework.permissions import IsAuthenticated


app_name = 'api'

router = DefaultRouter()

schema_view = get_schema_view(
    openapi.Info(
        title='Snippets API',
        default_version='v1',
    ),
    public=True,
    permission_classes=(IsAuthenticated, )
)

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
    path('swagger<format>/', schema_view.without_ui(), name='schema-json'),
    path('swagger/', schema_view.with_ui('swagger'), name='schema-swagger-ui'),
] + router.urls

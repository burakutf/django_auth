from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from django.utils.translation import gettext as _
from django.contrib.auth.models import update_last_login

from cvgezgini.apps.accounts.models import User,VerifyCode
from ..utils.permissions import CanAttemptPerm
from .serializers import (
    EmailLoginSerializer,
    EmailSerializers,
    ForgotPasswordSerializer,
    RegisterSerializer,
    UpdatePasswordSerializer, 
    UserProfileSerializer
    )

class LoginWithEmailView(APIView):
    permission_classes = [AllowAny,CanAttemptPerm]

    def post(self, request, *args, **kwargs):
        serializer = EmailLoginSerializer(data=request.POST)
        if not serializer.is_valid():
            return Response(data=serializer.errors, status=400)
        user = User.objects.get(email=serializer.data["email"])
        if not user.is_active:
            return Response(data={"detail": _("Hesabınız aktif değil!")}, status=403)

        token, x = Token.objects.get_or_create(user=user)
        update_last_login(None, user)

        return Response(data={"token": str(token)})


class RegisterView(APIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny,CanAttemptPerm]

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = UserProfileSerializer(instance=user).data
        return Response(data, status=201)

class UpdatePassword(APIView):
    def put(self, request, *args, **kwargs):
        serializer = UpdatePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.update(
            instance=request.user, validated_data=serializer.validated_data
        )
        return Response(
            {'detail': _('Şifreniz başarıyla güncellendi!')}
        )
    
class ForgotPasswordWithEmailFirstStep(APIView):
    """
    1. step of Forgot Password process
    Takes email number, if email exists in records sends a 6 digit code with SMS
    If does not exist just return response without sms
    returns 200 status code
    """

    permission_classes = [AllowAny, CanAttemptPerm]

    def post(self, request, *args, **kwargs):
        serializer = EmailSerializers(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            pass
        else:
            VerifyCode.generate(value=email, is_email=True)
        return Response({'detail': _('Mail gönderildi.')})


class ForgotPasswordWithEmailSecondStep(APIView):
    """
    2. step of Forgot Password process
    takes email, new_password, code(OTP code)
    returns authentication Token
    """

    serializer_class = ForgotPasswordSerializer
    permission_classes = [CanAttemptPerm]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            return Response({'detail': _('Şifre başarıyla güncellendi.')})

        return Response(serializer.errors, status=400)

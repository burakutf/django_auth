import logging

from rest_framework import serializers
from django.utils.translation import gettext as _
from django.contrib.auth.password_validation import validate_password
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from cvgezgini.apps.accounts.models import User,VerifyCode

logger = logging.getLogger("AuthSerializer")

class PasswordField(serializers.CharField):
    def __init__(
        self,
        trim_whitespace=False,
        write_only=True,
        style={'input_type': 'password'},
        **kwargs,
    ):
        super().__init__(
            style=style,
            trim_whitespace=trim_whitespace,
            write_only=write_only,
            **kwargs,
        )

class EmailSerializers(serializers.Serializer):
    email = serializers.EmailField()

class EmailLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = PasswordField()
    token = serializers.CharField(label='Token', read_only=True)

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        if not (email and password):
            msg = _('Email veya şifre gerekli.')
            raise serializers.ValidationError(msg, code='authorization')

        msg = _('Sağlanan kimlik bilgileriyle oturum açılamıyor.')
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError(msg, code='authorization')
        if not user.check_password(password):
            raise serializers.ValidationError(msg, code='authorization')
        return attrs

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True, 
    )
    password = serializers.CharField(
        write_only=True, required=True, validators=[validate_password]
    )

    class Meta:
        model = User
        fields = ("password", "email","first_name", "last_name")
        extra_kwargs = {
            "first_name": {"required": False},
            "last_name": {"required": False},
        }
    
    def create(self, validated_data):
        password = validated_data.pop("password")
        email = validated_data['email']
        user = User.objects.create(**validated_data)

        user.set_password(password)
        user.save()

        try:
            code = VerifyCode.generate(value=email, is_email=True)
        except Exception as e:
            logger.error(
                f"""Error while generating code in RegisterSerializer.
                email={email}, exception={e}"""
            )
        else:
            try:
                code.send()
            except Exception as e:
                logger.error(f"Could not send the code via mail! exception={e}")

        return user


class UserProfileSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name")

    def get_email(self, obj):
        if hasattr(obj, "email"):
            return None
        return obj.email.number



class UpdatePasswordSerializer(serializers.Serializer):
    old_password = PasswordField()
    new_password = PasswordField()

    def update(self, instance, validated_data):
        old_password = validated_data['old_password']
        new_password = validated_data['new_password']
        if not instance.check_password(old_password):
            raise serializers.ValidationError(
                _('Mevcut şifre yanlış!'), code='wrong-password'
            )

        try:
            validate_password(new_password)
        except:
            raise serializers.ValidationError(
                _(
                    'Şifre en az 8 karakterden uzun ve güçlü olmalı.'
                ),
                code='weak-password',
            )

        instance.set_password(new_password)
        instance.save()

        return instance
    

class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(write_only=True)
    new_password = PasswordField()

    def validate(self, attrs):
        email = attrs['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError()

        verifycode = VerifyCode.objects.get(value=email)
        if not verifycode:
            raise serializers.ValidationError()
        if not verifycode.is_valid(value=email,code=attrs['code']):
                raise serializers.ValidationError(_('Kod yanlış veya süresi dolmuş.'))

        try:
            validate_password(attrs['new_password'])
        except:
            raise serializers.ValidationError(
                _(
                    'Şifre en az 8 karakterden uzun ve güçlü olmalı.'
                )
            )

        user.set_password(attrs['new_password'])
        user.save()

        return attrs
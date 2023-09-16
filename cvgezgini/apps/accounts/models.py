from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from random import choice

from phonenumber_field.modelfields import PhoneNumberField

from .utils import (
    CodeExpired,
    generate_invite_code,
    send_email
    )


class User(AbstractUser):
    class Genders(models.TextChoices):
        MAN = 'MN', 'Erkek'
        WOMAN = 'WMN', 'Kadın'
    username = models.CharField(max_length=150, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255,blank=True,null=True)
    phone = PhoneNumberField(null=True, blank=True, db_index=True)
    phone_verified = models.BooleanField(default=False)
    is_premium = models.BooleanField('is premium', default=False)
    birth_date = models.DateField(null=True, blank=True)
    is_online = models.BooleanField('is online', default=False)
    gender = models.CharField(max_length=3, choices=Genders.choices)



    def save(self, *args, **kwargs):
        self.full_name = f'{self.first_name} {self.last_name}'
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.full_name or self.get_full_name() or str(self.id)


class Profile(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    about = models.TextField(blank=True, null=True)
    invite_code = models.CharField(max_length=8, unique=True)

    def __str__(self):
        return str(self.user)

    def save(self, *args, **kwargs):
        if not self.invite_code:
            self.set_invite_code()
        super().save(*args, **kwargs)

    def set_invite_code(self):
        self.invite_code = self._get_an_invite_code()

    def _get_an_invite_code(self):
        while True:
            code = generate_invite_code()
            if Profile.objects.filter(invite_code=code).exists():
                continue
            return code
    
class Invitation(models.Model):
    inviter = models.ForeignKey(
        User, models.CASCADE, 'invitings_as_inviter', null=True, blank=True
    )
    invited = models.OneToOneField(User, models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.inviter} invite {self.invited}'


class VerifyCode(models.Model):
    value = models.CharField(max_length=64,unique=True)  # email or phone
    code = models.CharField(max_length=8)
    is_email = models.BooleanField(default=False)
    is_phone = models.BooleanField(default=False)
    expire_at = models.DateTimeField()

    def __str__(self):
        return self.value

    @classmethod
    def generate(cls, value, is_email=False, is_phone=False, expire_at=None, code=None):
        if is_email == is_phone:
            raise ValidationError(
                "Both is_email and is_phone should not be True or False."
            )

        if code is None:
            code = cls.generate_code()
        elif len(str(code)) != settings.VERIFY_CODE_LENGTH:
            raise ValidationError(f"Code length must be {settings.VERIFY_CODE_LENGTH}")

        if expire_at is None:
            expire_at = now() + settings.VERIFICATION_CODE_EXPIRE_TIME

        return cls.objects.create(
            value=value,
            code=code,
            is_email=is_email,
            is_phone=is_phone,
            expire_at=expire_at,
        )

    @classmethod
    def generate_code(cls):
        if settings.USE_FALLBACK_CODE:
            return settings.VERIFICATION_CODE_FALLBACK
        return "".join(choice("0123456789") for _ in range(settings.VERIFY_CODE_LENGTH))

    @classmethod
    def is_valid(cls, value, code):
        return cls.objects.filter(value=value, code=code, expire_at__gt=now()).exists()

    def send(self):
        if self.expire_at < now():
            raise CodeExpired()

        if self.is_phone and settings.ENABLE_SENDING_SMS:
            pass
            # return send_phone()
        if self.is_email and settings.ENABLE_SENDING_EMAIL:
            pass
            send_email(
                email=self.value,
                message=_(f"Doğrulama kodunuz: {self.code}. \nCvGezgini®"),
            )
        return


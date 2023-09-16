from django.contrib import admin

from .models import (
    User,
    Profile,
    Invitation,
    VerifyCode
)


admin.site.register(User)
admin.site.register(Profile)
admin.site.register(Invitation)
admin.site.register(VerifyCode)
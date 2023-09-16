from django.db import models

# Create your models here.


class AuthAttempt(models.Model):
    """
    Keeping to attempts of login, register, forgot password etc.
    """

    ip = models.GenericIPAddressField()
    email = models.EmailField()
    time = models.DateTimeField(auto_now_add=True)

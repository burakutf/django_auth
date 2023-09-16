
from datetime import timedelta

from django.utils import timezone
from django.db.models import Q
from django.conf import settings

from rest_framework.permissions import BasePermission, SAFE_METHODS
from ipware import get_client_ip
from cvgezgini.apps.core.models import AuthAttempt



class CanAttemptPerm(BasePermission):
    message = (
        'Çok fazla denemede bulundunuz! Bir kaç saat sonra tekrar deneyin!'
    )

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS or not settings.ATTEMPT_PROTECTION:
            return True

        ip, is_routable = get_client_ip(request)

        if (ip is None or not is_routable) and not settings.DEVELOPMENT_MODE:
            self.message = 'Ip adresiniz ile ilgili bir sorun oluştu!'
            return False

        email = request.data.get('email', None)
        a_hour_ago = timezone.now() - timedelta(hours=1)

        total_attempts_in_last_hour = (
            AuthAttempt.objects.filter(
                Q(ip=ip) | Q(email=email), time__gt=a_hour_ago
            )
            .distinct()
            .count()
        )
        if total_attempts_in_last_hour >= 10:
            return False

        AuthAttempt.objects.create(email=email, ip=ip)
        return True

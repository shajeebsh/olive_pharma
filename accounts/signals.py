from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ROLE_ADMIN, ROLE_REP, UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    role = ROLE_ADMIN if instance.is_superuser else ROLE_REP
    UserProfile.objects.get_or_create(user=instance, defaults={"role": role})

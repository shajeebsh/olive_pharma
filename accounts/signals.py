from django.conf import settings
from django.db.models.signals import post_migrate, post_save
from django.dispatch import receiver

from .models import ROLE_ADMIN, ROLE_REP, UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def ensure_user_profile(sender, instance, created, **kwargs):
    if not created:
        return
    role = ROLE_ADMIN if instance.is_superuser else ROLE_REP
    UserProfile.objects.get_or_create(user=instance, defaults={"role": role})


@receiver(post_migrate)
def ensure_superuser_after_migrate(sender, **kwargs):
    if getattr(sender, "name", None) != "accounts":
        return
    from .services import ensure_superuser_from_env

    ensure_superuser_from_env()

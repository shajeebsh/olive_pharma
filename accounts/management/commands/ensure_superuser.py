from django.core.management.base import BaseCommand

from accounts.services import ensure_superuser_from_env


class Command(BaseCommand):
    help = "Create or update the superuser from DJANGO_SUPERUSER_* environment variables."

    def handle(self, *args, **options):
        user = ensure_superuser_from_env()
        if user is None:
            self.stdout.write(
                "Skipped: set both DJANGO_SUPERUSER_EMAIL and "
                "DJANGO_SUPERUSER_PASSWORD to provision an admin."
            )
        else:
            self.stdout.write(self.style.SUCCESS(f"Superuser ready: {user.email}"))

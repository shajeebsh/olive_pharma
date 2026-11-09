from django.core.management.base import BaseCommand, CommandError

from core.services.seeding import seed_rows


class Command(BaseCommand):
    help = "Create Faker-based sample rows for a project model."

    def add_arguments(self, parser):
        parser.add_argument(
            "model",
            help="Model label to seed, for example visits.DoctorVisit.",
        )
        parser.add_argument(
            "--rows",
            type=int,
            default=10,
            help="Number of sample rows to create (default: 10).",
        )

    def handle(self, *args, **options):
        label = options["model"]
        rows = options["rows"]
        if rows < 1 or rows > 1000:
            raise CommandError("--rows must be between 1 and 1000.")

        try:
            created = seed_rows(label, rows)
        except ValueError as exc:
            raise CommandError(str(exc)) from exc

        self.stdout.write(
            self.style.SUCCESS(f"Seeded {created} row(s) for {label}.")
        )

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF
from core.bootstrap import run_startup_tasks, startup_tasks_enabled
from core.models import Doctor, Hospital, Region
from visits.models import DoctorVisit


def make_user(username, role):
    user = get_user_model().objects.create_user(
        username=username, password="password123"
    )
    user.profile.role = role
    user.profile.save()
    return user


class ScopingTests(TestCase):
    def setUp(self):
        self.region = Region.objects.create(name="North")
        self.hospital = Hospital.objects.create(name="City", region=self.region)
        self.doctor = Doctor.objects.create(name="Chen", hospital=self.hospital)
        self.admin = make_user("admin", ROLE_ADMIN)
        self.staff = make_user("staff", ROLE_STAFF)
        self.rep1 = make_user("rep1", ROLE_REP)
        self.rep2 = make_user("rep2", ROLE_REP)

        for rep in (self.rep1, self.rep2):
            DoctorVisit.objects.create(
                rep=rep,
                date="2026-01-10",
                region=self.region,
                hospital=self.hospital,
                doctor=self.doctor,
            )

    def test_rep_sees_only_own_visits(self):
        visits = DoctorVisit.objects.for_user(self.rep1, "rep")
        self.assertEqual(visits.count(), 1)
        self.assertEqual(visits.first().rep, self.rep1)

    def test_admin_and_staff_see_all_visits(self):
        self.assertEqual(DoctorVisit.objects.for_user(self.admin, "rep").count(), 2)
        self.assertEqual(DoctorVisit.objects.for_user(self.staff, "rep").count(), 2)


class HealthTests(TestCase):
    def test_health_endpoint(self):
        response = self.client.get(reverse("health"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")
        self.assertEqual(response.json()["migrations"], "ok")

    @patch("core.views.connection")
    def test_health_reports_database_error(self, connection):
        connection.cursor.side_effect = Exception("database unavailable")

        response = self.client.get(reverse("health"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["status"], "error")
        self.assertEqual(response.json()["database"], "error")


class StartupBootstrapTests(TestCase):
    def test_disabled_without_render_or_override(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertFalse(startup_tasks_enabled())

    def test_enabled_on_render(self):
        with patch.dict(os.environ, {"RENDER": "true"}, clear=True):
            self.assertTrue(startup_tasks_enabled())

    def test_enabled_with_production_settings(self):
        with patch.dict(
            os.environ,
            {"DJANGO_SETTINGS_MODULE": "config.settings.prod"},
            clear=True,
        ):
            self.assertTrue(startup_tasks_enabled())

    def test_override_disables_startup_tasks(self):
        with patch.dict(
            os.environ,
            {"RENDER": "true", "RUN_STARTUP_TASKS": "0"},
            clear=True,
        ):
            self.assertFalse(startup_tasks_enabled())

    def test_migrations_and_superuser_run_once(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            lock_path = Path(temp_dir) / "startup.lock"
            with (
                patch.dict(os.environ, {"RUN_STARTUP_TASKS": "true"}, clear=True),
                patch("core.bootstrap.call_command") as command,
            ):
                self.assertTrue(run_startup_tasks(lock_path))
                command.assert_any_call("migrate", interactive=False, verbosity=0)
                command.assert_any_call("ensure_superuser")

                self.assertFalse(run_startup_tasks(lock_path))
                self.assertEqual(command.call_count, 2)

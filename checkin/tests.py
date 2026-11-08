from datetime import time

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.urls import reverse

from accounts.models import ROLE_REP

from .models import CheckInOut
from .services import check_in, check_out


def make_user(username="rep"):
    user = get_user_model().objects.create_user(
        username=username, password="password123"
    )
    user.profile.role = ROLE_REP
    user.profile.save()
    return user


class CheckInServiceTests(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_check_in_then_out(self):
        record = check_in(user=self.user, date="2026-01-10", check_in_time=time(9, 0))
        self.assertTrue(record.is_open)
        record = check_out(
            user=self.user, date="2026-01-10", check_out_time=time(17, 30)
        )
        self.assertEqual(record.check_out, time(17, 30))
        self.assertEqual(str(record.duration), "8:30:00")

    def test_duplicate_check_in_is_rejected(self):
        check_in(user=self.user, date="2026-01-10")
        with self.assertRaises(ValidationError):
            check_in(user=self.user, date="2026-01-10")

    def test_check_out_without_check_in_is_rejected(self):
        with self.assertRaises(ValidationError):
            check_out(user=self.user, date="2026-01-10")


class CheckInViewTests(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.force_login(self.user)

    def test_check_in_view_creates_record(self):
        response = self.client.post(
            reverse("checkin:check_in"),
            {"date": "2026-01-10", "check_in": "09:00", "notes": ""},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(CheckInOut.objects.count(), 1)

    def test_duplicate_check_in_shows_form_error(self):
        self.client.post(
            reverse("checkin:check_in"),
            {"date": "2026-01-10", "check_in": "09:00", "notes": ""},
        )
        response = self.client.post(
            reverse("checkin:check_in"),
            {"date": "2026-01-10", "check_in": "09:00", "notes": ""},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(CheckInOut.objects.count(), 1)
        self.assertContains(response, "already checked in")

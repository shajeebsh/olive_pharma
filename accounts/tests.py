import os
from unittest.mock import patch

from django.contrib.auth import authenticate, get_user_model
from django.test import TestCase

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF
from accounts.services import ensure_superuser_from_env


class ProfileSignalTests(TestCase):
    def test_profile_created_with_default_role(self):
        user = get_user_model().objects.create_user(
            username="newrep", password="password123"
        )
        self.assertTrue(hasattr(user, "profile"))
        self.assertEqual(user.profile.role, ROLE_REP)

    def test_role_helpers(self):
        user = get_user_model().objects.create_user(
            username="admin", password="password123"
        )
        user.profile.role = ROLE_ADMIN
        user.profile.save()
        self.assertTrue(user.profile.is_admin)
        self.assertFalse(user.profile.is_representative)
        self.assertFalse(user.profile.is_staff_member)

        user.profile.role = ROLE_STAFF
        user.profile.save()
        self.assertTrue(user.profile.is_staff_member)
        self.assertFalse(user.profile.is_admin)


class EnsureSuperuserTests(TestCase):
    env = {
        "DJANGO_SUPERUSER_EMAIL": "owner@example.com",
        "DJANGO_SUPERUSER_PASSWORD": "StrongPass123!",
    }

    @patch.dict(os.environ, env, clear=False)
    def test_creates_superuser_with_admin_profile(self):
        user = ensure_superuser_from_env()

        self.assertIsNotNone(user)
        self.assertEqual(user.username, "owner@example.com")
        self.assertEqual(user.email, "owner@example.com")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_superuser)
        self.assertEqual(user.profile.role, ROLE_ADMIN)
        self.assertTrue(
            authenticate(username="owner@example.com", password="StrongPass123!")
        )

    @patch.dict(os.environ, env, clear=False)
    def test_is_idempotent_and_updates_password(self):
        ensure_superuser_from_env()
        with patch.dict(
            os.environ, {"DJANGO_SUPERUSER_PASSWORD": "NewStrongPass456!"}, clear=False
        ):
            ensure_superuser_from_env()

        users = get_user_model().objects.filter(email="owner@example.com")
        self.assertEqual(users.count(), 1)
        self.assertTrue(
            authenticate(username="owner@example.com", password="NewStrongPass456!")
        )

    @patch.dict(
        os.environ,
        {"DJANGO_SUPERUSER_EMAIL": "", "DJANGO_SUPERUSER_PASSWORD": ""},
        clear=False,
    )
    def test_skips_when_credentials_are_missing(self):
        self.assertIsNone(ensure_superuser_from_env())

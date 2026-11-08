from django.contrib.auth import get_user_model
from django.test import TestCase

from accounts.models import ROLE_ADMIN, ROLE_REP, ROLE_STAFF


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

import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from media.models import Profile
from user.serializers import UserSerializer

USER_URL = reverse("user:create")


class ProfileCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        # self.user = get_user_model().objects.create_superuser(
        #     "admin@test.com",
        #     "pass_word123"
        # )
        # self.client.force_authenticate(self.user)

        self.user_data = {
            "email": "testuser@example.com",
            "password": "test_password01",
            "username": "Admin_test_user",
            "bio": "This is a test bio"
            }

    def test_create_user_with_profile(self):
        response = self.client.post(USER_URL, self.user_data)

        user = get_user_model().objects.get(email=self.user_data["email"])

        self.assertIsNotNone(user)

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.username, self.user_data["username"])
        self.assertEqual(profile.bio, self.user_data["bio"])

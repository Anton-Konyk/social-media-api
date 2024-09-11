import os
import tempfile

from PIL import Image
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from media.models import Profile, movie_image_file_path
from user.serializers import UserSerializer

USER_URL = reverse("user:create")
POSTS_URL = reverse("media:post-list")
LOGOUT_URL = reverse("user:logout")
TOKEN_REFRESH_URL = reverse("user:token_refresh")


class ProfileCreateTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            "email": "testuser@example.com",
            "password": "test_password01",
            "username": "Admin_test_user",
            "profile_pic": "",
            "bio": "This is a test bio"
            }

    def test_create_user_with_profile(self):
        """Test create user with profile"""
        response = self.client.post(USER_URL, self.user_data)

        user = get_user_model().objects.get(email=self.user_data["email"])

        self.assertIsNotNone(user)

        profile = Profile.objects.get(user=user)
        self.assertEqual(profile.username, self.user_data["username"])
        self.assertEqual(profile.bio, self.user_data["bio"])

    def test_create_user_with_image_profile(self):
        """Test create user with image"""
        with tempfile.NamedTemporaryFile(suffix=".jpg") as ntf:
            img = Image.new("RGB", (10, 10))
            img.save(ntf, format="JPEG")
            ntf.seek(0)
            data_with_image = {**self.user_data, "profile_pic": ntf}
            response = self.client.post(USER_URL, data_with_image, format="multipart")
        user = get_user_model().objects.get(email=self.user_data["email"])
        profile = Profile.objects.get(user=user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(profile.profile_pic.name.endswith('.jpg'))
        self.assertTrue(os.path.exists(profile.profile_pic.path))

    def test_create_user_with_image_bad_request(self):
        """Test uploading an invalid image"""
        data_with_image = {**self.user_data, "profile_pic": "not image"}
        response = self.client.post(USER_URL, data_with_image, format="multipart")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UnauthenticatedSocialMediaApiTests(TestCase):

    def setUp(self) -> None:
        self.client = APIClient()

    def test_auth_required(self):
        """Test that user can't be accessed without authenticated"""
        res = self.client.get(POSTS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class LogoutViewTests(APITestCase):

    def setUp(self):

        self.user = get_user_model().objects.create_user(
            email="testuser@example.com",
            password="test_password12"
        )

        self.refresh = RefreshToken.for_user(self.user)
        self.client = APIClient()
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.refresh.access_token}")

    def test_logout_success(self):
        """Test logout"""
        response = self.client.post(LOGOUT_URL)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertIn("detail", response.data)
        self.assertEqual(response.data["detail"], "Successfully logged out.")

        refresh_response = self.client.post(
            TOKEN_REFRESH_URL,
            {"refresh": str(self.refresh)},
        )
        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(refresh_response.data["detail"], "Token is blacklisted")

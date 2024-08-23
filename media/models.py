import os
import uuid

from django.contrib.auth import get_user_model
from django.db import models

from user.models import User
from django.utils.text import slugify


def movie_image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    filename = f"{slugify(instance.user.email)}-{uuid.uuid4()}{extension}"

    if isinstance(instance, Profile):
        folder = "profile_pics"
    else:
        folder = "post_image"

    return os.path.join(f"media_files/uploads/{folder}/", filename)


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_pic = models.ImageField(upload_to=movie_image_file_path, null=True, blank=True)
    bio = models.CharField(max_length=400, null=True, blank=True)
    following = models.ManyToManyField(
        "self",
        symmetrical=False,
        related_name="followers",
        blank=True
    )

    def __str__(self):
        return f"{self.user.email} Profile"

    class Meta:
        verbose_name_plural = "profiles"


class Post(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=255)
    message = models.TextField(max_length=500, null=True, blank=True)
    image = models.ImageField(upload_to=movie_image_file_path, null=True, blank=True)
    hashtag = models.CharField(max_length=255, null=True, blank=True)
    scheduled_publish_time = models.DateTimeField(null=True, blank=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.owner.email} Title: {self.title[0:10]}"

    class Meta:
        verbose_name_plural = "posts"


class Comment(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    comment = models.TextField(max_length=500, null=True, blank=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.email} Comment: {self.comment[0:10]}"

    class Meta:
        verbose_name_plural = "comments"
        ordering = ["post", "created_at"]


class UserReaction(models.Model):
    STATUS_CHOICES = (
        ("D", "Dislike"),
        ("L", "Like"),
    )

    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reactions")
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="reactions")
    reaction = models.CharField(max_length=1, choices=STATUS_CHOICES, default="L")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner.email} Post: {self.post.title[0:10]} Reaction: {self.reaction}"

    class Meta:
        verbose_name_plural = "reactions"
        ordering = ["post", "created_at"]

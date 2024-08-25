from django.urls import path, include
from rest_framework import routers

from media.views import (
    ProfileViewSet,
    ProfileFollowingToMeViewSet,
)

app_name = "media"

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register(
    "following_to_me",
    ProfileFollowingToMeViewSet,
    basename="profile-following-to-me"
)

urlpatterns = [
    path("", include(router.urls))
]

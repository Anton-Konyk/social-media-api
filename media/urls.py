from django.urls import path, include
from rest_framework import routers

from media.views import (
    ProfileViewSet,
    ProfileFollowingToMeViewSet,
    SetFollowView,
    UnFollowView,
    PostViewSet,
    MyFollowingView,
)

app_name = "media"

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)
router.register(
    "following_to_me",
    ProfileFollowingToMeViewSet,
    basename="profile-following-to-me"
)
router.register("posts", PostViewSet)

urlpatterns = [
    path("", include(router.urls)),
    path("set-follow/<int:user_id>/", SetFollowView.as_view(), name="set-follow"),
    path("unfollow/<int:user_id>/", UnFollowView.as_view(), name="unfollow"),
    path("my-followings/", MyFollowingView.as_view(), name="my-followings")
]

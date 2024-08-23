from django.urls import path, include
from rest_framework import routers

from media.views import (
    ProfileViewSet,
)

app_name = "media"

router = routers.DefaultRouter()
router.register("profiles", ProfileViewSet)

urlpatterns = [
    path("", include(router.urls))
]

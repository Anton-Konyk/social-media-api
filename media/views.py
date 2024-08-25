from django.db.models import Q
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from media.permissions import IsOwnerProfile
from media.serializers import (
    ProfileSerializer,
    ProfileImageSerializer,
    ProfileFollowingToMeSerializer
)
from media.models import Profile


class ProfileViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    @staticmethod
    def _params_to_ints(query_string):
        """Converts a string of format '1,2,3' to a list of integers [1,2,3]"""
        return [int(str_id) for str_id in query_string.split(",")]

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAuthenticated, IsOwnerProfile],
        url_path="upload-image_profile",
        serializer_class=ProfileImageSerializer,
    )
    def upload_image(self, request, pk=None):
        profile = self.get_object()
        serializer = self.get_serializer(profile, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        permission = IsOwnerProfile()
        if not permission.has_object_permission(request, self, instance):
            return Response({"detail": "You do not have permission to perform this action."},
                            status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):

        if Profile.objects.filter(user=request.user).exists():
            return Response({"detail": "Profile already exists."},
                            status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        queryset = self.queryset
        username = self.request.query_params.get("username")
        bio = self.request.query_params.get("bio")
        followers = self.request.query_params.get("following")

        if username:
            username_ids = (Profile.objects.
                            filter(username__icontains=username).
                            values_list("id")
                            )
            queryset = Profile.objects.filter(id__in=username_ids)

        if bio:
            bio_ids = (Profile.objects.
                       filter(bio__icontains=bio).
                       values_list("id")
                       )
            queryset = (
                Profile.objects.filter(id__in=bio_ids))

        if username and bio:
            queryset = (
                Profile.objects.
                filter(Q(id__in=username_ids) &
                       Q(id__in=bio_ids)))

        if followers:
            followers_ids = self._params_to_ints(followers)
            queryset = Profile.objects.filter(following__in=followers_ids)

        if followers and username:
            queryset = (
                Profile.objects.
                filter(Q(id__in=username_ids) &
                       Q(following__in=followers_ids)))

        if self.action == ("list", "retrieve"):
            queryset = Profile.objects.prefetch_related("following")

        return queryset

    # @extend_schema(
    #     parameters=[
    #         OpenApiParameter(
    #             "source",
    #             type={"type": "string", "items": {"type": "name"}},
    #             description="Filter by source station id ex. ?source=Berlin",
    #
    #         ),
    #         OpenApiParameter(
    #             "destination",
    #             type={"type": "string", "items": {"type": "name"}},
    #             description="Filter by destination station id ex. "
    #                         "?destination=Vien",
    #
    #         ),
    #     ]
    # )
    def list(self, request, *args, **kwargs):
        """Get list of profiles."""
        return super().list(request, *args, **kwargs)


class ProfileFollowingToMeViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    serializer_class = ProfileFollowingToMeSerializer

    def get_queryset(self):
        user = self.request.user
        current_profile = user.profile

        if current_profile:
            queryset = Profile.objects.filter(following=current_profile)
        else:
            queryset = Profile.objects.none()
            raise Profile.DoesNotExist("Profile does not exist for the user.")

        return queryset

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import mixins, status, views, generics
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from media.permissions import IsOwnerProfile
from media.serializers import (
    ProfileSerializer,
    ProfileImageSerializer,
    ProfileFollowingToMeSerializer,
    PostListSerializer,
    PostImageSerializer,
    PostCreateSerializer,
    UserReactionListSerializer,
    UserReactionCreateSerializer,
    CommentCreateSerializer,
    AllCommentsOfPostSerializer,
)
from media.models import Profile, Post, UserReaction, Comment


class ProfileViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """Get create, retrieve, update and list with filters a user profile"""
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
            return Response(
                {
                      "detail":
                      "You do not have permission to perform this action."
                      },
                status=status.HTTP_403_FORBIDDEN
            )
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type={"type": "string", "items": {"type": "username"}},
                description="Filter by username incentive. Ex. ?username=admin",

            ),
            OpenApiParameter(
                "bio",
                type={"type": "string", "items": {"type": "bio"}},
                description="Filter by bio incentive. Ex. "
                            "?bio=hard",

            ),
            OpenApiParameter(
                "following",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by user_id following. Ex. "
                            "?following=1,2",

            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of profiles."""
        return super().list(request, *args, **kwargs)


class ProfileFollowingToMeViewSet(
    mixins.ListModelMixin,
    GenericViewSet
):
    """Return list of profiles that follow me."""
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


class SetFollowView(views.APIView):
    """Set user's followed"""
    serializer_class = ProfileSerializer

    def post(self, request, user_id):
        current_user = self.request.user
        target_user = get_object_or_404(get_user_model(), id=user_id)

        current_profile = Profile.objects.get(user=current_user)
        target_profile = Profile.objects.get(user=target_user)
        print(current_profile)
        print(target_profile)
        if target_profile in current_profile.following.all():
            return Response({"detail": f"You already have following to "
                             f"the user :{target_profile.username} with "
                             f"user_id: {target_profile.user_id}."},
                            status=status.HTTP_200_OK
                            )
        else:
            current_profile.following.add(target_profile)

            return Response(
                {"detail": "You have subscribed successfully."},
                status=status.HTTP_200_OK
            )


class UnFollowView(views.APIView):
    """Unfollow (unsubscribe) user"""
    serializer_class = ProfileSerializer

    def post(self, request, user_id):
        current_user = self.request.user
        target_user = get_object_or_404(get_user_model(), id=user_id)

        current_profile = Profile.objects.get(user=current_user)
        target_profile = Profile.objects.get(user=target_user)

        if target_profile in current_profile.following.all():
            current_user.profile.following.remove(target_profile)
            return Response(
                {"detail": "You unsubscribed successfully."},
                status=status.HTTP_200_OK
            )
        else:
            return Response({"detail": f"You already have unsubscribed from "
                             f"the user :{target_profile.username} "
                             f"with user_id: {target_profile.user_id}."},
                            status=status.HTTP_200_OK
                            )


class MyFollowingView(generics.GenericAPIView, mixins.ListModelMixin):
    """Get list of user's following"""
    serializer_class = ProfileSerializer

    def get_queryset(self):
        current_user = self.request.user
        current_profile = get_object_or_404(Profile, user=current_user)
        queryset = current_profile.following.all()

        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class MySubscribersView(generics.GenericAPIView, mixins.ListModelMixin):
    """Get list of user's subscribers."""
    serializer_class = ProfileSerializer

    def get_queryset(self):
        current_user = self.request.user

        queryset = Profile.objects.filter(following=current_user.profile)
        return queryset

    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)


class PostViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """Manage user's posts (create, retrieve, list with filters)."""
    # queryset = Post.objects.filter(is_published=True)
    queryset = Post.objects.all()
    serializer_class = PostListSerializer

    @action(
        methods=["POST"],
        detail=True,
        permission_classes=[IsAuthenticated, IsOwnerProfile],
        url_path="upload-image_post",
        serializer_class=PostImageSerializer,
    )
    def upload_image(self, request, pk=None):
        post = self.get_object()
        serializer = self.get_serializer(post, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == "list":
            return PostListSerializer
        if self.action == "create":
            return PostCreateSerializer
        if self.action == "retrieve":
            return PostListSerializer
        elif self.action == "upload_image":
            return PostImageSerializer
        return super().get_serializer_class()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):

        queryset = super().get_queryset()
        username = self.request.query_params.get("username")
        title = self.request.query_params.get("title")
        message = self.request.query_params.get("message")
        hashtag = self.request.query_params.get("hashtag")

        filters = Q()

        if username:
            filters &= Q(user__profile__username__icontains=username)

        if title:
            filters &= Q(title__icontains=title)

        if message:
            filters &= Q(message__icontains=message)

        if hashtag:
            filters &= Q(hashtag__icontains=hashtag)

        queryset = queryset.filter(filters)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                type={"type": "string", "items": {"type": "username"}},
                description="Filter by username incentive. Ex. ?username=admin",

            ),
            OpenApiParameter(
                "title",
                type={"type": "string", "items": {"type": "title"}},
                description="Filter by title incentive. Ex. "
                            "?title=about",

            ),
            OpenApiParameter(
                "message",
                type={"type": "string", "items": {"type": "message"}},
                description="Filter by message incentive. Ex. "
                            "?message=info",

            ),
            OpenApiParameter(
                "hashtag",
                type={"type": "string", "items": {"type": "hashtag"}},
                description="Filter by hashtag incentive. Ex. "
                            "?hashtag=friends",

            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of posts."""
        return super().list(request, *args, **kwargs)


class UserReactionViewSet(
    mixins.CreateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    """Get create and list user's reactions with filters."""
    serializer_class = UserReactionListSerializer

    def perform_create(self, serializer):
        user = self.request.user
        post = serializer.validated_data["post"]
        if post.user_id == user.id:
            raise ValidationError({"detail": "You cannot like your own post."})

        serializer.save(user=user)

    def get_serializer_class(self):
        if self.action == "list":
            return UserReactionListSerializer
        if self.action == "create":
            return UserReactionCreateSerializer
        return super().get_serializer_class()

    def get_queryset(self):
        user = self.request.user
        queryset = UserReaction.objects.filter(user=user)
        post = self.request.query_params.get("post")
        reaction = self.request.query_params.get("reaction")

        filters = Q()

        if post:
            filters &= Q(post__user=post)

        if reaction:
            filters &= Q(reaction__icontains=reaction)

        queryset = queryset.filter(filters)
        return queryset

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "post",
                type={"type": "string", "items": {"type": "number"}},
                description="Filter by post ID. Ex. ?post=1",

            ),
            OpenApiParameter(
                "reaction",
                type={"type": "string", "items": {"type": "reaction"}},
                description="Filter by reaction incentive (D, L). Ex. "
                            "?title=L",

            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of user reactions."""
        return super().list(request, *args, **kwargs)


class CommentCreationViewSet(
    mixins.CreateModelMixin,
    GenericViewSet
):
    """Create a new comment."""
    serializer_class = CommentCreateSerializer
    queryset = UserReaction.objects.all()

    def get_queryset(self):
        user = self.request.user
        queryset = Comment.objects.filter(user=user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class AllCommentsOfPostView(GenericViewSet, mixins.RetrieveModelMixin):
    """Shows (retrieve) all comments of post."""
    serializer_class = AllCommentsOfPostSerializer
    queryset = Post.objects.all()

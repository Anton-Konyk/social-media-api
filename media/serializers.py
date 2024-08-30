from rest_framework import serializers

from media.models import Profile, Post, UserReaction, Comment


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        many=False,
        slug_field="email"
    )
    following = serializers.SlugRelatedField(
        read_only=True,
        many=True,
        slug_field="user.email"
    )

    class Meta:
        model = Profile
        fields = ("user_id", "user", "username", "profile_pic", "bio", "following")
        extra_kwargs = {"profile_pic": {"read_only": True}}


class ProfileImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("id", "profile_pic")


class ProfileFollowingToMeSerializer(serializers.ModelSerializer):
    following = serializers.SlugRelatedField(
        read_only=True,
        many=True,
        slug_field="user.email"
    )

    class Meta:
        model = Profile
        fields = ("username", "following")
        ordering = ["username"]


class PostListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        many=False,
        slug_field="email"
    )
    username = serializers.SlugRelatedField(
        source="user.profile",
        read_only=True,
        many=False,
        slug_field="username"
    )

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "username",
            "title",
            "message",
            "image",
            "hashtag",
            "scheduled_publish_time",
            "is_published",
        )
        extra_kwargs = {"image": {"read_only": True}}


class PostImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = ("id", "image")


class PostCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Post
        fields = (
            "id",
            "user",
            "title",
            "message",
            "hashtag",
            "scheduled_publish_time",
        )
        extra_kwargs = {"user": {"read_only": True}}


class UserReactionListSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(
        read_only=True,
        many=False,
        slug_field="email"
    )
    username = serializers.SlugRelatedField(
        source="user.profile",
        read_only=True,
        many=False,
        slug_field="username"
    )
    title = serializers.SlugRelatedField(
        source="post",
        read_only=True,
        many=False,
        slug_field="title"
    )
    post_username = serializers.SlugRelatedField(
        source="post.user.profile",
        read_only=True,
        many=False,
        slug_field="username"
    )
    message = serializers.SlugRelatedField(
        source="post",
        read_only=True,
        many=False,
        slug_field="message"
    )

    class Meta:
        model = UserReaction
        fields = ("id", "user", "username", "post_username", "title", "message", "reaction")


class UserReactionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserReaction
        fields = ("id", "post", "reaction")


class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ("id", "user", "comment", "post")
        extra_kwargs = {"user": {"read_only": True}}


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        source="user.profile",
        read_only=True,
        many=False,
        slug_field="username"
    )

    class Meta:
        model = Comment
        fields = ("id", "username", "comment", "post", "created_at")


class AllCommentsOfPostSerializer(serializers.ModelSerializer):
    post_username = serializers.SlugRelatedField(
        source="post.user.profile",
        read_only=True,
        many=False,
        slug_field="username"
    )
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            "id",
            "post_username",
            "title",
            "message",
            "image",
            "hashtag",
            "scheduled_publish_time",
            "comments",
        )

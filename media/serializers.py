from rest_framework import serializers

from media.models import Profile


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
        fields = ("id", "user", "username", "profile_pic", "bio", "following")
        extra_kwargs = {"profile_pic": {"read_only": True}}


class ProfileImageSerializer(serializers.ModelSerializer):

    class Meta:
        model = Profile
        fields = ("id", "profile_pic")

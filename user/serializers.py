from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from media.models import Profile


class UserSerializer(serializers.ModelSerializer):
    profile_pic = serializers.ImageField(
        source="profile.profile_pic",
        required=False
    )
    username = serializers.CharField(source="profile.username")
    bio = serializers.CharField(source="profile.bio", required=False)

    class Meta:
        model = get_user_model()
        fields = (
            "id",
            "email",
            "password",
            "username",
            "profile_pic",
            "bio",
        )
        extra_kwargs = {
            "password": {
                "write_only": True,
                "min_length": 5,
                "style": {"input_type": "password"},
                "label": _("Password"),
                "required": False
                }
            }

    def create(self, validated_data):
        profile_data = validated_data.pop("profile", None)

        user = get_user_model().objects.create_user(**validated_data)
        Profile.objects.create(user=user, **profile_data)

        return user

    def update(self, instance, validated_data):
        """Update User with encrypted password"""
        password = validated_data.pop("password", None)
        profile_data = validated_data.pop("profile", None)
        user = super().update(instance, validated_data)

        if password:
            user.set_password(password)
            user.save()

        if profile_data:
            profile, _ = Profile.objects.get_or_create(
                user=user,
                defaults=profile_data
            )
            for attr, value in profile_data.items():
                setattr(profile, attr, value)
            profile.save()

        return user


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.CharField(
        label=_("Email address"),
        write_only=True
    )
    password = serializers.CharField(
        label=_("Password"),
        style={'input_type': 'password'},
        trim_whitespace=False,
        write_only=True
    )
    token = serializers.CharField(
        label=_("Token"),
        read_only=True
    )

    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")

        if email and password:
            user = authenticate(request=self.context.get("request"),
                                email=email, password=password)

            # The authenticate call simply returns None for is_active=False
            # users. (Assuming the default ModelBackend authentication
            # backend.)
            if not user:
                msg = _('Unable to log in with provided credentials.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = _('Must include "email" and "password".')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class LogoutSerializer(serializers.Serializer):
    detail = serializers.CharField(read_only=True)

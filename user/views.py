from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.settings import api_settings
from rest_framework_simplejwt.tokens import (
    OutstandingToken,
    BlacklistedToken
)

from user.serializers import (
    UserSerializer,
    AuthTokenSerializer,
    LogoutSerializer
)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()


class LoginUserView(ObtainAuthToken):
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    serializer_class = AuthTokenSerializer


class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user


class LogoutView(GenericAPIView):
    """Logout user with moving token to blacklist"""
    permission_classes = (IsAuthenticated,)
    serializer_class = LogoutSerializer

    @extend_schema(
        request=None,
        responses={204: LogoutSerializer, 400: LogoutSerializer},
    )
    def post(self, request):
        try:
            tokens = OutstandingToken.objects.filter(user=self.request.user)
            for token in tokens:
                BlacklistedToken.objects.get_or_create(token=token)

            return Response({"detail": "Successfully logged out."}, status=204)
        except Exception as e:
            return Response({"detail": str(e)}, status=400)

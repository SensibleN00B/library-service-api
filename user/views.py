from drf_spectacular.utils import extend_schema, OpenApiResponse
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated

from user.serializers import ManageUserSerializer, UserSerializer

@extend_schema(
    description="Register a new user with email and password. No authentication required.",
    responses={
        201: OpenApiResponse(description="User successfully created"),
        400: OpenApiResponse(description="Validation errors"),
    }
)
class UserCreateView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = ()


@extend_schema(
    description="Retrieve or update authenticated user's profile. User must be logged in.",
    responses={
        200: OpenApiResponse(description="User profile retrieved or updated"),
        401: OpenApiResponse(description="Authentication credentials were not provided"),
    }
)
class ManageUserView(generics.RetrieveUpdateAPIView):
    serializer_class = ManageUserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

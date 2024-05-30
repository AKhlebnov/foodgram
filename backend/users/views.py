from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.contrib.auth import get_user_model

from .serializers import (
    UserSerializer,
    UserCreateSerializer,
    AvatarUpdateDeleteSerializer
)

User = get_user_model()


# class UserViewSet(viewsets.ModelViewSet):
#     queryset = User.objects.all()
#     permission_classes = [AllowAny]
#     http_method_names = ['get', 'post', ]

#     def get_serializer_class(self):
#         if self.request.method in ['POST']:
#             return UserCreateSerializer
#         return UserSerializer


class CurrentUserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class UpdateDeleteAvatarViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarUpdateDeleteSerializer

    def get_object(self):
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        user = self.get_object()
        user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

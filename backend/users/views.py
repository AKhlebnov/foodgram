from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError
from django.contrib.auth import get_user_model

from .serializers import (
    UserSerializer,
    AvatarUpdateDeleteSerializer,
    SubscriptionSerializers
)
from recipes.models import Subscription

User = get_user_model()


class CurrentUserViewSet(viewsets.ModelViewSet):
    """
    Класс представления для работы с текущим пользователем.
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Метод получения текущего пользователя.
        """

        return self.request.user


class UpdateDeleteAvatarViewSet(
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    """
    Класс представления для обновления и удаления аватара пользователя.
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = AvatarUpdateDeleteSerializer

    def get_object(self):
        """
        Метод получения текущего пользователя.
        """

        return self.request.user

    def destroy(self, request, *args, **kwargs):
        """
        Метод удаления аватара пользователя.
        """

        user = self.get_object()
        if user.avatar:
            user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionsViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    viewsets.GenericViewSet
):
    """
    Класс представления для управления подписками пользователей.
    """

    queryset = Subscription.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = SubscriptionSerializers

    def create(self, request, *args, **kwargs):
        """
        Метод создания новой подписки на автора.
        """

        user = self.request.user
        author = get_object_or_404(User, pk=self.kwargs['pk'])
        context = {'request': request, 'author': author, 'user': user}
        serializer = self.get_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_object(self):
        """
        Метод получения подписки пользователя на автора.
        """

        user = self.request.user
        author = get_object_or_404(User, pk=self.kwargs['pk'])
        if not Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                'У вас нет подписки на этого автора.'
            )
        obj = Subscription.objects.get(user=user, author=author)
        return obj

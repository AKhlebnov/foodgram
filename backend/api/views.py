import os

from django.http import FileResponse
from django.urls import reverse
from django.utils import baseconv
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Recipe, Tag, Ingredient
from foodgram.settings import PDF_DIR
from .serializers import (
    RecipeSerializer, RecipeCreateUpdateSerializer,
    TagSerializer, IngredientSerializer, FavoriteSerializer,
    ShoppingCartSerializer
)
from .filters import RecipeFilter, IngredientFilter
from .utils import generate_shopping_cart_pdf, generate_short_link
from .permissions import IsOwnerOrReadOnly


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Класс представления для обработки CRUD операций для модели Recipe.
    Предоставляет эндпоинты для получения, создания, обновления,
    удаления рецептов, а также для выполнения пользовательских действий,
    таких как добавление рецептов в избранное и в корзину, и генерация
    коротких ссылок для рецептов.
    """

    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """
        Метод возвращает соответствующий класс сериализатора
        в зависимости от действия.
        """

        if self.action == 'shopping_cart':
            return ShoppingCartSerializer
        if self.action == 'favorite':
            return FavoriteSerializer
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def get_permissions(self):
        """
        Метод возвращает соответствующие разрешения в зависимости
        от действия и метода запроса.
        """

        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        if self.action in ['favorite', 'shopping_cart']:
            return [permissions.IsAuthenticated()]
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        if self.request.method in ['PUT', 'PATCH', 'DELETE']:
            return [IsOwnerOrReadOnly()]
        return [permissions.AllowAny()]

    def perform_create(self, serializer):
        """
        Метод сохраняет рецепт с указанием
        текущего пользователя в качестве автора.
        """

        serializer.save(author=self.request.user)

    @action(
        detail=True, methods=['get'], url_path='get-link'
    )
    def get_link(self, request, pk=None):
        """
        Метод возвращает короткую ссылку для рецепта.
        """

        get_object_or_404(Recipe, pk=pk)
        short_string = generate_short_link(pk)
        full_url = request.build_absolute_uri(
            reverse('recipe-short-link', kwargs={'short_string': short_string})
        )
        return Response({'short-link': full_url})

    @action(
        detail=True, methods=['post', 'delete'], url_path='favorite'
    )
    def favorite(self, request, pk=None):
        """
        Метод добавляет или удаляет рецепт из
        избранного для текущего пользователя.
        """

        recipe = get_object_or_404(Recipe, pk=pk)
        context = {'request': request, 'recipe': recipe}

        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            serializer = self.get_serializer(
                data=request.data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True, methods=['post', 'delete'], url_path='shopping_cart'
    )
    def shopping_cart(self, request, pk=None):
        """
        Метод добавляет или удаляет рецепт из
        корзины для текущего пользователя.
        """

        recipe = get_object_or_404(Recipe, pk=pk)
        context = {'request': request, 'recipe': recipe}

        if request.method == 'POST':
            serializer = self.get_serializer(
                data=request.data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            serializer = self.get_serializer(
                data=request.data,
                context=context
            )
            serializer.is_valid(raise_exception=True)
            serializer.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False, methods=['get'], url_path='download_shopping_cart'
    )
    def download_shopping_cart(self, request):
        """
        Метод генерирует PDF файл со списком покупок
        для текущего пользователя и возвращает его.
        """

        user = request.user
        recipes = Recipe.objects.filter(in_shopping_carts__user=user)

        file_name = generate_shopping_cart_pdf(recipes, user)
        file_path = os.path.join(PDF_DIR, file_name)
        response = FileResponse(
            open(file_path, 'rb'),
            content_type='application/pdf'
        )
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response


class ShortLinkRedirectView(RedirectView):
    """
    Класс обрабатывает перенаправление по короткой
    ссылке на полный URL рецепта.
    """

    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        """
        Метод возвращает полный URL рецепта,
        используя декодированную короткую ссылку.
        """

        short_string = kwargs['short_string']
        recipe_id = baseconv.base62.decode(short_string)
        get_object_or_404(Recipe, pk=recipe_id)
        full_url = reverse('recipe-detail', kwargs={'pk': recipe_id})
        return full_url.replace('/api', '')


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс представления для обработки операций чтения из модели Tag.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (permissions.AllowAny, )
    pagination_class = None


class IngredientsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс представления для обработки операций чтения из модели Tag.
    """

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (permissions.AllowAny, )
    filter_backends = (DjangoFilterBackend, )
    pagination_class = None
    filterset_class = IngredientFilter

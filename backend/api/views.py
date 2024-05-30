from django.urls import reverse
from django.utils import baseconv
from django.shortcuts import get_object_or_404
from django.views.generic import RedirectView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from recipes.models import Recipe
from .serializers import RecipeSerializer, RecipeCreateUpdateSerializer
from .filters import RecipeFilter


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (permissions.AllowAny, )
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['get'])
    def get_link(self, request, pk=None):
        get_object_or_404(Recipe, pk=pk)
        short_link = self._generate_short_link(pk)
        full_url = request.build_absolute_uri(short_link)
        full_url = full_url.replace('/api', '')
        return Response({'short-link': full_url})

    def _generate_short_link(self, recipe_id):
        short_string = baseconv.base62.encode(recipe_id)
        return reverse(
            'recipe-short-link',
            kwargs={'short_string': short_string}
        )


class ShortLinkRedirectView(RedirectView):
    permanent = False

    def get_redirect_url(self, *args, **kwargs):
        short_string = kwargs['short_string']
        recipe_id = baseconv.base62.decode(short_string)
        get_object_or_404(Recipe, pk=recipe_id)
        return reverse('recipe-detail', kwargs={'pk': recipe_id})

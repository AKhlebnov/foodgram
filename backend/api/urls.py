from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, TagViewSet, IngredientsViewSet

router_v1 = DefaultRouter()

router_v1.register('ingredients', IngredientsViewSet, basename='ingredient')
router_v1.register('recipes', RecipeViewSet, basename='recipe')
router_v1.register('tags', TagViewSet, basename='tag')

urlpatterns = [
    path('', include(router_v1.urls)),
]

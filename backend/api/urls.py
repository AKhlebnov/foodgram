from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import RecipeViewSet, ShortLinkRedirectView

router_v1 = DefaultRouter()
router_v1.register('recipes', RecipeViewSet, basename='recipe')

urlpatterns = [
    path('recipes/<int:pk>/get-link/', RecipeViewSet.as_view({'get': 'get_link'}), name='recipe-get-link'),
    path('', include(router_v1.urls)),
]

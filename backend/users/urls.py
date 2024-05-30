from django.urls import include, path

from .views import CurrentUserViewSet, UpdateDeleteAvatarViewSet

urlpatterns = [
    path(
        'users/me/',
        CurrentUserViewSet.as_view({'get': 'retrieve'}),
        name='current-user'
    ),
    path(
        'users/me/avatar/',
        UpdateDeleteAvatarViewSet.as_view(
            {'put': 'update', 'patch': 'partial_update', 'delete': 'destroy'}
        ),
        name='update-avatar'
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

from django.urls import include, path

from .views import (CurrentUserViewSet, SubscriptionsViewSet,
                    UpdateDeleteAvatarViewSet)

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
    path(
        'users/subscriptions/',
        SubscriptionsViewSet.as_view({'get': 'list'}),
        name='subscriptions-list'
    ),
    path(
        'users/<int:author_id>/subscribe/',
        SubscriptionsViewSet.as_view({'post': 'create', 'delete': 'destroy'}),
        name='subscribe-user'
    ),
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
]

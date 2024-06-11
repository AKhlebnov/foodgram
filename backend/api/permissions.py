from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Права на уровне объектов, которые позволяют только владельцам
    объекта редактировать его.
    """

    def has_object_permission(self, request, view, obj):
        """
        Метод проверки разрешений на объект.
        """

        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
        )

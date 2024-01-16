from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользователь может изменять и удалять свои данные,
    администраторы, модераторы и суперпользователи
    могут редактировать любые данные.
    """
    def has_permission(self, request, view):
        if (request.method in permissions.SAFE_METHODS
           or request.user.is_authenticated):
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (request.user == obj.author or request.user.is_moderator
                or request.user.is_admin)


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Проверяем, аутентифицирован ли пользователь
        if not request.user.is_authenticated:
            return False
            # Проверяем, является ли пользователь администратором
        return request.user.is_admin

    def has_object_permission(self, request, view, obj):
        return request.user.is_admin


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешение для безопасных методов (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для POST и DELETE разрешено только администраторам
        return (request.user and request.user.is_authenticated
                and request.user.is_admin)

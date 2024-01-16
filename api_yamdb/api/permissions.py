from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользователь может изменять и удалять свои данные,
    администраторы, модераторы и суперпользователи
    могут редактировать любые данные.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS or (
           request.user.is_authenticated):
            return True

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        return (request.user == obj.author or request.user.role == 'moderator'
                or request.user.role == 'admin')


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        # Проверяем, аутентифицирован ли пользователь
        if request.user.is_authenticated:
            # Проверяем, является ли пользователь администратором
            return request.user.role == 'admin'

    def has_object_permission(self, request, view, obj):
        return request.user.role == 'admin'


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешение для безопасных методов (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для POST и DELETE разрешено только администраторам
        return (request.user and request.user.is_authenticated
                and request.user.role == 'admin')

    def has_object_permission(self, request, view, obj):
        # Если нужно применять разрешения к конкретному объекту
        # Может быть использовано в случае с detail-действиями
        return self.has_permission(request, view)


class IsAdminOrAuthorized(permissions.BasePermission):
    def has_permission(self, request, view):
        # Разрешение для безопасных методов (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True

        # Для POST и DELETE разрешено только администраторам
        return (request.superuser.role == 'admin'
                or request.user.role == 'admin')

    def has_object_permission(self, request, view, obj):
        # Если нужно применять разрешения к конкретному объекту
        # Может быть использовано в случае с detail-действиями
        return self.has_permission(request, view)

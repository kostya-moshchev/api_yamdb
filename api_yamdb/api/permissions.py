from rest_framework import permissions


<<<<<<< HEAD
class AuthorOrReadOnly(permissions.BasePermission):
=======

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Пользователь может изменять и удалять свои данные,
    администраторы, модераторы и суперпользователи
    могут редактировать любые данные.
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True

        return request.user.is_authenticated
>>>>>>> 5873e190b3efcdfc8292b9866d5821399f7bc419

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
<<<<<<< HEAD
        return obj.author == request.user


class ReadOnly(permissions.BasePermission):
    def has_object_permission(sel, request, view, obj):
        return request.method in permissions.SAFE_METHODS
=======

        return (
            request.user == obj.author
            or request.user.is_moderator
            or request.user.is_admin
        )

class IsAdminUserOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return super().has_permission(request, view)
>>>>>>> 5873e190b3efcdfc8292b9866d5821399f7bc419

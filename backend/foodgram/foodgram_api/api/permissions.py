from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
            or request.method in SAFE_METHODS
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (request.user.is_staff or request.user.is_superuser)
            or request.method in SAFE_METHODS
        )


class IsAuthorOrAdminOrReadOnly(BasePermission):

    def has_object_permission(self, request, view, obj):
        return (
            request.user.is_authenticated
            and (
                request.user.is_staff
                or request.user.is_superuser
                or request.user == obj.author)
            or request.method in SAFE_METHODS
        )

from functools import wraps

from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from rest_framework.permissions import BasePermission, SAFE_METHODS

EDITOR_GROUP_NAME = "Editor"


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name=EDITOR_GROUP_NAME).exists()


def is_owner(user):
    return user.is_authenticated and user.is_superuser


def can_edit(user):
    """Editors may update existing entries; the owner may do everything."""
    return is_owner(user) or is_editor(user)


def role_required(predicate):
    """Send anonymous visitors to login, but 403 signed-in users lacking the role."""
    def decorator(view_func):
        @wraps(view_func)
        @login_required(login_url="/login/")
        def _wrapped(request, *args, **kwargs):
            if not predicate(request.user):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)

        return _wrapped

    return decorator


class IsPortfolioOwnerOrReadOnly(BasePermission):
    message = "Only the portfolio owner can change projects."

    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or is_owner(request.user)


class IsPortfolioOwnerOrEditorOrReadOnly(BasePermission):
    def has_permission(self, request, view):
        return (
            request.method in SAFE_METHODS
            or is_owner(request.user)
            or (request.method in ("PUT", "PATCH") and is_editor(request.user))
        )

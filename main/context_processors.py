from main import permissions


def user_roles(request):
    """Expose the Tugas 4 access tiers to every template."""
    user = request.user
    return {
        "is_owner": permissions.is_owner(user),
        "is_editor": permissions.is_editor(user),
        "can_edit": permissions.can_edit(user),
    }

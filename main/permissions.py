EDITOR_GROUP_NAME = "Editor"


def is_editor(user):
    return user.is_authenticated and user.groups.filter(name=EDITOR_GROUP_NAME).exists()


def is_owner(user):
    return user.is_authenticated and user.is_superuser


def can_edit(user):
    """Editors may update existing entries; the owner may do everything."""
    return is_owner(user) or is_editor(user)

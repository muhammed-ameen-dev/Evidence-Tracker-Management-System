from django.contrib.auth.decorators import user_passes_test


def is_admin(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='Admin').exists()
    )


def is_investigator(user):
    return user.is_authenticated and (
        user.is_superuser or user.groups.filter(name='Investigator').exists()
    )


def has_system_access(user):
    # Allow both Admin and Investigator roles to access protected pages.
    return is_admin(user) or is_investigator(user)


def admin_required(view_func):
    # Restrict a view to users in the Admin group.
    return user_passes_test(is_admin)(view_func)


def investigator_required(view_func):
    # Restrict a view to users in the Investigator group.
    return user_passes_test(is_investigator)(view_func)


def role_required(view_func):
    # Restrict a view to users in Admin or Investigator groups.
    return user_passes_test(has_system_access)(view_func)


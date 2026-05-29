from audit.models import AuditLog


def create_audit_log(user, action):
    """Create an audit log entry for tracked actions."""
    if user and user.is_authenticated:
        AuditLog.objects.create(user=user, action=action)

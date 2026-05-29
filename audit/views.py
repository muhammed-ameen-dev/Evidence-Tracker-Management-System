from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from audit.utils import create_audit_log
from users.decorators import role_required
from .models import AuditLog


@login_required
@role_required
def log_list(request):
    create_audit_log(request.user, 'Log view')
    logs = AuditLog.objects.select_related('user').order_by('-timestamp')
    return render(request, 'logs.html', {'logs': logs})

import json
import time
from pathlib import Path
from django.contrib.auth.views import LoginView
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.conf import settings
from audit.models import AuditLog
from audit.utils import create_audit_log
from cases.models import Case
from evidence.models import Evidence
from .forms import SignUpForm
from .decorators import is_admin


def index(request):
    return render(request, 'index.html')


class UserLoginView(LoginView):
    template_name = 'registration/login.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        create_audit_log(self.request.user, 'User login')
        return response

    def form_invalid(self, form):
        return super().form_invalid(form)


def signup(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            # New signup users are added as Investigator by default.
            investigator_group, _ = Group.objects.get_or_create(name='Investigator')
            user.groups.add(investigator_group)
            create_audit_log(user, 'User signup')
            messages.success(request, 'Account created successfully. Please login.')
            return redirect('login')
    else:
        form = SignUpForm()

    return render(request, 'registration/signup.html', {'form': form})


@login_required
def dashboard(request):
    create_audit_log(request.user, 'Dashboard view')
    logs = AuditLog.objects.order_by('-timestamp')[:5]
    context = {
        'total_cases': Case.objects.count(),
        'active_cases': Case.objects.filter(status='ACTIVE').count(),
        'closed_cases': Case.objects.filter(status='CLOSED').count(),
        'total_evidence': Evidence.objects.count(),
        'logs': logs,
        'is_admin': is_admin(request.user),
    }
    return render(request, 'dashboard.html', context)


@login_required
def user_list(request):
    if not is_admin(request.user):
        messages.error(request, "Permission denied. Admin role required.")
        return redirect('dashboard')
    
    users = User.objects.all().order_by('username')
    # Pre-process roles for easier template management
    for u in users:
        u.is_admin_role = u.is_superuser or u.groups.filter(name='Admin').exists()
    
    return render(request, 'user_management.html', {
        'users': users,
        'is_admin': True # We already checked this above
    })


@login_required
def delete_user(request, pk):
    if not is_admin(request.user):
        messages.error(request, "Permission denied. Admin role required.")
        return redirect('dashboard')
    
    if request.method != 'POST':
        messages.error(request, "Invalid request method for critical action.")
        return redirect('user_list')
    
    user_to_delete = get_object_or_404(User, pk=pk)
    
    # Prevent deleting yourself
    if user_to_delete == request.user:
        messages.error(request, "You cannot delete your own account.")
        return redirect('user_list')
    
    # Prevent deleting superusers if you are not a superuser yourself
    if user_to_delete.is_superuser and not request.user.is_superuser:
        messages.error(request, "Only Superusers can delete other Superusers.")
        return redirect('user_list')

    username = user_to_delete.username
    user_to_delete.delete()
    create_audit_log(request.user, f"Deleted user account: {username}")
    messages.success(request, f"Investigator account '{username}' has been permanently deleted.")
    return redirect('user_list')


@login_required
def toggle_user_role(request, pk):
    if not is_admin(request.user):
        messages.error(request, "Permission denied. Admin role required.")
        return redirect('dashboard')
    
    target_user = get_object_or_404(User, pk=pk)
    
    # Prevent demoting yourself
    if target_user == request.user:
        messages.error(request, "You cannot change your own role.")
        return redirect('user_list')

    admin_group, _ = Group.objects.get_or_create(name='Admin')
    investigator_group, _ = Group.objects.get_or_create(name='Investigator')

    if target_user.groups.filter(name='Admin').exists():
        target_user.groups.remove(admin_group)
        target_user.groups.add(investigator_group)
        action = "demoted to Investigator"
    else:
        target_user.groups.add(admin_group)
        target_user.groups.remove(investigator_group)
        action = "promoted to Admin"
    
    create_audit_log(request.user, f"Changed role for {target_user.username}: {action}")
    messages.success(request, f"User {target_user.username} has been {action}.")
    return redirect('user_list')

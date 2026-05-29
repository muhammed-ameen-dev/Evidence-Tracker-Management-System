import re
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from audit.utils import create_audit_log
from users.decorators import admin_required, is_admin, role_required
from .forms import CaseForm
from .models import Case


@login_required
@role_required
def case_list(request):
    cases = Case.objects.annotate(evidence_count=Count('evidence_items')).select_related('created_by').order_by('-created_at')
    return render(
        request,
        'cases.html',
        {
            'cases': cases,
            'is_admin': is_admin(request.user),
            'is_superuser': request.user.is_superuser,
        },
    )


@login_required
@role_required
def create_case(request):
    if request.method == 'POST':
        form = CaseForm(request.POST)
        if form.is_valid():
            case = form.save(commit=False)
            
            # Logic for robust Case ID generation (CASE-001, CASE-002, etc.)
            # This avoids lexicographical sorting bugs in SQLite
            last_case = Case.objects.order_by('-id').first()
            if last_case:
                # Extract numeric part from the last case_id
                match = re.search(r'CASE-(\d+)', last_case.case_id)
                next_num = int(match.group(1)) + 1 if match else Case.objects.count() + 1
            else:
                next_num = 1
                
            case.case_id = f"CASE-{next_num:03d}"
            case.created_by = request.user
            case.save()
            
            create_audit_log(request.user, f"Created new case: {case.case_id}")
            return redirect('cases')
    else:
        form = CaseForm()

    return render(request, 'create_case.html', {'form': form})


@login_required
def delete_case(request, pk):
    # Restricted to Admin role (Superusers + Admin group).
    if not is_admin(request.user):
        messages.error(request, "Permission denied. Admin role required.")
        return redirect('dashboard')
    
    if request.method != 'POST':
        messages.error(request, "Invalid request method for critical action.")
        return redirect('cases')
    
    case = get_object_or_404(Case, pk=pk)
    
    # Prevent deleting closed cases to preserve forensic record
    if case.status == 'CLOSED':
        messages.error(request, "Cannot delete a CLOSED case. Re-open it first.")
        return redirect('cases')

    case_id = case.case_id
    case.delete()
    create_audit_log(request.user, f"Deleted case: {case_id}")
    messages.success(request, f"Forensic Case {case_id} has been permanently deleted.")
    return redirect('cases')


@login_required
def toggle_case_status(request, pk):
    if not is_admin(request.user):
        messages.error(request, "Permission denied. Admin role required.")
        return redirect('dashboard')
    
    case = get_object_or_404(Case, pk=pk)
    if case.status == 'ACTIVE':
        case.status = 'CLOSED'
        action = "Closed case"
    else:
        case.status = 'ACTIVE'
        action = "Re-opened case"
    
    case.save()
    create_audit_log(request.user, f"{action}: {case.case_id}")
    messages.success(request, f"Case {case.case_id} is now {case.get_status_display()}.")
    return redirect('cases')

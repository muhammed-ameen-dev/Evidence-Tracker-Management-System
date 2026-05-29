import hashlib
import re
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from audit.utils import create_audit_log
from users.decorators import is_admin, role_required
from .forms import EvidenceForm
from .models import Evidence


def _calculate_file_sha256(file_field):
    """Calculate SHA-256 hash for a saved evidence file."""
    sha256_hash = hashlib.sha256()
    with file_field.open('rb') as file_obj:
        for chunk in file_obj.chunks():
            sha256_hash.update(chunk)
    return sha256_hash.hexdigest()


@login_required
@role_required
def evidence_list(request):
    case_filter = request.GET.get('case')
    evidence_items = Evidence.objects.select_related('case', 'uploaded_by').order_by('-uploaded_at')
    
    if case_filter:
        evidence_items = evidence_items.filter(case__case_id=case_filter)

    # Recalculate hash while viewing evidence to verify integrity.
    for item in evidence_items:
        try:
            current_hash = _calculate_file_sha256(item.file)
            item.integrity_status = (
                'File is valid' if current_hash == item.hash_value else 'File may be tampered'
            )
        except Exception:
            item.integrity_status = 'File may be tampered'

    form = EvidenceForm()
    create_audit_log(request.user, f'Evidence view {"(Filtered: " + case_filter + ")" if case_filter else ""}')
    return render(request, 'evidence.html', {
        'evidence_items': evidence_items, 
        'form': form,
        'is_admin': is_admin(request.user),
        'active_filter': case_filter
    })


@login_required
@role_required
def upload_evidence(request):
    if request.method == 'POST':
        form = EvidenceForm(request.POST, request.FILES)
        if form.is_valid():
            evidence = form.save(commit=False)
            
            # Prevent uploads to closed cases
            if evidence.case.status == 'CLOSED':
                messages.error(request, f"Case {evidence.case.case_id} is LOCKED (CLOSED). No new evidence can be uploaded.")
                return redirect('evidence')

            evidence.uploaded_by = request.user

            # Generate SHA-256 hash from uploaded file content.
            uploaded_file = request.FILES['file']
            sha256_hash = hashlib.sha256()
            for chunk in uploaded_file.chunks():
                sha256_hash.update(chunk)
            evidence.hash_value = sha256_hash.hexdigest()

            # Reset file pointer before saving the file to storage.
            uploaded_file.seek(0)
            evidence.save()
            create_audit_log(request.user, f'Evidence upload: {evidence.file_name}')
    return redirect('evidence')


@login_required
def delete_evidence(request, pk):
    # Restricted to Admin role (Superusers + Admin group).
    if not is_admin(request.user):
        messages.error(request, "Permission denied. Admin role required.")
        return redirect('dashboard')
    
    if request.method != 'POST':
        messages.error(request, "Invalid request method for critical action.")
        return redirect('evidence')
    
    evidence = get_object_or_404(Evidence, pk=pk)

    # Prevent deletion from closed cases
    if evidence.case.status == 'CLOSED':
        messages.error(request, f"Cannot delete evidence from a CLOSED case: {evidence.case.case_id}")
        return redirect('evidence')

    file_name = evidence.file_name
    case_id = evidence.case.case_id
    
    evidence.delete()
    create_audit_log(request.user, f"Deleted evidence: {file_name} from Case {case_id}")
    messages.success(request, f"Evidence {file_name} has been permanently deleted.")
    return redirect('evidence')

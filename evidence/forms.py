from django import forms
from .models import Evidence
from cases.models import Case


class EvidenceForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Only allow uploading to ACTIVE cases
        self.fields['case'].queryset = Case.objects.filter(status='ACTIVE')

    class Meta:
        model = Evidence
        fields = ['file', 'file_name', 'case']

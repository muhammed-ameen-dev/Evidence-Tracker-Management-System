from django.contrib import admin
from .models import Evidence


@admin.register(Evidence)
class EvidenceAdmin(admin.ModelAdmin):
    list_display = ('file_name', 'case', 'uploaded_by', 'uploaded_at')
    search_fields = ('file_name', 'hash_value')
    list_filter = ('uploaded_at', 'case')

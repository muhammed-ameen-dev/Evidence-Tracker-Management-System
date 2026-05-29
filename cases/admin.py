from django.contrib import admin
from .models import Case


@admin.register(Case)
class CaseAdmin(admin.ModelAdmin):
    list_display = ('case_id', 'title', 'created_by', 'created_at')
    search_fields = ('case_id', 'title')
    list_filter = ('created_at',)

from django.db import models
from django.contrib.auth.models import User


class Case(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('CLOSED', 'Closed'),
        ('ARCHIVED', 'Archived'),
    ]

    # Human-readable case identifier (e.g., CASE-001)
    case_id = models.CharField(max_length=50, unique=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cases')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.case_id} - {self.title} ({self.get_status_display()})"

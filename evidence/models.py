from django.db import models
from django.contrib.auth.models import User
from cases.models import Case


class Evidence(models.Model):
    file = models.FileField(upload_to='evidence_files/')
    file_name = models.CharField(max_length=255)
    case = models.ForeignKey(Case, on_delete=models.CASCADE, related_name='evidence_items')
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_evidence')
    # SHA-256 hash stored as 64 hex characters
    hash_value = models.CharField(max_length=64)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    @property
    def extension(self):
        import os
        return os.path.splitext(self.file.name)[1].lower()

    @property
    def is_image(self):
        return self.extension in ['.jpg', '.jpeg', '.png', '.gif', '.webp']

    def __str__(self):
        return self.file_name

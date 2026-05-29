from django.urls import path
from .views import evidence_list, upload_evidence, delete_evidence

urlpatterns = [
    path('', evidence_list, name='evidence'),
    path('upload/', upload_evidence, name='upload_evidence'),
    path('delete/<int:pk>/', delete_evidence, name='delete_evidence'),
]

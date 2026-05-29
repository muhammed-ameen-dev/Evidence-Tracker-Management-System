from django.urls import path
from .views import case_list, create_case, delete_case, toggle_case_status

urlpatterns = [
    path('', case_list, name='cases'),
    path('create/', create_case, name='create_case'),
    path('delete/<int:pk>/', delete_case, name='delete_case'),
    path('toggle-status/<int:pk>/', toggle_case_status, name='toggle_case_status'),
]

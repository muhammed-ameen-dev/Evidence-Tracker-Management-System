from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import UserLoginView, dashboard, delete_user, index, signup, toggle_user_role, user_list

urlpatterns = [
    path('', index, name='home'),
    path('dashboard/', dashboard, name='dashboard'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('signup/', signup, name='signup'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('users/', user_list, name='user_list'),
    path('users/delete/<int:pk>/', delete_user, name='delete_user'),
    path('users/toggle-role/<int:pk>/', toggle_user_role, name='toggle_user_role'),
]

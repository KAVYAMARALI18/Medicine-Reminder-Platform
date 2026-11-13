from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html', redirect_authenticated_user=True), name='login'),
    path('logout/', views.custom_logout, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('caregiver-access/', views.caregiver_access, name='caregiver_access'),
    path('caregiver-access/<int:caregiver_id>/edit/', views.edit_caregiver, name='edit_caregiver'),
    path('caregiver-access/<int:caregiver_id>/delete/', views.delete_caregiver, name='delete_caregiver'),
]

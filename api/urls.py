from django.urls import path
from . import views

urlpatterns = [
    path('check_reminders/', views.check_reminders, name='check_reminders'),
    path('register_device/', views.register_device, name='register_device'),
    path('notification_action/', views.notification_action, name='notification_action'),
]

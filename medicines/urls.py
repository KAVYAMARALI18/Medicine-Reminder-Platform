from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('medicines/', views.medicine_list, name='medicine_list'),
    path('medicines/history/', views.medicine_history, name='medicine_history'),
    path('medicines/scan/', views.medicine_qr_scanner, name='medicine_qr_scanner'),
    path('medicines/add/', views.medicine_create, name='medicine_create'),
    path('medicines/<int:pk>/', views.medicine_detail, name='medicine_detail'),
    path('medicines/<int:pk>/edit/', views.medicine_edit, name='medicine_edit'),
    path('medicines/<int:pk>/delete/', views.medicine_delete, name='medicine_delete'),
    path('medicines/<int:pk>/prescription/', views.prescription_download, name='prescription_download'),
    path('medicines/refills/', views.refill_tracking, name='refill_tracking'),
    path('medicines/<int:medicine_id>/refill/add/', views.add_refill, name='add_refill'),
    path('reminders/<int:reminder_id>/status/', views.update_reminder_status, name='update_reminder_status'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('reports/', views.reports_view, name='reports'),
    path('reports/export/<str:format_type>/', views.export_reports, name='export_reports'),
    path('settings/', views.settings_view, name='settings'),
]

from django.urls import path

from . import views

app_name = 'symptoms'

urlpatterns = [
    path('', views.symptom_checker, name='checker'),
    path('assessments/', views.assessment_history, name='assessment_history'),
    path('assessments/<int:pk>/', views.assessment_result, name='assessment_result'),
    path('assessments/<int:pk>/delete/', views.delete_assessment, name='delete_assessment'),
    path('health-information/', views.disease_list, name='disease_list'),
    path('health-information/<int:pk>/', views.disease_detail, name='disease_detail'),
    path('medicine-information/', views.medicine_information, name='medicine_information'),
]

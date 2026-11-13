from django.urls import path

from . import api_views

app_name = 'symptoms_api'

urlpatterns = [
    path('symptoms/', api_views.SymptomListAPI.as_view(), name='symptom-list'),
    path('assessments/', api_views.AssessmentListCreateAPI.as_view(), name='assessment-list'),
    path('assessments/<int:pk>/', api_views.AssessmentDetailAPI.as_view(), name='assessment-detail'),
    path('diseases/', api_views.DiseaseInformationAPI.as_view(), name='disease-list'),
    path('diseases/<int:pk>/', api_views.DiseaseInformationAPI.as_view(), name='disease-detail'),
    path('medicines/', api_views.MedicineInformationAPI.as_view(), name='medicine-information'),
]

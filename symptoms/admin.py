from django.contrib import admin

from .models import (
    AssessmentSymptom,
    DiseaseInformation,
    DiseaseSymptom,
    EmergencySymptom,
    Symptom,
    SymptomAssessment,
)


class DiseaseSymptomInline(admin.TabularInline):
    model = DiseaseSymptom
    extra = 0


class AssessmentSymptomInline(admin.TabularInline):
    model = AssessmentSymptom
    extra = 0
    readonly_fields = ('symptom',)
    can_delete = False


@admin.register(Symptom)
class SymptomAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'is_active')
    list_filter = ('category', 'is_active')
    search_fields = ('name', 'description')


@admin.register(DiseaseInformation)
class DiseaseInformationAdmin(admin.ModelAdmin):
    list_display = ('name', 'source_name', 'is_active')
    list_filter = ('is_active', 'source_name')
    search_fields = ('name', 'description')
    inlines = [DiseaseSymptomInline]


@admin.register(SymptomAssessment)
class SymptomAssessmentAdmin(admin.ModelAdmin):
    list_display = ('user', 'duration', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username',)
    readonly_fields = ('user', 'duration', 'additional_notes', 'assessment_summary', 'created_at')
    inlines = [AssessmentSymptomInline]


@admin.register(EmergencySymptom)
class EmergencySymptomAdmin(admin.ModelAdmin):
    list_display = ('symptom', 'source_name', 'is_active')
    list_filter = ('is_active', 'source_name')
    search_fields = ('symptom__name',)

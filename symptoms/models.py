from django.conf import settings
from django.db import models


class Symptom(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.CharField(max_length=255, blank=True)
    category = models.CharField(max_length=50)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return self.name


class DiseaseInformation(models.Model):
    name = models.CharField(max_length=150, unique=True)
    description = models.TextField()
    general_information = models.TextField()
    medical_care_guidance = models.TextField()
    symptoms = models.ManyToManyField(
        Symptom,
        through='DiseaseSymptom',
        related_name='disease_information',
    )
    source_name = models.CharField(max_length=150)
    source_url = models.URLField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class DiseaseSymptom(models.Model):
    disease = models.ForeignKey(
        DiseaseInformation,
        on_delete=models.CASCADE,
        related_name='disease_symptoms',
    )
    symptom = models.ForeignKey(
        Symptom,
        on_delete=models.CASCADE,
        related_name='disease_symptoms',
    )
    association_source = models.URLField()

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['disease', 'symptom'],
                name='unique_disease_symptom',
            ),
        ]

    def __str__(self):
        return f'{self.symptom} associated with {self.disease}'


class SymptomAssessment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='symptom_assessments',
    )
    symptoms = models.ManyToManyField(
        Symptom,
        through='AssessmentSymptom',
        related_name='assessments',
    )
    duration = models.CharField(max_length=100)
    additional_notes = models.TextField(blank=True)
    assessment_summary = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Symptom assessment for {self.user} on {self.created_at:%Y-%m-%d}'


class AssessmentSymptom(models.Model):
    assessment = models.ForeignKey(
        SymptomAssessment,
        on_delete=models.CASCADE,
        related_name='assessment_symptoms',
    )
    symptom = models.ForeignKey(
        Symptom,
        on_delete=models.PROTECT,
        related_name='assessment_symptoms',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['assessment', 'symptom'],
                name='unique_assessment_symptom',
            ),
        ]


class EmergencySymptom(models.Model):
    symptom = models.OneToOneField(
        Symptom,
        on_delete=models.CASCADE,
        related_name='emergency_rule',
    )
    warning = models.TextField()
    source_name = models.CharField(max_length=150)
    source_url = models.URLField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['symptom__name']

    def __str__(self):
        return f'Emergency warning for {self.symptom}'

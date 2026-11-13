from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone


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


class DailyWellnessCheckin(models.Model):
    MOOD_CHOICES = [
        ('Very low', 'Very low'),
        ('Low', 'Low'),
        ('Okay', 'Okay'),
        ('Good', 'Good'),
        ('Excellent', 'Excellent'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='wellness_checkins',
    )
    date = models.DateField(default=timezone.now)
    sleep_hours = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        blank=True,
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(24)],
    )
    hydration_liters = models.DecimalField(
        max_digits=3,
        decimal_places=1,
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    exercise_minutes = models.PositiveIntegerField(default=0)
    mood = models.CharField(max_length=20, choices=MOOD_CHOICES, default='Okay')
    energy_level = models.PositiveSmallIntegerField(
        default=3,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date']
        constraints = [
            models.UniqueConstraint(fields=['user', 'date'], name='unique_user_daily_wellness_checkin'),
        ]

    def __str__(self):
        return f'{self.user} wellness check-in for {self.date}'


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

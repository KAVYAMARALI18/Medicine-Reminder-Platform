from django.contrib.auth.models import AbstractUser
from django.db import models

from .validators import SpaceAllowedUsernameValidator


class User(AbstractUser):
    username = models.CharField(
        max_length=150,
        unique=True,
        help_text="Required. 150 characters or fewer. Letters, digits, spaces and @/./+/-/_ only.",
        validators=[SpaceAllowedUsernameValidator()],
        error_messages={
            "unique": "A user with that username already exists.",
        },
    )

    # Additional fields
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

    # Settings preferences
    dark_mode = models.BooleanField(default=False)
    language = models.CharField(max_length=10, default='en')
    time_format = models.CharField(max_length=10, default='12h', choices=[('12h', '12 Hour'), ('24h', '24 Hour')])
    sound_enabled = models.BooleanField(default=True)
    desktop_notifications_enabled = models.BooleanField(default=True)
    email_notifications_enabled = models.BooleanField(default=True)
    sms_notifications_enabled = models.BooleanField(default=False)
    sms_phone_number = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return self.username

class EmergencyContact(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='emergency_contact')
    blood_group = models.CharField(max_length=5, blank=True, null=True)
    primary_contact_name = models.CharField(max_length=100, blank=True, null=True)
    primary_contact_number = models.CharField(max_length=20, blank=True, null=True)
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    doctor_number = models.CharField(max_length=20, blank=True, null=True)
    allergies = models.TextField(blank=True, null=True)
    medical_conditions = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Emergency Info for {self.user.username}"

class FamilyAccess(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caregivers')
    caregiver_name = models.CharField(max_length=100)
    caregiver_phone = models.CharField(max_length=20, blank=True, null=True)
    caregiver_email = models.EmailField(blank=True, null=True)
    can_view_dashboard = models.BooleanField(default=True)
    can_receive_reminders = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.caregiver_name} for {self.user.username}"

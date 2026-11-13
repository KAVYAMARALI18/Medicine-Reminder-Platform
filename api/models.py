from django.db import models
from django.conf import settings

class Notification(models.Model):
    TYPE_CHOICES = [
        ('Reminder', 'Reminder'),
        ('Missed', 'Missed Medicine Alert'),
        ('Stock', 'Low Stock Warning'),
        ('Expiry', 'Prescription Expiry'),
        ('System', 'System Alert')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='System')
    title = models.CharField(max_length=100)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Optional link to relevant item (e.g., Medicine ID)
    related_id = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return f"{self.notification_type} for {self.user.username}"

class FCMDevice(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='fcm_devices')
    registration_id = models.CharField(max_length=255, unique=True)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Device for {self.user.username}"

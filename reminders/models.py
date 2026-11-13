from django.db import models
from django.conf import settings
from medicines.models import Medicine
from datetime import date

class Reminder(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='reminders')
    time = models.TimeField()
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.medicine.name} at {self.time}"

class MedicineLog(models.Model):
    STATUS_CHOICES = [
        ('Taken', 'Taken'),
        ('Skipped', 'Skipped'),
        ('Missed', 'Missed'),
        ('Pending', 'Pending')
    ]

    reminder = models.ForeignKey(Reminder, on_delete=models.CASCADE, related_name='logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medicine_logs')
    date = models.DateField(default=date.today)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    
    # Notification delivery tracking
    DELIVERY_CHOICES = [
        ('Pending', 'Pending'),
        ('Sent', 'Sent'),
        ('Failed', 'Failed'),
    ]
    delivery_status = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='Pending')
    snooze_time = models.DateTimeField(blank=True, null=True, help_text="Time until which this reminder is snoozed")
    
    # Email notification tracking
    email_delivery_status = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='Pending')
    email_sent_time = models.DateTimeField(blank=True, null=True)

    # SMS notification tracking
    sms_delivery_status = models.CharField(max_length=20, choices=DELIVERY_CHOICES, default='Pending')
    sms_sent_time = models.DateTimeField(blank=True, null=True)

    taken_at = models.DateTimeField(blank=True, null=True)
    notes = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('reminder', 'date')

    def __str__(self):
        return f"{self.reminder.medicine.name} - {self.date} - {self.status}"

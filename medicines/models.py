from django.db import models
from django.conf import settings
from .storage import PrivatePrescriptionStorage
from .validators import validate_prescription_upload

class Medicine(models.Model):
    TYPE_CHOICES = [
        ('Tablet', 'Tablet'),
        ('Syrup', 'Syrup'),
        ('Capsule', 'Capsule'),
        ('Injection', 'Injection'),
        ('Drops', 'Drops'),
        ('Other', 'Other')
    ]

    FREQUENCY_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
        ('Custom', 'Custom'),
        ('As Needed', 'As Needed')
    ]

    FOOD_CHOICES = [
        ('Before Food', 'Before Food'),
        ('After Food', 'After Food'),
        ('Anytime', 'Anytime')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medicines')
    name = models.CharField(max_length=100)
    medicine_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='Tablet')
    dosage = models.CharField(max_length=50) # e.g., 500mg, 10ml
    quantity = models.PositiveIntegerField(default=1, help_text="Total quantity remaining")
    before_after_food = models.CharField(max_length=20, choices=FOOD_CHOICES, default='After Food')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='Daily')

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    notes = models.TextField(blank=True, null=True)
    doctor_name = models.CharField(max_length=100, blank=True, null=True)
    prescription_upload = models.FileField(
        upload_to='prescriptions/',
        storage=PrivatePrescriptionStorage(),
        validators=[validate_prescription_upload],
        blank=True,
        null=True,
    )

    # Stock Management
    low_stock_threshold = models.PositiveIntegerField(default=5)
    refill_reminder_days = models.PositiveIntegerField(default=7, help_text="Days before refill alert")
    last_refill_date = models.DateField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def is_low_stock(self):
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        return f"{self.name} - {self.user.username}"


class RefillRecord(models.Model):
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='refills')
    refill_date = models.DateField()
    quantity_added = models.PositiveIntegerField(default=1)
    quantity_after_refill = models.PositiveIntegerField(default=1)
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    pharmacy_name = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-refill_date', '-created_at']

    def __str__(self):
        return f"{self.medicine.name} refill on {self.refill_date}"

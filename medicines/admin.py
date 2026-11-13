from django.contrib import admin
from django.db import models

from .forms import PrivatePrescriptionInput
from .models import Medicine


@admin.register(Medicine)
class MedicineAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.FileField: {'widget': PrivatePrescriptionInput},
    }

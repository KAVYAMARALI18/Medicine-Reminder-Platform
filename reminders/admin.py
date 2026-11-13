from django.contrib import admin
from .models import Reminder, MedicineLog

admin.site.register(Reminder)
admin.site.register(MedicineLog)

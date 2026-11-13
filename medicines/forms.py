from django import forms
from django.forms import inlineformset_factory
from pathlib import PurePosixPath

from .models import Medicine
from reminders.models import Reminder


class PrivatePrescriptionInput(forms.ClearableFileInput):
    template_name = 'widgets/private_file_input.html'

    def is_initial(self, value):
        return bool(value and getattr(value, 'name', None))

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if context['widget']['is_initial']:
            context['widget']['initial_name'] = PurePosixPath(value.name).name
        return context


class MedicineForm(forms.ModelForm):
    class Meta:
        model = Medicine
        exclude = ['user', 'created_at', 'updated_at']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
            'prescription_upload': PrivatePrescriptionInput(attrs={
                'class': 'form-control',
                'accept': '.pdf,.jpg,.jpeg,.png,.webp',
            }),
        }

class ReminderForm(forms.ModelForm):
    class Meta:
        model = Reminder
        fields = ['time', 'is_active']
        widgets = {
            'time': forms.TimeInput(attrs={'type': 'time'})
        }

ReminderFormSet = inlineformset_factory(
    Medicine, Reminder, form=ReminderForm,
    extra=1, can_delete=True
)

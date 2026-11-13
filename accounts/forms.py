from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

from .models import FamilyAccess

User = get_user_model()

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email']

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def validate_password_for_user(self, user, password_field_name='password1'):
        return super().validate_password_for_user(
            user,
            password_field_name=password_field_name,
        )


class FamilyAccessForm(forms.ModelForm):
    class Meta:
        model = FamilyAccess
        fields = [
            'caregiver_name',
            'caregiver_phone',
            'caregiver_email',
            'can_view_dashboard',
            'can_receive_reminders',
            'is_active',
        ]
        widgets = {
            'caregiver_name': forms.TextInput(attrs={'class': 'form-control'}),
            'caregiver_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'caregiver_email': forms.EmailInput(attrs={'class': 'form-control'}),
            'can_view_dashboard': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_receive_reminders': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

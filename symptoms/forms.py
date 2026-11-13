from django import forms

from .models import Symptom


class SymptomAssessmentForm(forms.Form):
    symptoms = forms.ModelMultipleChoiceField(
        queryset=Symptom.objects.none(),
        required=True,
        error_messages={'required': 'Select at least one symptom.'},
    )
    duration = forms.CharField(max_length=100)
    additional_notes = forms.CharField(
        max_length=1000,
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['symptoms'].queryset = Symptom.objects.filter(is_active=True)

    def clean_duration(self):
        duration = self.cleaned_data['duration'].strip()
        if not duration:
            raise forms.ValidationError('Enter how long you have had these symptoms.')
        return duration

    def clean_symptoms(self):
        symptoms = self.cleaned_data['symptoms']
        if len(symptoms) > 30:
            raise forms.ValidationError('Select no more than 30 symptoms.')
        return symptoms

    def clean_additional_notes(self):
        return self.cleaned_data.get('additional_notes', '').strip()

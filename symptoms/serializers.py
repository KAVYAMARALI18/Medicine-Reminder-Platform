from rest_framework import serializers

from .models import DiseaseInformation, Symptom, SymptomAssessment


class SymptomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Symptom
        fields = ['id', 'name', 'description', 'category']


class DiseaseInformationSerializer(serializers.ModelSerializer):
    symptoms = SymptomSerializer(many=True, read_only=True)

    class Meta:
        model = DiseaseInformation
        fields = [
            'id',
            'name',
            'description',
            'general_information',
            'medical_care_guidance',
            'source_name',
            'source_url',
            'symptoms',
        ]


class AssessmentCreateSerializer(serializers.Serializer):
    symptom_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        allow_empty=False,
        max_length=30,
    )
    duration = serializers.CharField(max_length=100, trim_whitespace=True)
    additional_notes = serializers.CharField(
        max_length=1000,
        allow_blank=True,
        required=False,
        trim_whitespace=True,
    )

    def validate_symptom_ids(self, symptom_ids):
        if len(set(symptom_ids)) != len(symptom_ids):
            raise serializers.ValidationError('Select each symptom only once.')
        if Symptom.objects.filter(pk__in=symptom_ids, is_active=True).count() != len(symptom_ids):
            raise serializers.ValidationError('One or more selected symptoms are unavailable.')
        return symptom_ids

    def validate_duration(self, duration):
        if not duration:
            raise serializers.ValidationError('Enter how long you have had these symptoms.')
        return duration


class SymptomAssessmentSerializer(serializers.ModelSerializer):
    symptoms = SymptomSerializer(many=True, read_only=True)

    class Meta:
        model = SymptomAssessment
        fields = [
            'id',
            'symptoms',
            'duration',
            'additional_notes',
            'assessment_summary',
            'created_at',
        ]

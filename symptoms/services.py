from collections import defaultdict

from .models import DiseaseInformation, DiseaseSymptom, EmergencySymptom


EMERGENCY_GUIDANCE = (
    'These selected warning signs may need immediate attention. Contact your local '
    'emergency services or seek immediate medical care now. Do not wait for an online '
    'assessment. This warning list is not exhaustive.'
)


def analyze_symptoms(symptoms):
    """Match only explicitly sourced associations; urgent rules bypass routine matching."""
    symptom_list = list(symptoms)
    urgent_rules = list(
        EmergencySymptom.objects.filter(
            symptom__in=symptom_list,
            is_active=True,
        ).select_related('symptom')
    )
    if urgent_rules:
        return {
            'is_emergency': True,
            'emergency_guidance': EMERGENCY_GUIDANCE,
            'emergency_matches': [
                {
                    'symptom': rule.symptom.name,
                    'warning': rule.warning,
                    'source_name': rule.source_name,
                    'source_url': rule.source_url,
                }
                for rule in urgent_rules
            ],
            'conditions': [],
        }

    grouped = defaultdict(lambda: {'disease': None, 'matched_symptoms': []})
    for association in DiseaseSymptom.objects.filter(
        symptom__in=symptom_list,
        disease__is_active=True,
    ).select_related('disease', 'symptom'):
        match = grouped[association.disease_id]
        match['disease'] = association.disease
        match['matched_symptoms'].append(association.symptom.name)

    conditions = sorted(
        grouped.values(),
        key=lambda item: (-len(item['matched_symptoms']), item['disease'].name),
    )
    return {
        'is_emergency': False,
        'emergency_guidance': '',
        'emergency_matches': [],
        'conditions': [
            {
                'id': match['disease'].pk,
                'name': match['disease'].name,
                'matched_symptoms': match['matched_symptoms'],
            }
            for match in conditions
        ],
    }


def get_assessment_conditions(assessment):
    summary = assessment.assessment_summary or {}
    condition_ids = [item['id'] for item in summary.get('conditions', [])]
    disease_map = {
        disease.pk: disease
        for disease in DiseaseInformation.objects.filter(pk__in=condition_ids, is_active=True)
    }
    return [
        {
            'disease': disease_map[item['id']],
            'matched_symptoms': item['matched_symptoms'],
        }
        for item in summary.get('conditions', [])
        if item.get('id') in disease_map
    ]

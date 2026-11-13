from django.db import migrations

CDC_ASTHMA_URL = 'https://www.cdc.gov/asthma/default.htm'
CDC_MIGRAINE_URL = 'https://www.cdc.gov/migraine/'
CDC_COVID_URL = 'https://www.cdc.gov/coronavirus/2019-ncov/symptoms-testing/symptoms.html'

NEW_SYMPTOMS = [
    ('Wheezing', 'Respiratory'),
    ('Shortness of breath', 'Respiratory'),
    ('Chest tightness', 'Urgent warning signs'),
    ('Sensitivity to light', 'Neurological'),
    ('Loss of taste or smell', 'Neurological'),
]

CONDITIONS = [
    {
        'name': 'Asthma',
        'description': 'A chronic lung condition that can cause airway inflammation and breathing problems.',
        'general_information': (
            'Asthma can cause wheezing, chest tightness, and shortness of breath. These episodes may be triggered by allergens, smoke, exercise, respiratory infections, or air pollutants. Not everyone experiences the same pattern or severity.'
        ),
        'medical_care_guidance': (
            'Seek prompt medical care if breathing is difficult, symptoms are severe, or rescue inhaler treatment is not helping. A healthcare professional can help review triggers, long-term treatment, and emergency plans.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_ASTHMA_URL,
        'symptoms': ['Cough', 'Wheezing', 'Shortness of breath', 'Chest tightness'],
    },
    {
        'name': 'Migraine',
        'description': 'A neurological condition often associated with recurring headaches and sensitivity to light or sound.',
        'general_information': (
            'A migraine may involve a moderate to severe headache, nausea, dizziness, and sensitivity to light. Some people also notice visual changes, trouble concentrating, or fatigue before or during the episode.'
        ),
        'medical_care_guidance': (
            'Contact a healthcare professional if headaches are frequent, severe, or new for you. Get urgent evaluation for sudden severe headache, weakness, confusion, or neurological changes.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_MIGRAINE_URL,
        'symptoms': ['Headache', 'Nausea', 'Dizziness', 'Sensitivity to light'],
    },
    {
        'name': 'COVID-19',
        'description': 'An illness caused by the SARS-CoV-2 virus that can range from mild symptoms to severe respiratory illness.',
        'general_information': (
            'CDC information lists fever, cough, fatigue, body aches, and loss of taste or smell among common symptoms of COVID-19. Some people also have sore throat, congestion, headache, nausea, or shortness of breath.'
        ),
        'medical_care_guidance': (
            'If you have fever, breathing trouble, or rapidly worsening symptoms, seek medical advice and follow local public health guidance. Seek emergency help for severe shortness of breath, chest pain, or confusion.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_COVID_URL,
        'symptoms': ['Fever', 'Cough', 'Fatigue', 'Loss of taste or smell', 'Shortness of breath'],
    },
]


def seed_more_health_information(apps, schema_editor):
    Symptom = apps.get_model('symptoms', 'Symptom')
    DiseaseInformation = apps.get_model('symptoms', 'DiseaseInformation')
    DiseaseSymptom = apps.get_model('symptoms', 'DiseaseSymptom')

    symptoms_by_name = {}
    for name, category in NEW_SYMPTOMS:
        symptom, _ = Symptom.objects.get_or_create(
            name=name,
            defaults={'category': category, 'description': '', 'is_active': True},
        )
        symptoms_by_name[name] = symptom

    for condition in CONDITIONS:
        disease, _ = DiseaseInformation.objects.update_or_create(
            name=condition['name'],
            defaults={
                'description': condition['description'],
                'general_information': condition['general_information'],
                'medical_care_guidance': condition['medical_care_guidance'],
                'source_name': condition['source_name'],
                'source_url': condition['source_url'],
                'is_active': True,
            },
        )
        for symptom_name in condition['symptoms']:
            symptom = Symptom.objects.filter(name=symptom_name).first()
            if symptom:
                DiseaseSymptom.objects.get_or_create(
                    disease=disease,
                    symptom=symptom,
                    defaults={'association_source': condition['source_url']},
                )


class Migration(migrations.Migration):

    dependencies = [
        ('symptoms', '0002_seed_reviewed_information'),
    ]

    operations = [
        migrations.RunPython(seed_more_health_information, migrations.RunPython.noop),
    ]

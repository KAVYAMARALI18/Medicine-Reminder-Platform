from django.db import migrations


CDC_COLD_URL = 'https://www.cdc.gov/common-cold/about/index.html'
CDC_FLU_URL = 'https://www.cdc.gov/flu/signs-symptoms/index.html'
CDC_NOROVIRUS_URL = 'https://www.cdc.gov/norovirus/about/index.html'
CDC_STROKE_URL = 'https://www.cdc.gov/stroke/signs-symptoms/index.html'
MEDLINEPLUS_ANAPHYLAXIS_URL = 'https://medlineplus.gov/anaphylaxis.html'
MEDLINEPLUS_FAINTING_URL = 'https://medlineplus.gov/fainting.html'


SYMPTOMS = [
    ('Fever', 'General'),
    ('Headache', 'General'),
    ('Cough', 'Respiratory'),
    ('Fatigue', 'General'),
    ('Sore throat', 'Respiratory'),
    ('Sneezing', 'Respiratory'),
    ('Runny or stuffy nose', 'Respiratory'),
    ('Nausea', 'Digestive'),
    ('Vomiting', 'Digestive'),
    ('Dizziness', 'Neurological'),
    ('Stomach pain', 'Digestive'),
    ('Body aches', 'General'),
    ('Chest pain or pressure', 'Urgent warning signs'),
    ('Difficulty breathing', 'Urgent warning signs'),
    ('Sudden weakness', 'Urgent warning signs'),
    ('Severe allergic reaction', 'Urgent warning signs'),
    ('Loss of consciousness', 'Urgent warning signs'),
]


CONDITIONS = [
    {
        'name': 'Common cold',
        'description': 'A viral infection of the upper respiratory tract.',
        'general_information': (
            'The CDC lists runny or stuffy nose, cough, sneezing, sore throat, headache, '
            'mild body aches, and fever among possible cold symptoms. These symptoms can '
            'also occur with other illnesses.'
        ),
        'medical_care_guidance': (
            'Contact a healthcare professional if symptoms are severe, persistent, '
            'worsening, or concerning. Consult the CDC source for current guidance.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_COLD_URL,
        'symptoms': [
            'Runny or stuffy nose', 'Cough', 'Sneezing', 'Sore throat',
            'Headache', 'Body aches', 'Fever',
        ],
    },
    {
        'name': 'Influenza (flu)',
        'description': 'A contagious respiratory illness caused by influenza viruses.',
        'general_information': (
            'The CDC lists fever or chills, cough, sore throat, runny or stuffy nose, '
            'body aches, headache, and fatigue among flu symptoms. Some people, especially '
            'children, may also have vomiting or diarrhea. Not everyone with flu has a fever.'
        ),
        'medical_care_guidance': (
            'The CDC lists difficulty breathing, persistent chest or abdominal pain, '
            'persistent dizziness or confusion, and severe weakness among adult warning '
            'signs that need medical care right away. This list is not exhaustive.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_FLU_URL,
        'symptoms': [
            'Fever', 'Cough', 'Sore throat', 'Runny or stuffy nose',
            'Body aches', 'Headache', 'Fatigue', 'Vomiting',
        ],
    },
    {
        'name': 'Norovirus illness',
        'description': 'A contagious virus that causes acute gastroenteritis.',
        'general_information': (
            'The CDC lists diarrhea, vomiting, nausea, and stomach pain as the most common '
            'norovirus symptoms. Fever, headache, and body aches can also occur. The '
            'selected symptom overlap does not establish a cause.'
        ),
        'medical_care_guidance': (
            'The CDC notes that dehydration can be a concern, particularly for young '
            'children, older adults, and people with other illnesses. Seek medical care '
            'for severe dehydration or symptoms that are severe, persistent, or concerning.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_NOROVIRUS_URL,
        'symptoms': [
            'Nausea', 'Vomiting', 'Stomach pain', 'Fever', 'Headache', 'Body aches',
        ],
    },
]


EMERGENCY_RULES = [
    (
        'Chest pain or pressure',
        'Persistent chest pain or pressure is listed by CDC as an adult flu complication warning sign.',
        'U.S. Centers for Disease Control and Prevention (CDC)',
        CDC_FLU_URL,
    ),
    (
        'Difficulty breathing',
        'Difficulty breathing or shortness of breath is listed by CDC as an adult flu complication warning sign.',
        'U.S. Centers for Disease Control and Prevention (CDC)',
        CDC_FLU_URL,
    ),
    (
        'Sudden weakness',
        'Sudden weakness, especially in the face, arm, or leg, is a CDC stroke warning sign. Call local emergency services immediately.',
        'U.S. Centers for Disease Control and Prevention (CDC)',
        CDC_STROKE_URL,
    ),
    (
        'Severe allergic reaction',
        'MedlinePlus describes anaphylaxis as a potentially life-threatening serious allergic reaction and advises calling emergency services.',
        'MedlinePlus, U.S. National Library of Medicine',
        MEDLINEPLUS_ANAPHYLAXIS_URL,
    ),
    (
        'Loss of consciousness',
        'Loss of consciousness (fainting) can sometimes indicate a serious problem. Seek medical evaluation; contact emergency services if immediate danger is present.',
        'MedlinePlus, U.S. National Library of Medicine',
        MEDLINEPLUS_FAINTING_URL,
    ),
]


def seed_information(apps, schema_editor):
    Symptom = apps.get_model('symptoms', 'Symptom')
    DiseaseInformation = apps.get_model('symptoms', 'DiseaseInformation')
    DiseaseSymptom = apps.get_model('symptoms', 'DiseaseSymptom')
    EmergencySymptom = apps.get_model('symptoms', 'EmergencySymptom')

    symptoms_by_name = {}
    for name, category in SYMPTOMS:
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
            DiseaseSymptom.objects.get_or_create(
                disease=disease,
                symptom=symptoms_by_name[symptom_name],
                defaults={'association_source': condition['source_url']},
            )

    for name, warning, source_name, source_url in EMERGENCY_RULES:
        EmergencySymptom.objects.update_or_create(
            symptom=symptoms_by_name[name],
            defaults={
                'warning': warning,
                'source_name': source_name,
                'source_url': source_url,
                'is_active': True,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ('symptoms', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_information, migrations.RunPython.noop),
    ]

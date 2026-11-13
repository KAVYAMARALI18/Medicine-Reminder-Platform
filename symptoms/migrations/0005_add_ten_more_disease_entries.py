from django.db import migrations

CDC_PNEUMONIA_URL = 'https://www.cdc.gov/pneumonia/'
CDC_ECZEMA_URL = 'https://www.cdc.gov/healthyskin/eczema/'
CDC_DEHYDRATION_URL = 'https://www.cdc.gov/healthywater/drinking/nutrition/index.html'
CDC_INSOMNIA_URL = 'https://www.cdc.gov/niosh/topics/insomnia/'
CDC_ARTHRITIS_URL = 'https://www.cdc.gov/arthritis/about/index.html'
CDC_KIDNEY_STONES_URL = 'https://www.cdc.gov/health-topics/kidney-stones'
CDC_GERD_URL = 'https://www.cdc.gov/gerd/'
CDC_CONJUNCTIVITIS_URL = 'https://www.cdc.gov/conjunctivitis/about/index.html'
CDC_HEPATITIS_URL = 'https://www.cdc.gov/hepatitis/'
CDC_ANEMIA_URL = 'https://www.cdc.gov/ncbddd/anaemia/'

NEW_SYMPTOMS = [
    ('Shortness of breath', 'Respiratory'),
    ('Fever', 'General'),
    ('Chills', 'General'),
    ('Skin rash', 'Skin'),
    ('Dry skin', 'Skin'),
    ('Itching', 'Skin'),
    ('Thirst', 'General'),
    ('Dark urine', 'Urinary'),
    ('Trouble sleeping', 'General'),
    ('Joint pain', 'Musculoskeletal'),
    ('Swollen joints', 'Musculoskeletal'),
    ('Back pain', 'Musculoskeletal'),
    ('Burning pain in the chest', 'Digestive'),
    ('Acid reflux', 'Digestive'),
    ('Red eye', 'Eye'),
    ('Eye discharge', 'Eye'),
    ('Yellowing of the eyes', 'Digestive'),
    ('Fatigue', 'General'),
    ('Pale skin', 'General'),
    ('Dizziness', 'Neurological'),
]

CONDITIONS = [
    {
        'name': 'Pneumonia',
        'description': 'An infection that causes inflammation in the air sacs of one or both lungs.',
        'general_information': (
            'Pneumonia may cause fever, chills, cough, shortness of breath, and fatigue. Symptoms can vary from mild to severe, especially in older adults or people with other health conditions.'
        ),
        'medical_care_guidance': (
            'Seek medical care for trouble breathing, chest pain, high fever, or worsening symptoms. Severe pneumonia can be dangerous and may require urgent evaluation.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_PNEUMONIA_URL,
        'symptoms': ['Fever', 'Chills', 'Cough', 'Shortness of breath', 'Fatigue'],
    },
    {
        'name': 'Eczema',
        'description': 'A chronic skin condition that can cause dry, itchy, and inflamed skin.',
        'general_information': (
            'Eczema commonly causes dry skin, itching, redness, and rashes. The condition may flare with irritants, allergens, stress, or temperature changes.'
        ),
        'medical_care_guidance': (
            'A healthcare professional can help identify triggers and recommend skin care and treatment plans. Seek advice if the rash is severe, spreading, or accompanied by signs of infection.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_ECZEMA_URL,
        'symptoms': ['Dry skin', 'Itching', 'Skin rash'],
    },
    {
        'name': 'Dehydration',
        'description': 'A condition caused by not having enough fluids in the body for normal function.',
        'general_information': (
            'Dehydration may cause thirst, dry mouth, dark urine, dizziness, and fatigue. It can happen with vomiting, diarrhea, fever, heavy sweating, or not drinking enough fluids.'
        ),
        'medical_care_guidance': (
            'Replace fluids and seek medical advice if dehydration is severe, persistent, or associated with confusion, fainting, or inability to keep fluids down.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_DEHYDRATION_URL,
        'symptoms': ['Thirst', 'Dark urine', 'Dizziness', 'Fatigue'],
    },
    {
        'name': 'Insomnia',
        'description': 'A sleep disorder that makes it hard to fall asleep, stay asleep, or get enough restorative sleep.',
        'general_information': (
            'Insomnia can lead to trouble sleeping, daytime fatigue, irritability, and difficulty concentrating. Common causes include stress, poor sleep habits, pain, or another medical condition.'
        ),
        'medical_care_guidance': (
            'If sleep problems continue for weeks or interfere with daily functioning, speak with a healthcare professional. Severe sleep deprivation can affect mood, safety, and work performance.'
        ),
        'source_name': 'U.S. National Institute for Occupational Safety and Health (NIOSH)',
        'source_url': CDC_INSOMNIA_URL,
        'symptoms': ['Trouble sleeping', 'Fatigue', 'Dizziness'],
    },
    {
        'name': 'Arthritis',
        'description': 'A group of conditions that cause inflammation and pain in the joints.',
        'general_information': (
            'Arthritis can cause joint pain, stiffness, swelling, and reduced movement. Symptoms may come and go and can affect different joints depending on the type of arthritis.'
        ),
        'medical_care_guidance': (
            'Early evaluation can help reduce pain and protect joint function. Seek care if swelling, severe pain, or loss of movement is affecting daily activities.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_ARTHRITIS_URL,
        'symptoms': ['Joint pain', 'Swollen joints', 'Stiffness'],
    },
    {
        'name': 'Kidney stones',
        'description': 'Hard deposits that form in the kidneys and can cause severe pain as they move through the urinary tract.',
        'general_information': (
            'Kidney stones may cause severe back or side pain, nausea, blood in the urine, and painful urination. The severity of symptoms depends on the size and location of the stone.'
        ),
        'medical_care_guidance': (
            'Seek urgent care for severe pain, fever, vomiting, or blood in the urine. These symptoms can require evaluation to prevent complications.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_KIDNEY_STONES_URL,
        'symptoms': ['Back pain', 'Nausea', 'Painful urination'],
    },
    {
        'name': 'Gastroesophageal reflux disease (GERD)',
        'description': 'A chronic digestive condition in which stomach acid flows back into the esophagus.',
        'general_information': (
            'GERD may cause heartburn, acid reflux, chest discomfort, and sometimes nausea. Symptoms can be triggered by certain foods, late meals, or lying down after eating.'
        ),
        'medical_care_guidance': (
            'Speak with a healthcare professional if symptoms are frequent, severe, or accompanied by trouble swallowing, weight loss, or chest pain.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_GERD_URL,
        'symptoms': ['Burning pain in the chest', 'Acid reflux', 'Nausea'],
    },
    {
        'name': 'Conjunctivitis',
        'description': 'Inflammation of the outer membrane of the eye, often called pink eye.',
        'general_information': (
            'Conjunctivitis can cause redness, eye discharge, itching, and tearing. It may be caused by viruses, bacteria, or allergens and often spreads easily in shared environments.'
        ),
        'medical_care_guidance': (
            'Contact a healthcare professional if symptoms are severe, prolonged, or accompanied by pain or vision changes. Keep the eye washed and avoid sharing towels or makeup.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_CONJUNCTIVITIS_URL,
        'symptoms': ['Red eye', 'Eye discharge', 'Itching'],
    },
    {
        'name': 'Hepatitis',
        'description': 'Inflammation of the liver that can be caused by viruses or other conditions.',
        'general_information': (
            'Hepatitis can cause fatigue, jaundice, abdominal pain, nausea, and sometimes fever. Some people do not have noticeable symptoms in the early stages.'
        ),
        'medical_care_guidance': (
            'Seek medical evaluation for persistent fatigue, yellowing of the eyes, abdominal pain, or worsening symptoms. Testing and treatment can help reduce complications.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_HEPATITIS_URL,
        'symptoms': ['Fatigue', 'Yellowing of the eyes', 'Stomach pain', 'Nausea'],
    },
    {
        'name': 'Anemia',
        'description': 'A condition in which the body has too few healthy red blood cells to carry enough oxygen.',
        'general_information': (
            'Anemia can cause fatigue, pale skin, weakness, dizziness, and shortness of breath. It can result from low iron, blood loss, illness, or other underlying conditions.'
        ),
        'medical_care_guidance': (
            'See a healthcare professional for evaluation if you have persistent fatigue, paleness, dizziness, or unusual weakness. Treatment depends on the cause of the anemia.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_ANEMIA_URL,
        'symptoms': ['Fatigue', 'Pale skin', 'Dizziness', 'Shortness of breath'],
    },
]


def seed_ten_more_diseases(apps, schema_editor):
    Symptom = apps.get_model('symptoms', 'Symptom')
    DiseaseInformation = apps.get_model('symptoms', 'DiseaseInformation')
    DiseaseSymptom = apps.get_model('symptoms', 'DiseaseSymptom')

    for name, category in NEW_SYMPTOMS:
        Symptom.objects.get_or_create(
            name=name,
            defaults={'category': category, 'description': '', 'is_active': True},
        )

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
        ('symptoms', '0004_add_more_disease_entries'),
    ]

    operations = [
        migrations.RunPython(seed_ten_more_diseases, migrations.RunPython.noop),
    ]

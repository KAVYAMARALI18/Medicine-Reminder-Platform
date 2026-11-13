from django.db import migrations

CDC_DIABETES_URL = 'https://www.cdc.gov/diabetes/basics/symptoms.html'
CDC_HYPERTENSION_URL = 'https://www.cdc.gov/bloodpressure/about.htm'
CDC_BRONCHITIS_URL = 'https://www.cdc.gov/acute-bronchitis/about/index.html'
CDC_UTI_URL = 'https://www.cdc.gov/uti/about/index.html'
CDC_SEASONAL_ALLERGIES_URL = 'https://www.cdc.gov/healthyschools/air/seasonal_allergies.htm'

NEW_SYMPTOMS = [
    ('Excessive thirst', 'General'),
    ('Frequent urination', 'General'),
    ('Blurred vision', 'Neurological'),
    ('Slow-healing wound', 'General'),
    ('High blood pressure', 'Cardiovascular'),
    ('Mucus production', 'Respiratory'),
    ('Painful urination', 'Urinary'),
    ('Itchy eyes', 'Sensory'),
    ('Watery eyes', 'Sensory'),
    ('Chest tightness', 'Urgent warning signs'),
]

CONDITIONS = [
    {
        'name': 'Diabetes',
        'description': 'A chronic condition that affects how the body uses blood sugar for energy.',
        'general_information': (
            'Diabetes can cause increased thirst, frequent urination, fatigue, blurry vision, and slow-healing wounds. Some people may not notice symptoms at first, and the condition can range from mild to severe.'
        ),
        'medical_care_guidance': (
            'See a healthcare professional for evaluation if you notice unusual thirst, frequent urination, persistent fatigue, or vision changes. Diabetes can also increase the risk of heart, eye, and kidney complications.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_DIABETES_URL,
        'symptoms': ['Excessive thirst', 'Frequent urination', 'Fatigue', 'Blurred vision', 'Slow-healing wound'],
    },
    {
        'name': 'High blood pressure',
        'description': 'A condition in which blood pressure stays higher than is considered healthy over time.',
        'general_information': (
            'High blood pressure often has no obvious symptoms, which is why it is sometimes called a silent condition. In some people, headaches, dizziness, or shortness of breath may occur, especially if blood pressure is very high.'
        ),
        'medical_care_guidance': (
            'Regular checkups and blood pressure monitoring help identify this condition early. Seek urgent medical care for severe headache, chest pain, severe shortness of breath, or sudden weakness.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_HYPERTENSION_URL,
        'symptoms': ['Headache', 'Dizziness', 'Shortness of breath', 'High blood pressure'],
    },
    {
        'name': 'Bronchitis',
        'description': 'Inflammation of the bronchial tubes that can cause cough and mucus production.',
        'general_information': (
            'Acute bronchitis commonly causes a cough, mucus production, fatigue, and sometimes chest tightness or wheezing. It is often linked to a viral infection and can overlap with other respiratory illnesses.'
        ),
        'medical_care_guidance': (
            'Most people recover with rest and fluids, but medical guidance is important if symptoms last longer than expected, worsen, or are accompanied by trouble breathing or chest pain.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_BRONCHITIS_URL,
        'symptoms': ['Cough', 'Fatigue', 'Mucus production', 'Chest tightness', 'Wheezing'],
    },
    {
        'name': 'Urinary tract infection (UTI)',
        'description': 'An infection in the urinary system, most commonly affecting the bladder or urethra.',
        'general_information': (
            'A UTI may cause frequent urination, painful urination, pressure in the lower abdomen, and sometimes fever or nausea. Symptoms can vary, especially in older adults or during pregnancy.'
        ),
        'medical_care_guidance': (
            'Healthcare evaluation helps confirm the diagnosis and guide treatment. Seek urgent care for fever with back pain, confusion, signs of severe illness, or symptoms that are worsening.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_UTI_URL,
        'symptoms': ['Frequent urination', 'Painful urination', 'Fever', 'Nausea', 'Stomach pain'],
    },
    {
        'name': 'Seasonal allergies',
        'description': 'An immune reaction to allergens such as pollen, dust, or mold that can trigger allergy symptoms.',
        'general_information': (
            'Seasonal allergies can cause sneezing, a runny nose, itchy eyes, watery eyes, and fatigue. Symptoms often flare during certain times of the year when allergens are high in the air.'
        ),
        'medical_care_guidance': (
            'If symptoms are frequent or severe, a healthcare professional can review treatment options and evaluation for asthma or other related conditions.'
        ),
        'source_name': 'U.S. Centers for Disease Control and Prevention (CDC)',
        'source_url': CDC_SEASONAL_ALLERGIES_URL,
        'symptoms': ['Sneezing', 'Runny or stuffy nose', 'Itchy eyes', 'Watery eyes', 'Fatigue'],
    },
]


def seed_more_disease_entries(apps, schema_editor):
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
        ('symptoms', '0003_add_more_health_information'),
    ]

    operations = [
        migrations.RunPython(seed_more_disease_entries, migrations.RunPython.noop),
    ]

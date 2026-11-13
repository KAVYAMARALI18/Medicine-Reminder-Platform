import json
from unittest.mock import patch

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from accounts.models import User
from .medicine_info import lookup_medicine_information
from .models import (
    DiseaseInformation,
    DiseaseSymptom,
    Symptom,
    SymptomAssessment,
)


class SymptomFeatureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='symptom-user', password='test-password')
        self.other_user = User.objects.create_user(username='other-user', password='test-password')
        self.client.force_login(self.user)
        self.cough = Symptom.objects.get(name='Cough')
        self.fever = Symptom.objects.get(name='Fever')
        self.difficulty_breathing = Symptom.objects.get(name='Difficulty breathing')
        self.flu = DiseaseInformation.objects.get(name='Influenza (flu)')

    def create_assessment(self, user=None, symptoms=None):
        selected = symptoms or [self.cough, self.fever]
        assessment = SymptomAssessment.objects.create(
            user=user or self.user,
            duration='2 days',
            assessment_summary={
                'is_emergency': False,
                'emergency_matches': [],
                'conditions': [],
            },
        )
        assessment.symptoms.set(selected)
        return assessment

    def test_checker_requires_authentication(self):
        self.client.logout()

        response = self.client.get(reverse('symptoms:checker'))

        self.assertEqual(response.status_code, 302)

    def test_checker_displays_search_categories_and_disclaimer(self):
        response = self.client.get(reverse('symptoms:checker'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Search symptoms')
        self.assertContains(response, 'Filter by category')
        self.assertContains(response, 'not a diagnosis')

    def test_empty_symptom_selection_is_rejected(self):
        response = self.client.post(
            reverse('symptoms:checker'),
            {'duration': 'one day'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select at least one symptom.')
        self.assertEqual(SymptomAssessment.objects.count(), 0)

    def test_assessment_is_saved_with_sourced_associations(self):
        response = self.client.post(
            reverse('symptoms:checker'),
            {'symptoms': [self.cough.pk, self.fever.pk], 'duration': '2 days'},
        )

        assessment = SymptomAssessment.objects.get(user=self.user)
        self.assertRedirects(
            response,
            reverse('symptoms:assessment_result', args=[assessment.pk]),
        )
        self.assertEqual(set(assessment.symptoms.values_list('pk', flat=True)), {self.cough.pk, self.fever.pk})
        self.assertTrue(assessment.assessment_summary['conditions'])
        self.assertTrue(
            DiseaseSymptom.objects.filter(
                disease__name='Influenza (flu)',
                association_source__startswith='https://www.cdc.gov/',
            ).exists()
        )

    def test_emergency_symptom_bypasses_routine_condition_matching(self):
        response = self.client.post(
            reverse('symptoms:checker'),
            {
                'symptoms': [self.difficulty_breathing.pk, self.cough.pk],
                'duration': 'today',
            },
        )

        assessment = SymptomAssessment.objects.get(user=self.user)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(assessment.assessment_summary['is_emergency'])
        self.assertEqual(assessment.assessment_summary['conditions'], [])
        self.assertContains(
            self.client.get(reverse('symptoms:assessment_result', args=[assessment.pk])),
            'Seek immediate medical attention',
        )

    def test_history_and_assessment_results_are_private(self):
        private_assessment = self.create_assessment(user=self.other_user)

        self.assertEqual(self.client.get(reverse('symptoms:assessment_history')).status_code, 200)
        self.assertEqual(
            self.client.get(reverse('symptoms:assessment_result', args=[private_assessment.pk])).status_code,
            404,
        )
        self.assertEqual(
            self.client.post(reverse('symptoms:delete_assessment', args=[private_assessment.pk])).status_code,
            404,
        )
        self.assertTrue(SymptomAssessment.objects.filter(pk=private_assessment.pk).exists())

    def test_disease_information_page_uses_seeded_source(self):
        response = self.client.get(reverse('symptoms:disease_detail', args=[self.flu.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'https://www.cdc.gov/flu/signs-symptoms/index.html')
        self.assertContains(response, 'Body aches')

    @patch('symptoms.views.lookup_medicine_information')
    def test_medicine_information_is_educational_and_shows_source(self, lookup):
        lookup.return_value = [{
            'name': 'Example brand',
            'generic_name': 'Example generic',
            'prescription_status': 'HUMAN OTC DRUG',
            'purpose': 'Purpose from label',
            'indications': '',
            'warnings': 'Label warning',
            'do_not_use': '',
            'ask_doctor': '',
            'stop_use': '',
            'pregnancy': '',
            'source_name': 'U.S. FDA openFDA drug product labeling',
            'source_url': 'https://dailymed.nlm.nih.gov/dailymed/',
        }]

        response = self.client.get(
            reverse('symptoms:medicine_information'),
            {'q': 'Example'},
        )

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Purpose from label')
        self.assertContains(response, 'HUMAN OTC DRUG')
        self.assertContains(response, 'Educational information only')
        lookup.assert_called_once_with('Example')

    def test_api_requires_authentication(self):
        client = APIClient()

        response = client.get(reverse('symptoms_api:symptom-list'))

        self.assertIn(response.status_code, [401, 403])

    def test_api_creates_assessment_and_returns_summary(self):
        client = APIClient()
        client.force_authenticate(self.user)

        response = client.post(
            reverse('symptoms_api:assessment-list'),
            {'symptom_ids': [self.cough.pk, self.fever.pk], 'duration': '2 days'},
            format='json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(len(response.data['symptoms']), 2)
        self.assertTrue(response.data['assessment_summary']['conditions'])

    def test_api_rejects_empty_or_unknown_symptoms(self):
        client = APIClient()
        client.force_authenticate(self.user)

        empty_response = client.post(
            reverse('symptoms_api:assessment-list'),
            {'symptom_ids': [], 'duration': 'today'},
            format='json',
        )
        invalid_response = client.post(
            reverse('symptoms_api:assessment-list'),
            {'symptom_ids': [999999], 'duration': 'today'},
            format='json',
        )

        self.assertEqual(empty_response.status_code, 400)
        self.assertEqual(invalid_response.status_code, 400)

    def test_api_assessment_detail_is_private_and_history_is_user_scoped(self):
        assessment = self.create_assessment(user=self.other_user)
        client = APIClient()
        client.force_authenticate(self.user)

        detail = client.get(reverse('symptoms_api:assessment-detail', args=[assessment.pk]))
        history = client.get(reverse('symptoms_api:assessment-list'))

        self.assertEqual(detail.status_code, 404)
        self.assertEqual(history.data, [])

    def test_api_disease_and_medicine_information_require_authentication(self):
        client = APIClient()
        client.force_authenticate(self.user)

        diseases = client.get(reverse('symptoms_api:disease-list'))
        missing_query = client.get(reverse('symptoms_api:medicine-information'))

        self.assertEqual(diseases.status_code, 200)
        self.assertIn(self.flu.name, [item['name'] for item in diseases.data])
        self.assertEqual(missing_query.status_code, 400)

    @patch('symptoms.medicine_info.urlopen')
    def test_fda_label_service_returns_official_label_fields_without_dosage(self, urlopen_mock):
        from unittest.mock import MagicMock

        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps({
            'results': [{
                'openfda': {
                    'brand_name': ['Example'],
                    'generic_name': ['Example ingredient'],
                    'product_type': ['HUMAN OTC DRUG'],
                    'spl_set_id': ['12345678-1234-1234-1234-123456789012'],
                },
                'purpose': ['Label purpose'],
                'warnings': ['Label warning'],
                'dosage_and_administration': ['This field must not be presented.'],
            }],
        }).encode()
        urlopen_mock.return_value = response

        result = lookup_medicine_information('Example')

        self.assertEqual(result[0]['purpose'], 'Label purpose')
        self.assertEqual(result[0]['warnings'], 'Label warning')
        self.assertNotIn('dosage', result[0])
        self.assertIn('dailymed.nlm.nih.gov', result[0]['source_url'])

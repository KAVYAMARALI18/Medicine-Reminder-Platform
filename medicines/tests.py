from datetime import date
from io import BytesIO
from tempfile import TemporaryDirectory
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from openpyxl import load_workbook

from accounts.models import User
from .forms import MedicineForm
from .models import Medicine, RefillRecord
from reminders.models import MedicineLog, Reminder


class MedicineFeatureTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='patient', password='test-password')
        self.other_user = User.objects.create_user(username='other', password='test-password')
        self.medicine = Medicine.objects.create(
            user=self.user,
            name='Daily medicine',
            dosage='1 tablet',
            start_date=date.today(),
        )
        self.client.force_login(self.user)

    def test_detail_page_displays_personal_qr_code(self):
        response = self.client.get(reverse('medicine_detail', args=[self.medicine.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data:image/png;base64,')

    def test_medicine_detail_is_private_to_its_owner(self):
        other_medicine = Medicine.objects.create(
            user=self.other_user,
            name='Private medicine',
            dosage='1 tablet',
            start_date=date.today(),
        )

        response = self.client.get(reverse('medicine_detail', args=[other_medicine.pk]))

        self.assertEqual(response.status_code, 404)

    def test_edit_form_displays_private_prescription_without_public_url(self):
        self.medicine.prescription_upload.name = 'prescriptions/existing.pdf'
        self.medicine.save(update_fields=['prescription_upload'])

        response = self.client.get(reverse('medicine_edit', args=[self.medicine.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'existing.pdf')

    def test_admin_form_displays_private_prescription_without_public_url(self):
        self.medicine.prescription_upload.name = 'prescriptions/existing.pdf'
        self.medicine.save(update_fields=['prescription_upload'])
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='test-password',
        )
        self.client.force_login(admin_user)

        response = self.client.get(reverse('admin:medicines_medicine_change', args=[self.medicine.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'existing.pdf')

    def test_prescription_download_is_private_and_uses_attachment_response(self):
        storage = self.medicine._meta.get_field('prescription_upload').storage
        content = b'%PDF-1.4 private prescription'
        with TemporaryDirectory() as temporary_directory:
            with patch.object(storage, '_location', temporary_directory):
                self.medicine.prescription_upload.save(
                    'prescription.pdf',
                    ContentFile(content),
                    save=True,
                )
                response = self.client.get(reverse('prescription_download', args=[self.medicine.pk]))

                self.assertEqual(response.status_code, 200)
                self.assertIn('attachment', response['Content-Disposition'])
                self.assertEqual(b''.join(response.streaming_content), content)
                response.close()

    def test_voice_reminder_endpoint_returns_due_uncompleted_reminders(self):
        current_time = timezone.localtime().time().replace(second=0, microsecond=0)
        reminder = Reminder.objects.create(medicine=self.medicine, time=current_time)

        response = self.client.get(reverse('check_reminders'))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['reminders'][0]['id'], reminder.pk)

        MedicineLog.objects.create(
            reminder=reminder,
            user=self.user,
            date=timezone.localdate(),
            status='Taken',
        )
        response = self.client.get(reverse('check_reminders'))
        self.assertEqual(response.json()['reminders'], [])

    def test_scanner_page_requires_authentication(self):
        self.client.logout()

        response = self.client.get(reverse('medicine_qr_scanner'))

        self.assertRedirects(
            response,
            f'{reverse("login")}?next={reverse("medicine_qr_scanner")}',
        )

    def test_scanner_page_renders_for_authenticated_user(self):
        response = self.client.get(reverse('medicine_qr_scanner'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Start camera')
        self.assertContains(response, 'sample medicine QR code')

    def test_dashboard_renders_voice_reminder_controls(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Enable voice reminders')

    def test_refill_page_renders_when_user_has_no_medicines(self):
        self.medicine.delete()

        response = self.client.get(reverse('refill_tracking'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No medicines available')

    def test_refill_page_uses_selected_medicine_add_route(self):
        response = self.client.get(reverse('refill_tracking'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'data-refill-url="{reverse("add_refill", args=[self.medicine.pk])}"',
        )

    def test_refill_page_posts_refill_for_selected_medicine(self):
        response = self.client.post(
            reverse('add_refill', args=[self.medicine.pk]),
            {
                'refill_date': date.today().isoformat(),
                'quantity_added': '12',
                'cost': '8.50',
                'pharmacy_name': 'Local pharmacy',
                'notes': 'Monthly refill',
            },
        )

        self.assertRedirects(response, reverse('refill_tracking'))
        self.medicine.refresh_from_db()
        self.assertEqual(self.medicine.quantity, 13)
        self.assertEqual(self.medicine.last_refill_date, date.today())
        refill = RefillRecord.objects.get(medicine=self.medicine)
        self.assertEqual(refill.quantity_added, 12)
        self.assertEqual(refill.quantity_after_refill, 13)
        self.assertEqual(refill.cost, 8.50)

    def test_refill_rejects_invalid_numeric_input_without_server_error(self):
        response = self.client.post(
            reverse('add_refill', args=[self.medicine.pk]),
            {'quantity_added': 'invalid', 'cost': 'invalid'},
        )

        self.assertRedirects(response, reverse('refill_tracking'))
        self.assertFalse(RefillRecord.objects.filter(medicine=self.medicine).exists())

    def test_report_exports_return_pdf_and_excel_files(self):
        pdf_response = self.client.get(reverse('export_reports', args=['pdf']))
        excel_response = self.client.get(reverse('export_reports', args=['excel']))

        self.assertEqual(pdf_response.status_code, 200)
        self.assertTrue(pdf_response.content.startswith(b'%PDF'))
        self.assertEqual(pdf_response['Content-Type'], 'application/pdf')
        self.assertEqual(excel_response.status_code, 200)
        self.assertTrue(excel_response.content.startswith(b'PK'))
        self.assertIn(
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            excel_response['Content-Type'],
        )
        workbook = load_workbook(BytesIO(excel_response.content), read_only=True)
        worksheet = workbook['Medicine Report']
        self.assertEqual(worksheet['A1'].value, 'Medicine')
        self.assertEqual(worksheet['A2'].value, self.medicine.name)
        workbook.close()

    def test_prescription_upload_rejects_non_pdf_content(self):
        upload = SimpleUploadedFile(
            'prescription.pdf',
            b'not a PDF',
            content_type='application/pdf',
        )
        form = MedicineForm(files={'prescription_upload': upload})

        self.assertIn('prescription_upload', form.errors)

    def test_prescription_upload_rejects_oversized_files(self):
        upload = SimpleUploadedFile(
            'prescription.pdf',
            b'%PDF-' + b'x' * (10 * 1024 * 1024),
            content_type='application/pdf',
        )
        form = MedicineForm(files={'prescription_upload': upload})

        self.assertIn('prescription_upload', form.errors)

from datetime import date, time
from unittest.mock import patch

from django.core import mail
from django.test import TestCase, override_settings
from django.utils import timezone

from accounts.models import User
from medicines.models import Medicine
from medicines.notifications import send_email_notification
from .models import MedicineLog, Reminder


class EmailReminderTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='patient',
            email='patient@example.com',
            password='test-password',
        )
        self.medicine = Medicine.objects.create(
            user=self.user,
            name='Daily medicine',
            dosage='1 tablet',
            start_date=date.today(),
        )
        self.reminder = Reminder.objects.create(medicine=self.medicine, time=time(8, 30))
        self.log = MedicineLog.objects.create(
            reminder=self.reminder,
            user=self.user,
            date=date.today(),
        )

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='reminders@example.com',
    )
    def test_sends_reminder_to_user_email_and_records_success(self):
        sent_at = timezone.now()

        result = send_email_notification(
            self.user,
            self.medicine,
            self.reminder,
            self.log,
            sent_at,
        )

        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].to, [self.user.email])
        self.assertEqual(self.log.email_delivery_status, 'Sent')
        self.assertEqual(self.log.email_sent_time, sent_at)

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        DEFAULT_FROM_EMAIL='reminders@example.com',
    )
    @patch('medicines.notifications.EmailMultiAlternatives.send', return_value=0)
    def test_records_failure_when_email_backend_sends_nothing(self, send):
        result = send_email_notification(
            self.user,
            self.medicine,
            self.reminder,
            self.log,
            timezone.now(),
        )

        self.assertFalse(result)
        self.assertEqual(self.log.email_delivery_status, 'Failed')
        self.assertIsNone(self.log.email_sent_time)
        send.assert_called_once_with(fail_silently=False)

    def test_does_not_send_when_user_has_no_email_or_has_disabled_notifications(self):
        self.user.email = ''
        self.user.save(update_fields=['email'])

        result = send_email_notification(
            self.user,
            self.medicine,
            self.reminder,
            self.log,
            timezone.now(),
        )

        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)

        self.user.email = 'patient@example.com'
        self.user.email_notifications_enabled = False
        self.user.save(update_fields=['email', 'email_notifications_enabled'])
        result = send_email_notification(
            self.user,
            self.medicine,
            self.reminder,
            self.log,
            timezone.now(),
        )

        self.assertFalse(result)
        self.assertEqual(len(mail.outbox), 0)

# Create your tests here.

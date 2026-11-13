import logging
import os
import re

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from accounts.models import FamilyAccess

logger = logging.getLogger(__name__)


def normalize_phone_number(phone_number):
    if not phone_number:
        return None

    digits = re.sub(r'\D', '', str(phone_number))
    if not digits:
        return None

    if digits.startswith('+'):
        return digits

    return f'+{digits}'


def send_sms_message(phone_number, message):
    number = normalize_phone_number(phone_number)
    if not number:
        return False, 'No phone number available.'

    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', '') or os.getenv('TWILIO_ACCOUNT_SID', '')
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', '') or os.getenv('TWILIO_AUTH_TOKEN', '')
    from_number = getattr(settings, 'TWILIO_PHONE_NUMBER', '') or os.getenv('TWILIO_PHONE_NUMBER', '')

    if not all([account_sid, auth_token, from_number]):
        logger.warning('Twilio SMS configuration is missing. SMS delivery skipped.')
        return False, 'Twilio configuration not set.'

    try:
        from twilio.rest import Client

        client = Client(account_sid, auth_token)
        client.messages.create(
            body=message,
            from_=from_number,
            to=number,
        )
        logger.info('SMS reminder sent to %s', number)
        return True, 'SMS sent successfully.'
    except Exception as exc:  # pragma: no cover - integration-specific fallback
        logger.exception('Failed to send SMS reminder to %s', number)
        return False, str(exc)


def send_email_notification(user, medicine, reminder, log, sent_at):
    if not user.email or not user.email_notifications_enabled or log.email_delivery_status != 'Pending':
        return False

    try:
        context = {
            'patient_name': user.first_name or user.username,
            'medicine_name': medicine.name,
            'dosage': medicine.dosage,
            'medicine_type': medicine.medicine_type,
            'scheduled_time': reminder.time.strftime('%I:%M %p'),
            'before_after_food': medicine.before_after_food,
            'notes': medicine.notes,
            'doctor_name': getattr(medicine, 'doctor_name', None),
        }
        html_content = render_to_string('emails/reminder.html', context)
        message = EmailMultiAlternatives(
            '💊 Medicine Reminder - Time to Take Your Medication',
            strip_tags(html_content),
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
        )
        message.attach_alternative(html_content, 'text/html')
        sent_count = message.send(fail_silently=False)
        if sent_count != 1:
            log.email_delivery_status = 'Failed'
            logger.error('Email backend did not send a reminder to %s', user.email)
            return False

        log.email_delivery_status = 'Sent'
        log.email_sent_time = sent_at
        logger.info('Email reminder sent to %s', user.email)
        return True
    except Exception as exc:  # pragma: no cover - integration-specific fallback
        log.email_delivery_status = 'Failed'
        logger.exception('Failed to send email reminder to %s', user.email)
        return False


def send_caregiver_notifications(user, medicine, reminder, sent_at):
    caregivers = FamilyAccess.objects.filter(user=user, is_active=True, can_receive_reminders=True)
    if not caregivers.exists():
        return

    message = (
        f"Reminder: {user.first_name or user.username} should take {medicine.name} "
        f"({medicine.dosage}) at {reminder.time.strftime('%I:%M %p')}"
    )

    for caregiver in caregivers:
        if caregiver.caregiver_phone:
            send_sms_message(caregiver.caregiver_phone, message)

        if caregiver.caregiver_email:
            try:
                from django.core.mail import EmailMultiAlternatives

                html = render_to_string('emails/reminder.html', {
                    'patient_name': user.first_name or user.username,
                    'medicine_name': medicine.name,
                    'dosage': medicine.dosage,
                    'medicine_type': medicine.medicine_type,
                    'scheduled_time': reminder.time.strftime('%I:%M %p'),
                    'before_after_food': medicine.before_after_food,
                    'notes': medicine.notes,
                    'doctor_name': getattr(medicine, 'doctor_name', None),
                })
                text = strip_tags(html)
                email = EmailMultiAlternatives(
                    f'Caregiver alert: {medicine.name} reminder',
                    text,
                    getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@medremindersystem.local'),
                    [caregiver.caregiver_email],
                )
                email.attach_alternative(html, 'text/html')
                email.send(fail_silently=True)
            except Exception:
                logger.exception('Failed to send caregiver email to %s', caregiver.caregiver_email)


def send_reminder_message(user, medicine, reminder, log, now):
    if user.email_notifications_enabled:
        send_email_notification(user, medicine, reminder, log, now)

    if getattr(user, 'sms_notifications_enabled', False) and getattr(user, 'sms_phone_number', None):
        sms_message = (
            f"Reminder: Take {medicine.name} ({medicine.dosage}) "
            f"{medicine.before_after_food.lower()} at {reminder.time.strftime('%I:%M %p')}."
        )
        success, _ = send_sms_message(user.sms_phone_number, sms_message)
        log.sms_delivery_status = 'Sent' if success else 'Failed'
        log.sms_sent_time = now if success else None

    send_caregiver_notifications(user, medicine, reminder, now)

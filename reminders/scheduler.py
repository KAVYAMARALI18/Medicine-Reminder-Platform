from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

def check_and_send_reminders():
    # To avoid circular imports, import models here
    from reminders.models import Reminder, MedicineLog
    from api.fcm import send_push_notification
    from medicines.notifications import send_reminder_message
    from datetime import date
    
    now = timezone.localtime(timezone.now())
    today = now.date()
    current_time = now.time()
    
    # Find active reminders for the exact hour and minute
    reminders = Reminder.objects.filter(
        is_active=True,
        time__hour=current_time.hour,
        time__minute=current_time.minute
    )
    
    for reminder in reminders:
        medicine = reminder.medicine
        # Get or create the log for today
        log, created = MedicineLog.objects.get_or_create(
            reminder=reminder,
            date=today,
            user=medicine.user,
            defaults={'status': 'Pending', 'delivery_status': 'Pending'}
        )
        
        # If it hasn't been sent yet, send it
        if log.delivery_status == 'Pending':
            title = f"Time for Medicine: {medicine.name}"
            body = f"Take {medicine.dosage} {medicine.before_after_food}"
            if medicine.notes:
                body += f" ({medicine.notes})"
            
            data = {
                'medicine_id': str(medicine.id),
                'reminder_id': str(reminder.id),
                'log_id': str(log.id),
                'action': 'medication_reminder'
            }
            
            success = send_push_notification(medicine.user, title, body, data)
            if success:
                log.delivery_status = 'Sent'
            else:
                log.delivery_status = 'Failed'
                
            send_reminder_message(medicine.user, medicine, reminder, log, now)
            log.save()

    # Check for snoozed reminders that are due now
    snoozed_logs = MedicineLog.objects.filter(
        status='Pending',
        delivery_status='Sent', # It was sent, then snoozed
        snooze_time__lte=now
    )
    
    for log in snoozed_logs:
        medicine = log.reminder.medicine
        title = f"Snoozed Reminder: {medicine.name}"
        body = f"It's time to take {medicine.dosage} {medicine.before_after_food}"
        
        data = {
            'medicine_id': str(medicine.id),
            'reminder_id': str(log.reminder.id),
            'log_id': str(log.id),
            'action': 'medication_reminder'
        }
        
        success = send_push_notification(medicine.user, title, body, data)
        # Reset snooze time so it doesn't fire continuously
        log.snooze_time = None 
        log.save()

def start_scheduler():
    scheduler = BackgroundScheduler(timezone=timezone.get_current_timezone())
    
    # Run every minute
    scheduler.add_job(
        check_and_send_reminders,
        'cron',
        minute='*',
        id='check_reminders_job',
        replace_existing=True,
    )
    
    register_events(scheduler)
    scheduler.start()
    logger.info("Scheduler started.")

import json
from datetime import timedelta

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from reminders.models import MedicineLog, Reminder
from .models import FCMDevice

@login_required
def check_reminders(request):
    now = timezone.localtime(timezone.now())
    today = timezone.localdate()
    completed_reminder_ids = MedicineLog.objects.filter(
        user=request.user,
        date=today,
    ).exclude(status='Pending').values_list('reminder_id', flat=True)
    reminders = Reminder.objects.filter(
        medicine__user=request.user,
        is_active=True,
        time__hour=now.hour,
        time__minute=now.minute
    ).exclude(pk__in=completed_reminder_ids).select_related('medicine')
    
    data = []
    for r in reminders:
        data.append({
            'id': r.pk,
            'date': today.isoformat(),
            'medicine': r.medicine.name,
            'dosage': r.medicine.dosage,
            'time': r.time.strftime("%H:%M")
        })
        
    return JsonResponse({'reminders': data})

@csrf_exempt
@login_required
def register_device(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            token = data.get('token')
            if token:
                FCMDevice.objects.get_or_create(
                    user=request.user,
                    registration_id=token,
                    defaults={'active': True}
                )
                return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def notification_action(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            log_id = data.get('log_id')
            action = data.get('action') # 'taken', 'skipped', 'snooze'
            
            if not log_id or not action:
                return JsonResponse({'status': 'error', 'message': 'Missing data'}, status=400)
                
            log = MedicineLog.objects.get(id=log_id)
            
            if action == 'taken':
                log.status = 'Taken'
                log.taken_at = timezone.now()
            elif action == 'skipped':
                log.status = 'Skipped'
            elif action == 'snooze':
                # Snooze for 15 minutes by default
                log.snooze_time = timezone.now() + timedelta(minutes=15)
                
            log.save()
            return JsonResponse({'status': 'success'})
        except MedicineLog.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Log not found'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    return JsonResponse({'status': 'error'}, status=400)

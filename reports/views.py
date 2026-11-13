from datetime import timedelta
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from medicines.models import Medicine
from reminders.models import MedicineLog

@login_required
def reports_view(request):
    user = request.user
    today = timezone.now().date()
    six_weeks_ago = today - timedelta(days=42)

    adherence = []
    labels = []
    for offset in range(6):
        day = today - timedelta(days=offset)
        labels.append(day.strftime('%b %d'))
        adherence.append(MedicineLog.objects.filter(user=user, date=day, status='Taken').count())

    missed = MedicineLog.objects.filter(user=user, date__gte=six_weeks_ago, status='Missed').count()
    taken = MedicineLog.objects.filter(user=user, date__gte=six_weeks_ago, status='Taken').count()
    pending = MedicineLog.objects.filter(user=user, date__gte=six_weeks_ago, status='Pending').count()
    medications = Medicine.objects.filter(user=user)

    return render(request, 'medicines/reports.html', {
        'labels': labels[::-1],
        'adherence': adherence[::-1],
        'missed': missed,
        'taken': taken,
        'pending': pending,
        'medications': medications,
    })

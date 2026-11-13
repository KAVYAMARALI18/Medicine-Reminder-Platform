import base64
from decimal import Decimal, InvalidOperation
from io import BytesIO
import qrcode
from django.http import FileResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Q, F
from django.utils import timezone
from .models import Medicine, RefillRecord
from symptoms.models import SymptomAssessment
from reminders.models import Reminder, MedicineLog
from .forms import MedicineForm, ReminderFormSet
from datetime import date, timedelta


def _get_refill_alerts_for_user(user):
    today = date.today()
    alerts = []
    for medicine in Medicine.objects.filter(user=user).exclude(last_refill_date__isnull=True):
        if medicine.last_refill_date is None:
            continue
        next_due_date = medicine.last_refill_date + timedelta(days=medicine.refill_reminder_days)
        days_left = (next_due_date - today).days
        if days_left <= 14:
            alerts.append({
                'medicine': medicine,
                'next_due_date': next_due_date,
                'days_left': days_left,
                'is_due': days_left <= 0,
            })
    return sorted(alerts, key=lambda item: item['days_left'])


def _calculate_adherence_rate(user, days=7):
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)
    logs = MedicineLog.objects.filter(user=user, date__range=[start_date, end_date])
    total = logs.count()
    if total == 0:
        return 0
    taken = logs.filter(status='Taken').count()
    return round((taken / total) * 100, 1)

@login_required
def dashboard(request):
    user = request.user
    today = date.today()
    now = timezone.localtime(timezone.now()).time()

    total_medicines = Medicine.objects.filter(user=user).count()
    dashboard_medicines = Medicine.objects.filter(user=user).order_by('name')[:5]
    today_logs = MedicineLog.objects.filter(user=user, date=today)
    completed_today = today_logs.filter(status='Taken').count()
    missed_today = today_logs.filter(status='Missed').count()
    low_stock_medicines = Medicine.objects.filter(user=user, quantity__lte=F('low_stock_threshold'))
    refill_alerts = _get_refill_alerts_for_user(user)
    adherence_rate = _calculate_adherence_rate(user)

    reminders = Reminder.objects.filter(medicine__user=user, is_active=True).select_related('medicine').order_by('time')
    today_schedule = []
    next_reminder_time = None

    for reminder in reminders:
        log = MedicineLog.objects.filter(reminder=reminder, user=user, date=today).first()
        status = log.status if log else 'Pending'
        reminder_time = reminder.time
        if next_reminder_time is None and reminder_time >= now:
            next_reminder_time = reminder_time
        today_schedule.append({
            'reminder': reminder,
            'medicine': reminder.medicine,
            'time': reminder_time,
            'status': status,
        })

    if next_reminder_time is None and reminders.exists():
        next_reminder_time = reminders.first().time

    weekly_labels = []
    weekly_data = []
    for offset in range(6, -1, -1):
        day = today - timedelta(days=offset)
        weekly_labels.append(day.strftime('%a'))
        taken = MedicineLog.objects.filter(user=user, date=day, status='Taken').count()
        weekly_data.append(taken)

    context = {
        'total_medicines': total_medicines,
        'dashboard_medicines': dashboard_medicines,
        'completed_today': completed_today,
        'missed_today': missed_today,
        'low_stock_medicines': low_stock_medicines,
        'refill_alerts': refill_alerts,
        'adherence_rate': adherence_rate,
        'today_schedule': today_schedule,
        'next_reminder_time': next_reminder_time,
        'weekly_labels': weekly_labels,
        'weekly_data': weekly_data,
        'today': today,
        'symptom_assessment_count': SymptomAssessment.objects.filter(user=user).count(),
        'recent_symptom_assessments': (
            SymptomAssessment.objects.filter(user=user)
            .prefetch_related('symptoms')[:3]
        ),
    }
    return render(request, 'medicines/dashboard.html', context)

@login_required
def update_reminder_status(request, reminder_id):
    if request.method != 'POST':
        return redirect('dashboard')

    reminder = get_object_or_404(Reminder, pk=reminder_id, medicine__user=request.user)
    status = request.POST.get('status', 'Pending')

    if status not in dict(MedicineLog.STATUS_CHOICES):
        messages.error(request, 'Invalid reminder status.')
        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

    log, _ = MedicineLog.objects.get_or_create(reminder=reminder, user=request.user, date=date.today())
    log.status = status
    if status == 'Taken':
        log.taken_at = timezone.now()
    else:
        log.taken_at = None
    log.save()

    messages.success(request, f"Reminder marked as {status}.")
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

@login_required
def medicine_list(request):
    medicines = Medicine.objects.filter(user=request.user).order_by('name')
    query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', 'all').strip().lower()
    today = date.today()

    if query:
        medicines = medicines.filter(
            Q(name__icontains=query) |
            Q(medicine_type__icontains=query) |
            Q(dosage__icontains=query)
        )

    if status_filter == 'low_stock':
        medicines = medicines.filter(quantity__lte=F('low_stock_threshold'))
    elif status_filter == 'refill_due':
        medicines = medicines.exclude(last_refill_date__isnull=True).filter(
            last_refill_date__lte=today - timedelta(days=7)
        )
    elif status_filter == 'needs_attention':
        medicines = medicines.filter(
            Q(quantity__lte=F('low_stock_threshold')) |
            Q(last_refill_date__lte=today - timedelta(days=7))
        )

    return render(request, 'medicines/medicine_list.html', {
        'medicines': medicines,
        'query': query,
        'status_filter': status_filter,
    })


@login_required
def medicine_history(request):
    logs = MedicineLog.objects.filter(user=request.user).select_related('reminder__medicine').order_by('-date', '-taken_at', '-id')[:80]
    return render(request, 'medicines/medicine_history.html', {'logs': logs})


@login_required
def medicine_detail(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)
    detail_url = request.build_absolute_uri(reverse('medicine_detail', args=[medicine.pk]))
    qr_image = qrcode.make(detail_url)
    image_buffer = BytesIO()
    qr_image.save(image_buffer, format='PNG')
    qr_code = base64.b64encode(image_buffer.getvalue()).decode('ascii')
    reminders = medicine.reminders.filter(is_active=True).order_by('time')
    return render(request, 'medicines/medicine_detail.html', {
        'medicine': medicine,
        'reminders': reminders,
        'qr_code': qr_code,
    })


@login_required
def medicine_qr_scanner(request):
    return render(request, 'medicines/medicine_qr_scanner.html')


@login_required
def prescription_download(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)
    prescription = medicine.prescription_upload
    if not prescription or not prescription.storage.exists(prescription.name):
        messages.error(request, 'No prescription file is available for this medicine.')
        return redirect('medicine_detail', pk=medicine.pk)
    return FileResponse(
        prescription.open('rb'),
        as_attachment=True,
        filename=prescription.name.rsplit('/', 1)[-1],
        content_type='application/octet-stream',
    )


@login_required
def refill_tracking(request):
    medicines = Medicine.objects.filter(user=request.user).select_related('user').prefetch_related('refills')
    refill_records = RefillRecord.objects.filter(medicine__user=request.user).select_related('medicine')
    return render(request, 'medicines/refill_tracking.html', {
        'medicines': medicines,
        'refill_records': refill_records,
    })

@login_required
def add_refill(request, medicine_id):
    medicine = get_object_or_404(Medicine, pk=medicine_id, user=request.user)
    if request.method == 'POST':
        try:
            refill_date = date.fromisoformat(request.POST.get('refill_date') or date.today().isoformat())
            quantity_added = int(request.POST.get('quantity_added', 0) or 0)
            cost = Decimal(request.POST.get('cost', '') or '0')
        except (ValueError, InvalidOperation):
            messages.error(request, 'Enter a valid refill date, quantity, and cost.')
            return redirect('refill_tracking')

        pharmacy_name = request.POST.get('pharmacy_name', '').strip()
        notes = request.POST.get('notes', '').strip()

        if quantity_added <= 0:
            messages.error(request, 'Quantity added must be greater than zero.')
            return redirect('refill_tracking')
        if not cost.is_finite() or cost < 0 or cost > Decimal('99999999.99'):
            messages.error(request, 'Cost must be a valid amount between 0 and 99999999.99.')
            return redirect('refill_tracking')

        with transaction.atomic():
            medicine.quantity += quantity_added
            medicine.last_refill_date = refill_date
            medicine.save(update_fields=['quantity', 'last_refill_date', 'updated_at'])

            RefillRecord.objects.create(
                medicine=medicine,
                refill_date=refill_date,
                quantity_added=quantity_added,
                quantity_after_refill=medicine.quantity,
                cost=cost,
                pharmacy_name=pharmacy_name or None,
                notes=notes or None,
            )
        messages.success(request, f'Refill recorded for {medicine.name}.')
        return redirect('refill_tracking')
    return redirect('refill_tracking')

@login_required
def export_reports(request, format_type):
    if format_type not in ['pdf', 'excel']:
        return redirect('reports')

    medicines = Medicine.objects.filter(user=request.user)
    rows = []
    for medicine in medicines:
        rows.append({
            'Medicine': medicine.name,
            'Type': medicine.medicine_type,
            'Dosage': medicine.dosage,
            'Quantity': medicine.quantity,
            'Low Stock Threshold': medicine.low_stock_threshold,
            'Last Refill': medicine.last_refill_date or 'N/A',
            'Next Refill Due': (medicine.last_refill_date + timedelta(days=medicine.refill_reminder_days)).isoformat() if medicine.last_refill_date else 'N/A',
        })

    if format_type == 'excel':
        from openpyxl import Workbook

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = 'Medicine Report'
        fieldnames = ['Medicine', 'Type', 'Dosage', 'Quantity', 'Low Stock Threshold', 'Last Refill', 'Next Refill Due']
        worksheet.append(fieldnames)
        for row in rows:
            worksheet.append([row[fieldname] for fieldname in fieldnames])

        output = BytesIO()
        workbook.save(output)
        response = HttpResponse(
            output.getvalue(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        )
        response['Content-Disposition'] = 'attachment; filename="medicine_report.xlsx"'
        return response

    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
    from reportlab.lib.styles import getSampleStyleSheet

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    data = [['Medicine', 'Type', 'Dosage', 'Quantity', 'Low Stock Threshold', 'Last Refill', 'Next Refill Due']]
    for row in rows:
        data.append([
            row['Medicine'],
            row['Type'],
            row['Dosage'],
            row['Quantity'],
            row['Low Stock Threshold'],
            row['Last Refill'],
            row['Next Refill Due'],
        ])

    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0d6efd')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('GRID', (0, 0), (-1, -1), 1, colors.grey),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
    ]))
    doc.build([Paragraph('Medicine Report', styles['Title']), table])

    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="medicine_report.pdf"'
    return response

@login_required
def medicine_create(request):
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES)
        formset = ReminderFormSet(request.POST)
        if form.is_valid() and formset.is_valid():
            medicine = form.save(commit=False)
            medicine.user = request.user
            medicine.save()
            formset.instance = medicine
            formset.save()
            messages.success(request, 'Medicine added successfully!')
            return redirect('medicine_list')
    else:
        form = MedicineForm()
        formset = ReminderFormSet()
    
    return render(request, 'medicines/medicine_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Add Medicine'
    })

@login_required
def medicine_edit(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)
    if request.method == 'POST':
        form = MedicineForm(request.POST, request.FILES, instance=medicine)
        formset = ReminderFormSet(request.POST, instance=medicine)
        if form.is_valid() and formset.is_valid():
            form.save()
            formset.save()
            messages.success(request, 'Medicine updated successfully!')
            return redirect('medicine_list')
    else:
        form = MedicineForm(instance=medicine)
        formset = ReminderFormSet(instance=medicine)
    
    return render(request, 'medicines/medicine_form.html', {
        'form': form,
        'formset': formset,
        'title': 'Edit Medicine'
    })

@login_required
def medicine_delete(request, pk):
    medicine = get_object_or_404(Medicine, pk=pk, user=request.user)
    if request.method == 'POST':
        medicine.delete()
        messages.success(request, 'Medicine deleted successfully!')
        return redirect('medicine_list')
    return render(request, 'medicines/medicine_confirm_delete.html', {'medicine': medicine})

@login_required
def calendar_view(request):
    return render(request, 'medicines/calendar.html')

@login_required
def reports_view(request):
    user = request.user
    months = []
    taken = []
    missed = []
    for i in range(5, -1, -1):
        day = date.today() - timedelta(days=i * 7)
        month_label = day.strftime('%b %d')
        months.append(month_label)
        taken.append(MedicineLog.objects.filter(user=user, date__range=[day - timedelta(days=6), day], status='Taken').count())
        missed.append(MedicineLog.objects.filter(user=user, date__range=[day - timedelta(days=6), day], status='Missed').count())

    missed_logs = MedicineLog.objects.filter(user=user, status='Missed').order_by('-date')[:10]
    return render(request, 'medicines/reports.html', {
        'month_labels': months,
        'taken_data': taken,
        'missed_data': missed,
        'missed_logs': missed_logs,
    })

@login_required
def settings_view(request):
    user = request.user
    if request.method == 'POST':
        user.dark_mode = request.POST.get('dark_mode') == 'on'
        user.sound_enabled = request.POST.get('sound_enabled') == 'on'
        user.desktop_notifications_enabled = request.POST.get('desktop_notifications') == 'on'
        user.email_notifications_enabled = request.POST.get('email_notifications_enabled') == 'on'
        user.sms_notifications_enabled = request.POST.get('sms_notifications_enabled') == 'on'
        user.sms_phone_number = request.POST.get('sms_phone_number', '').strip() or None
        user.language = request.POST.get('language', 'en')
        user.save()
        messages.success(request, 'Settings saved successfully.')
        return redirect('settings')
    return render(request, 'medicines/settings.html')

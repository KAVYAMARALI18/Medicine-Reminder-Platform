from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib import messages
from .forms import UserRegisterForm, FamilyAccessForm
from django.contrib.auth.decorators import login_required
from .models import EmergencyContact, FamilyAccess
from medicines.models import Medicine
from reminders.models import Reminder, MedicineLog
from datetime import date

def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            EmergencyContact.objects.create(user=user)
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

@login_required
def profile(request):
    caregivers = FamilyAccess.objects.filter(user=request.user, is_active=True)
    return render(request, 'accounts/profile.html', {'caregivers': caregivers})

@login_required
def caregiver_access(request):
    caregivers = FamilyAccess.objects.filter(user=request.user).order_by('caregiver_name')
    medicines = Medicine.objects.filter(user=request.user)
    today = date.today()
    schedule = []
    for reminder in Reminder.objects.filter(medicine__user=request.user, is_active=True).select_related('medicine').order_by('time'):
        log = MedicineLog.objects.filter(reminder=reminder, user=request.user, date=today).first()
        status = log.status if log else 'Pending'
        schedule.append({
            'medicine': reminder.medicine,
            'time': reminder.time.strftime('%H:%M'),
            'status': status,
            'badge_class': 'success' if status == 'Taken' else 'danger' if status == 'Missed' else 'warning' if status == 'Skipped' else 'secondary',
        })

    caregiver_form = FamilyAccessForm()
    if request.method == 'POST':
        caregiver_form = FamilyAccessForm(request.POST)
        if caregiver_form.is_valid():
            caregiver = caregiver_form.save(commit=False)
            caregiver.user = request.user
            caregiver.save()
            messages.success(request, 'Caregiver added successfully.')
            return redirect('caregiver_access')

    context = {
        'caregivers': caregivers,
        'caregiver_form': caregiver_form,
        'medicines': medicines,
        'schedule': schedule,
        'today_doses': len(schedule),
        'missed_doses': sum(1 for item in schedule if item['status'] == 'Missed'),
    }
    return render(request, 'accounts/caregiver_access.html', context)


@login_required
def edit_caregiver(request, caregiver_id):
    caregiver = get_object_or_404(FamilyAccess, pk=caregiver_id, user=request.user)
    if request.method == 'POST':
        form = FamilyAccessForm(request.POST, instance=caregiver)
        if form.is_valid():
            form.save()
            messages.success(request, 'Caregiver updated successfully.')
            return redirect('caregiver_access')
    else:
        form = FamilyAccessForm(instance=caregiver)

    return render(request, 'accounts/caregiver_form.html', {'form': form, 'caregiver': caregiver})


@login_required
def delete_caregiver(request, caregiver_id):
    caregiver = get_object_or_404(FamilyAccess, pk=caregiver_id, user=request.user)
    if request.method == 'POST':
        caregiver.delete()
        messages.success(request, 'Caregiver removed successfully.')
    return redirect('caregiver_access')


def custom_logout(request):
    logout(request)
    return redirect('login')

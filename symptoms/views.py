from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import SymptomAssessmentForm
from .medicine_info import MedicineLookupError, lookup_medicine_information
from .models import DiseaseInformation, Symptom, SymptomAssessment
from .services import analyze_symptoms, get_assessment_conditions


MEDICAL_DISCLAIMER = (
    'This educational tool is not a diagnosis and cannot determine whether you have a '
    'condition. Symptoms can have many causes. It does not assess your personal medical '
    'history or confirm that you are safe. Contact a qualified healthcare professional '
    'for medical advice.'
)


@login_required
def symptom_checker(request):
    if request.method == 'POST':
        form = SymptomAssessmentForm(request.POST)
        if form.is_valid():
            symptoms = list(form.cleaned_data['symptoms'])
            summary = analyze_symptoms(symptoms)
            assessment = SymptomAssessment.objects.create(
                user=request.user,
                duration=form.cleaned_data['duration'],
                additional_notes=form.cleaned_data['additional_notes'],
                assessment_summary=summary,
            )
            assessment.symptoms.set(symptoms)
            messages.success(request, 'Your symptom assessment has been saved privately.')
            return redirect('symptoms:assessment_result', pk=assessment.pk)
    else:
        form = SymptomAssessmentForm()

    categories = (
        Symptom.objects.filter(is_active=True)
        .order_by()
        .values_list('category', flat=True)
        .distinct()
        .order_by('category')
    )
    category_groups = [
        {
            'name': category,
            'symptoms': Symptom.objects.filter(is_active=True, category=category),
        }
        for category in categories
    ]
    return render(request, 'symptoms/checker.html', {
        'form': form,
        'category_groups': category_groups,
        'selected_symptom_ids': request.POST.getlist('symptoms'),
        'disclaimer': MEDICAL_DISCLAIMER,
    })


@login_required
def assessment_result(request, pk):
    assessment = get_object_or_404(
        SymptomAssessment.objects.prefetch_related('symptoms'),
        pk=pk,
        user=request.user,
    )
    return render(request, 'symptoms/result.html', {
        'assessment': assessment,
        'conditions': get_assessment_conditions(assessment),
        'disclaimer': MEDICAL_DISCLAIMER,
    })


@login_required
def assessment_history(request):
    assessments = (
        SymptomAssessment.objects.filter(user=request.user)
        .prefetch_related('symptoms')
    )
    return render(request, 'symptoms/history.html', {'assessments': assessments})


@login_required
@require_POST
def delete_assessment(request, pk):
    assessment = get_object_or_404(SymptomAssessment, pk=pk, user=request.user)
    assessment.delete()
    messages.success(request, 'Symptom assessment deleted.')
    return redirect('symptoms:assessment_history')


@login_required
def disease_list(request):
    diseases = DiseaseInformation.objects.filter(is_active=True).prefetch_related('symptoms')
    return render(request, 'symptoms/disease_list.html', {'diseases': diseases})


@login_required
def disease_detail(request, pk):
    disease = get_object_or_404(
        DiseaseInformation.objects.prefetch_related('symptoms'),
        pk=pk,
        is_active=True,
    )
    return render(request, 'symptoms/disease_detail.html', {
        'disease': disease,
        'disclaimer': MEDICAL_DISCLAIMER,
    })


@login_required
def medicine_information(request):
    query = request.GET.get('q', '').strip()
    medicines = []
    lookup_error = ''
    if query:
        try:
            medicines = lookup_medicine_information(query)
        except ValueError as error:
            lookup_error = str(error)
        except MedicineLookupError as error:
            lookup_error = str(error)
    return render(request, 'symptoms/medicine_information.html', {
        'query': query,
        'medicines': medicines,
        'lookup_error': lookup_error,
        'disclaimer': (
            'Educational information only. This lookup does not determine whether a '
            'medicine is suitable for you and does not provide a treatment or dosage '
            'recommendation. Consult a doctor or pharmacist before making medicine decisions.'
        ),
    })

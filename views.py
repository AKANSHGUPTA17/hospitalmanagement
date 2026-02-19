from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.utils import timezone
from .models import Patient, PatientDocument, PatientVitals
from .forms import PatientForm, PatientDocumentForm, PatientVitalsForm, PatientDischargeForm


@login_required
def patient_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')

    patients = Patient.objects.all().select_related('created_by')

    if query:
        patients = patients.filter(
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(phone__icontains=query) |
            Q(patient_id__icontains=query)
        )

    if status_filter == 'admitted':
        patients = patients.filter(is_admitted=True)
    elif status_filter == 'discharged':
        patients = patients.filter(is_admitted=False)

    paginator = Paginator(patients, 20)
    page = request.GET.get('page')
    patients = paginator.get_page(page)

    return render(request, 'patients/patient_list.html', {
        'patients': patients,
        'query': query,
        'status_filter': status_filter,
        'total_patients': Patient.objects.count(),
        'admitted_count': Patient.objects.filter(is_admitted=True).count(),
    })


@login_required
def patient_create(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            messages.success(request, f'Patient {patient.full_name} (ID: {patient.patient_id}) registered successfully.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm()
    return render(request, 'patients/patient_form.html', {'form': form, 'title': 'Register New Patient'})


@login_required
def patient_detail(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    documents = patient.documents.all()
    vitals = patient.vitals.all()[:5]
    bills = patient.bills.all()
    appointments = patient.appointments.all().select_related('doctor')

    return render(request, 'patients/patient_detail.html', {
        'patient': patient,
        'documents': documents,
        'vitals': vitals,
        'bills': bills,
        'appointments': appointments,
        'doc_form': PatientDocumentForm(),
        'vitals_form': PatientVitalsForm(),
    })


@login_required
def patient_edit(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Patient information updated.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientForm(instance=patient)
    return render(request, 'patients/patient_form.html', {
        'form': form, 'patient': patient, 'title': 'Edit Patient'
    })


@login_required
def patient_discharge(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientDischargeForm(request.POST, instance=patient)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.is_admitted = False
            patient.discharge_datetime = timezone.now()
            patient.save()
            messages.success(request, f'Patient {patient.full_name} has been discharged.')
            return redirect('patients:patient_detail', pk=patient.pk)
    else:
        form = PatientDischargeForm(instance=patient)
    return render(request, 'patients/patient_discharge.html', {'form': form, 'patient': patient})


@login_required
def upload_document(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.patient = patient
            doc.uploaded_by = request.user
            doc.save()
            messages.success(request, 'Document uploaded successfully.')
    return redirect('patients:patient_detail', pk=pk)


@login_required
def delete_document(request, pk):
    doc = get_object_or_404(PatientDocument, pk=pk)
    patient_pk = doc.patient.pk
    doc.file.delete(save=False)
    doc.delete()
    messages.success(request, 'Document deleted.')
    return redirect('patients:patient_detail', pk=patient_pk)


@login_required
def add_vitals(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    if request.method == 'POST':
        form = PatientVitalsForm(request.POST)
        if form.is_valid():
            vitals = form.save(commit=False)
            vitals.patient = patient
            vitals.recorded_by = request.user
            vitals.save()
            messages.success(request, 'Vitals recorded.')
    return redirect('patients:patient_detail', pk=pk)


@login_required
def patient_history(request, pk):
    patient = get_object_or_404(Patient, pk=pk)
    vitals = patient.vitals.all()
    return render(request, 'patients/patient_history.html', {
        'patient': patient, 'vitals': vitals
    })


@login_required
def patient_search_ajax(request):
    query = request.GET.get('q', '')
    patients = Patient.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(phone__icontains=query) |
        Q(patient_id__icontains=query)
    )[:10]

    data = [{
        'id': p.pk,
        'patient_id': p.patient_id,
        'full_name': p.full_name,
        'phone': p.phone,
        'age': p.age,
        'gender': p.get_gender_display(),
    } for p in patients]
    return JsonResponse({'results': data})

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Appointment, DoctorSchedule
from .forms import AppointmentForm, DoctorScheduleForm
from apps.doctors.models import Doctor


@login_required
def appointment_list(request):
    appointments = Appointment.objects.all().select_related('patient', 'doctor')

    status_filter = request.GET.get('status', '')
    doctor_filter = request.GET.get('doctor', '')
    date_filter = request.GET.get('date', '')
    query = request.GET.get('q', '')

    if status_filter:
        appointments = appointments.filter(status=status_filter)
    if doctor_filter:
        appointments = appointments.filter(doctor_id=doctor_filter)
    if date_filter:
        appointments = appointments.filter(appointment_date=date_filter)
    if query:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query) |
            Q(appointment_id__icontains=query)
        )

    doctors = Doctor.objects.filter(is_active=True)
    today_appointments = Appointment.objects.filter(
        appointment_date=timezone.now().date()
    ).count()

    return render(request, 'appointments/appointment_list.html', {
        'appointments': appointments,
        'doctors': doctors,
        'status_filter': status_filter,
        'doctor_filter': doctor_filter,
        'date_filter': date_filter,
        'today_appointments': today_appointments,
    })


@login_required
def appointment_create(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            apt = form.save(commit=False)
            apt.booked_by = request.user
            apt.save()
            messages.success(request, f'Appointment {apt.appointment_id} booked successfully.')
            return redirect('appointments:appointment_list')
    else:
        form = AppointmentForm()
    return render(request, 'appointments/appointment_form.html', {
        'form': form, 'title': 'Book Appointment'
    })


@login_required
def appointment_detail(request, pk):
    apt = get_object_or_404(Appointment, pk=pk)
    return render(request, 'appointments/appointment_detail.html', {'appointment': apt})


@login_required
def appointment_update(request, pk):
    apt = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=apt)
        if form.is_valid():
            form.save()
            messages.success(request, 'Appointment updated.')
            return redirect('appointments:appointment_detail', pk=apt.pk)
    else:
        form = AppointmentForm(instance=apt)
    return render(request, 'appointments/appointment_form.html', {
        'form': form, 'appointment': apt, 'title': 'Edit Appointment'
    })


@login_required
def appointment_status_update(request, pk):
    apt = get_object_or_404(Appointment, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Appointment.STATUS_CHOICES):
            apt.status = new_status
            if new_status == 'completed':
                apt.diagnosis = request.POST.get('diagnosis', '')
                apt.prescription = request.POST.get('prescription', '')
            apt.save()
            messages.success(request, f'Appointment status updated to {new_status}.')
    return redirect('appointments:appointment_detail', pk=pk)


@login_required
def doctor_schedule(request, doctor_pk):
    doctor = get_object_or_404(Doctor, pk=doctor_pk)
    schedules = doctor.schedules.all()
    if request.method == 'POST':
        form = DoctorScheduleForm(request.POST)
        if form.is_valid():
            schedule = form.save(commit=False)
            schedule.doctor = doctor
            schedule.save()
            messages.success(request, 'Schedule added.')
    else:
        form = DoctorScheduleForm()
    return render(request, 'appointments/doctor_schedule.html', {
        'doctor': doctor, 'schedules': schedules, 'form': form
    })

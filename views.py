from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from django.utils import timezone
from datetime import date, timedelta
import json


@login_required
def index(request):
    return redirect('dashboard:dashboard')


@login_required
def dashboard(request):
    from apps.patients.models import Patient
    from apps.billing.models import Bill
    from apps.doctors.models import Doctor
    from apps.appointments.models import Appointment

    today = date.today()

    # Stats
    total_patients = Patient.objects.count()
    admitted_patients = Patient.objects.filter(is_admitted=True).count()
    new_patients_today = Patient.objects.filter(entry_datetime__date=today).count()
    discharged_today = Patient.objects.filter(discharge_datetime__date=today).count()

    today_revenue = Bill.objects.filter(
        bill_date__date=today, payment_status='paid'
    ).aggregate(total=Sum('paid_amount'))['total'] or 0

    month_revenue = Bill.objects.filter(
        bill_date__year=today.year,
        bill_date__month=today.month,
        payment_status='paid'
    ).aggregate(total=Sum('paid_amount'))['total'] or 0

    pending_bills_amount = Bill.objects.filter(
        Q(payment_status='pending') | Q(payment_status='partial')
    ).aggregate(total=Sum('due_amount'))['total'] or 0

    total_doctors = Doctor.objects.filter(is_active=True).count()

    today_appointments = Appointment.objects.filter(
        appointment_date=today
    ).select_related('patient', 'doctor').order_by('appointment_time')[:10]

    pending_appointments = Appointment.objects.filter(
        appointment_date=today, status__in=['pending', 'confirmed']
    ).count()

    # Recent patients
    recent_patients = Patient.objects.order_by('-created_at')[:5]

    # Revenue chart data - last 7 days
    revenue_labels = []
    revenue_data = []
    for i in range(6, -1, -1):
        day = today - timedelta(days=i)
        rev = Bill.objects.filter(
            bill_date__date=day, payment_status='paid'
        ).aggregate(total=Sum('paid_amount'))['total'] or 0
        revenue_labels.append(day.strftime('%d %b'))
        revenue_data.append(float(rev))

    # Patient gender distribution
    male_count = Patient.objects.filter(gender='M').count()
    female_count = Patient.objects.filter(gender='F').count()
    other_count = Patient.objects.filter(gender='O').count()

    # Doctor specialization data
    from apps.doctors.models import Specialization
    spec_data = Specialization.objects.annotate(
        doc_count=Count('doctors', filter=Q(doctors__is_active=True))
    ).filter(doc_count__gt=0)[:6]

    # Ayushman vs regular patients
    ayushman_patients = Patient.objects.filter(has_ayushman_card=True).count()
    regular_patients = total_patients - ayushman_patients

    context = {
        # Stats cards
        'total_patients': total_patients,
        'admitted_patients': admitted_patients,
        'new_patients_today': new_patients_today,
        'discharged_today': discharged_today,
        'today_revenue': today_revenue,
        'month_revenue': month_revenue,
        'pending_bills_amount': pending_bills_amount,
        'total_doctors': total_doctors,
        'pending_appointments': pending_appointments,

        # Data
        'today_appointments': today_appointments,
        'recent_patients': recent_patients,

        # Charts (JSON serialized)
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
        'gender_data': json.dumps([male_count, female_count, other_count]),
        'spec_labels': json.dumps([s.name for s in spec_data]),
        'spec_data': json.dumps([s.doc_count for s in spec_data]),
        'ayushman_data': json.dumps([ayushman_patients, regular_patients]),
    }
    return render(request, 'dashboard/dashboard.html', context)

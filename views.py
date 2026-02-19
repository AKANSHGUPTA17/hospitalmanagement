from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.utils import timezone
from django.db.models import Sum, Count, Q
from datetime import datetime, date, timedelta
from .models import Bill, BillItem, Payment
from .forms import BillForm, BillItemFormSet, PaymentForm
from apps.patients.models import Patient


@login_required
def bill_list(request):
    bills = Bill.objects.all().select_related('patient', 'doctor', 'created_by')

    status_filter = request.GET.get('status', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    query = request.GET.get('q', '')

    if status_filter:
        bills = bills.filter(payment_status=status_filter)
    if date_from:
        bills = bills.filter(bill_date__date__gte=date_from)
    if date_to:
        bills = bills.filter(bill_date__date__lte=date_to)
    if query:
        bills = bills.filter(
            Q(bill_number__icontains=query) |
            Q(patient__first_name__icontains=query) |
            Q(patient__last_name__icontains=query)
        )

    today = date.today()
    today_revenue = Bill.objects.filter(
        bill_date__date=today, payment_status='paid'
    ).aggregate(total=Sum('paid_amount'))['total'] or 0

    month_revenue = Bill.objects.filter(
        bill_date__year=today.year,
        bill_date__month=today.month,
        payment_status='paid'
    ).aggregate(total=Sum('paid_amount'))['total'] or 0

    return render(request, 'billing/bill_list.html', {
        'bills': bills,
        'today_revenue': today_revenue,
        'month_revenue': month_revenue,
        'status_filter': status_filter,
        'query': query,
    })


@login_required
def bill_create(request):
    patient_id = request.GET.get('patient_id')
    initial_patient = None
    if patient_id:
        try:
            initial_patient = Patient.objects.get(pk=patient_id)
        except Patient.DoesNotExist:
            pass

    if request.method == 'POST':
        form = BillForm(request.POST)
        if form.is_valid():
            bill = form.save(commit=False)
            bill.created_by = request.user
            if bill.payment_status == 'paid':
                bill.payment_date = timezone.now()
            bill.save()
            messages.success(request, f'Bill #{bill.bill_number} created successfully.')
            return redirect('billing:bill_detail', pk=bill.pk)
    else:
        initial = {}
        if initial_patient:
            initial['patient'] = initial_patient
            if initial_patient.has_ayushman_card:
                initial['is_ayushman'] = True
                initial['payment_method'] = 'ayushman'
        form = BillForm(initial=initial)

    return render(request, 'billing/bill_form.html', {
        'form': form, 'title': 'Create Bill', 'patient': initial_patient
    })


@login_required
def bill_detail(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    payments = bill.payments.all()
    return render(request, 'billing/bill_detail.html', {
        'bill': bill,
        'payments': payments,
        'payment_form': PaymentForm(),
    })


@login_required
def bill_edit(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        form = BillForm(request.POST, instance=bill)
        if form.is_valid():
            form.save()
            messages.success(request, 'Bill updated successfully.')
            return redirect('billing:bill_detail', pk=bill.pk)
    else:
        form = BillForm(instance=bill)
    return render(request, 'billing/bill_form.html', {'form': form, 'bill': bill, 'title': 'Edit Bill'})


@login_required
def add_payment(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.bill = bill
            payment.received_by = request.user
            payment.save()

            # Update bill paid amount
            total_paid = bill.payments.aggregate(total=Sum('amount'))['total'] or 0
            bill.paid_amount = total_paid
            if bill.paid_amount >= bill.total_amount:
                bill.payment_status = 'paid'
                bill.payment_date = timezone.now()
            elif bill.paid_amount > 0:
                bill.payment_status = 'partial'
            bill.save()

            messages.success(request, f'Payment of ₹{payment.amount} recorded.')
    return redirect('billing:bill_detail', pk=pk)


@login_required
def bill_pdf(request, pk):
    bill = get_object_or_404(Bill, pk=pk)
    # Generate PDF using reportlab
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from io import BytesIO

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    story = []

    # Header
    title_style = ParagraphStyle('Title', parent=styles['Title'], fontSize=20,
                                  spaceAfter=6, textColor=colors.HexColor('#1a237e'))
    story.append(Paragraph("🏥 City Hospital Management System", title_style))
    story.append(Paragraph("123 Medical Lane, Healthcare City, State - 400001 | Phone: +91-1234567890",
                           styles['Normal']))
    story.append(Spacer(1, 0.5*cm))

    # Bill header
    header_data = [
        ['INVOICE / RECEIPT', ''],
        ['Bill No:', bill.bill_number],
        ['Date:', bill.bill_date.strftime('%d-%m-%Y %H:%M')],
        ['Status:', bill.get_payment_status_display()],
    ]
    header_table = Table(header_data, colWidths=[4*cm, 8*cm])
    header_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 14),
        ('SPAN', (0, 0), (1, 0)),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(header_table)
    story.append(Spacer(1, 0.5*cm))

    # Patient info
    patient = bill.patient
    patient_data = [
        ['PATIENT INFORMATION', ''],
        ['Patient ID:', patient.patient_id],
        ['Name:', patient.full_name],
        ['Age / Gender:', f"{patient.age} yrs / {patient.get_gender_display()}"],
        ['Phone:', patient.phone],
        ['Address:', patient.address],
    ]
    if patient.has_ayushman_card:
        patient_data.append(['Ayushman Card No:', patient.ayushman_card_number])

    patient_table = Table(patient_data, colWidths=[5*cm, 12*cm])
    patient_table.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('SPAN', (0, 0), (1, 0)),
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e3f2fd')),
        ('FONTNAME', (0, 1), (0, -1), 'Helvetica-Bold'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 6),
    ]))
    story.append(patient_table)
    story.append(Spacer(1, 0.5*cm))

    # Charges
    charges_data = [['Description', 'Amount (₹)']]
    charge_fields = [
        ('Consultation Fee', bill.consultation_fee),
        ('Entry / Registration Fee', bill.entry_fee),
        ('Room Charges', bill.room_charges),
        ('Medicine Charges', bill.medicine_charges),
        ('Lab / Test Charges', bill.lab_charges),
        ('Other Charges', bill.other_charges),
    ]
    for label, amount in charge_fields:
        if amount > 0:
            charges_data.append([label, f'{amount:,.2f}'])

    charges_data.extend([
        ['Subtotal', f'{bill.subtotal:,.2f}'],
        ['Discount', f'- {bill.discount:,.2f}'],
        ['Tax', f'{bill.tax:,.2f}'],
        ['TOTAL', f'{bill.total_amount:,.2f}'],
        ['Paid Amount', f'{bill.paid_amount:,.2f}'],
        ['Balance Due', f'{bill.due_amount:,.2f}'],
    ])

    charges_table = Table(charges_data, colWidths=[12*cm, 5*cm])
    charges_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1a237e')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('FONTNAME', (0, -3), (-1, -1), 'Helvetica-Bold'),
        ('BACKGROUND', (0, -3), (-1, -3), colors.HexColor('#fff9c4')),
        ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#ffebee')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(charges_table)
    story.append(Spacer(1, 1*cm))

    story.append(Paragraph(
        f"Payment Method: {bill.get_payment_method_display()} | "
        f"Status: {bill.get_payment_status_display()}",
        styles['Normal']
    ))
    story.append(Spacer(1, 0.5*cm))
    story.append(Paragraph("Thank you for choosing our hospital. Wishing you a speedy recovery!",
                           styles['Italic']))
    story.append(Spacer(1, 1*cm))
    story.append(Paragraph("_________________________", styles['Normal']))
    story.append(Paragraph("Authorized Signature", styles['Normal']))

    doc.build(story)
    pdf = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="bill_{bill.bill_number}.pdf"'
    return response


@login_required
def revenue_report(request):
    report_type = request.GET.get('type', 'daily')
    today = date.today()

    if report_type == 'daily':
        # Last 30 days
        days = [(today - timedelta(days=i)) for i in range(29, -1, -1)]
        data = []
        for day in days:
            revenue = Bill.objects.filter(
                bill_date__date=day, payment_status='paid'
            ).aggregate(total=Sum('paid_amount'))['total'] or 0
            count = Bill.objects.filter(bill_date__date=day).count()
            data.append({'date': day.strftime('%d %b'), 'revenue': float(revenue), 'count': count})
    else:
        # Last 12 months
        data = []
        for i in range(11, -1, -1):
            from calendar import monthrange
            if today.month - i > 0:
                month = today.month - i
                year = today.year
            else:
                month = today.month - i + 12
                year = today.year - 1
            revenue = Bill.objects.filter(
                bill_date__year=year, bill_date__month=month, payment_status='paid'
            ).aggregate(total=Sum('paid_amount'))['total'] or 0
            from datetime import date as d
            data.append({
                'date': d(year, month, 1).strftime('%b %Y'),
                'revenue': float(revenue)
            })

    total_revenue = sum(d['revenue'] for d in data)
    pending_amount = Bill.objects.filter(payment_status='pending').aggregate(
        total=Sum('total_amount'))['total'] or 0
    ayushman_revenue = Bill.objects.filter(
        is_ayushman=True, payment_status='paid'
    ).aggregate(total=Sum('ayushman_claim_amount'))['total'] or 0

    return render(request, 'billing/revenue_report.html', {
        'data': data,
        'total_revenue': total_revenue,
        'pending_amount': pending_amount,
        'ayushman_revenue': ayushman_revenue,
        'report_type': report_type,
    })

from django.db import models
from django.utils import timezone


class Bill(models.Model):
    PAYMENT_STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('partial', 'Partial'),
        ('waived', 'Waived'),
    ]
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('ayushman', 'Ayushman Scheme'),
        ('insurance', 'Insurance'),
        ('cheque', 'Cheque'),
    ]

    bill_number = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey('patients.Patient', on_delete=models.CASCADE, related_name='bills')
    doctor = models.ForeignKey(
        'doctors.Doctor', on_delete=models.SET_NULL,
        null=True, blank=True, related_name='bills'
    )

    # Charges
    consultation_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    entry_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    room_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    medicine_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    lab_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    other_charges = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tax = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    # Totals
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    paid_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    due_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    # Ayushman
    is_ayushman = models.BooleanField(default=False)
    ayushman_claim_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default='cash')
    payment_date = models.DateTimeField(null=True, blank=True)

    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL, null=True
    )
    bill_date = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'bills'
        ordering = ['-bill_date']

    def __str__(self):
        return f"Bill #{self.bill_number} - {self.patient.full_name}"

    def save(self, *args, **kwargs):
        if not self.bill_number:
            from datetime import date
            today = date.today()
            prefix = f"INV{today.year}{today.month:02d}"
            count = Bill.objects.filter(bill_number__startswith=prefix).count()
            self.bill_number = f"{prefix}{count + 1:04d}"

        self.subtotal = (
            self.consultation_fee + self.entry_fee + self.room_charges +
            self.medicine_charges + self.lab_charges + self.other_charges
        )
        self.total_amount = self.subtotal - self.discount + self.tax
        self.due_amount = self.total_amount - self.paid_amount - self.ayushman_claim_amount
        super().save(*args, **kwargs)


class BillItem(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='items')
    description = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=8, decimal_places=2, default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        db_table = 'bill_items'

    def save(self, *args, **kwargs):
        self.total = self.quantity * self.unit_price
        super().save(*args, **kwargs)

    def __str__(self):
        return self.description


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('cash', 'Cash'), ('card', 'Card'), ('upi', 'UPI'),
        ('netbanking', 'Net Banking'), ('ayushman', 'Ayushman'),
        ('insurance', 'Insurance'), ('cheque', 'Cheque'),
    ]

    bill = models.ForeignKey(Bill, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(default=timezone.now)
    received_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL, null=True
    )
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'payments'
        ordering = ['-payment_date']

    def __str__(self):
        return f"Payment of ₹{self.amount} for {self.bill.bill_number}"

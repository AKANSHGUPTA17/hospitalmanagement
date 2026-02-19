from django.db import models
from django.utils import timezone
import uuid


def patient_document_path(instance, filename):
    return f'documents/patient_{instance.patient.patient_id}/{filename}'


class Patient(models.Model):
    GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
    BLOOD_GROUP_CHOICES = [
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-'),
    ]

    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    blood_group = models.CharField(max_length=3, choices=BLOOD_GROUP_CHOICES, blank=True)
    phone = models.CharField(max_length=15)
    alternate_phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField()
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    pincode = models.CharField(max_length=10, blank=True)

    # Ayushman Card
    has_ayushman_card = models.BooleanField(default=False, verbose_name='Ayushman Card')
    ayushman_card_number = models.CharField(max_length=50, blank=True)

    # Emergency contact
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)

    # Timestamps
    entry_datetime = models.DateTimeField(default=timezone.now)
    discharge_datetime = models.DateTimeField(null=True, blank=True)
    is_admitted = models.BooleanField(default=True)

    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL,
        null=True, related_name='patients_created'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'patients'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.patient_id} - {self.full_name}"

    def save(self, *args, **kwargs):
        if not self.patient_id:
            self.patient_id = self.generate_patient_id()
        super().save(*args, **kwargs)

    def generate_patient_id(self):
        from datetime import date
        today = date.today()
        prefix = f"P{today.year}{today.month:02d}"
        last = Patient.objects.filter(patient_id__startswith=prefix).count()
        return f"{prefix}{last + 1:04d}"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def age_display(self):
        return f"{self.age} yrs"

    @property
    def status(self):
        return "Admitted" if self.is_admitted else "Discharged"


class PatientDocument(models.Model):
    DOC_TYPE_CHOICES = [
        ('prescription', 'Prescription'),
        ('lab_report', 'Lab Report'),
        ('xray', 'X-Ray'),
        ('scan', 'Scan/MRI'),
        ('insurance', 'Insurance'),
        ('ayushman', 'Ayushman Card'),
        ('other', 'Other'),
    ]

    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='documents')
    document_type = models.CharField(max_length=20, choices=DOC_TYPE_CHOICES, default='other')
    title = models.CharField(max_length=200)
    file = models.FileField(upload_to=patient_document_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    uploaded_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL, null=True
    )

    class Meta:
        db_table = 'patient_documents'
        ordering = ['-uploaded_at']

    def __str__(self):
        return f"{self.patient.full_name} - {self.title}"


class PatientVitals(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='vitals')
    recorded_by = models.ForeignKey(
        'authentication.User', on_delete=models.SET_NULL, null=True
    )
    blood_pressure = models.CharField(max_length=20, blank=True)
    pulse_rate = models.CharField(max_length=10, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    height = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    oxygen_saturation = models.CharField(max_length=10, blank=True)
    notes = models.TextField(blank=True)
    recorded_at = models.DateTimeField(default=timezone.now)

    class Meta:
        db_table = 'patient_vitals'
        ordering = ['-recorded_at']

    def __str__(self):
        return f"{self.patient.full_name} vitals at {self.recorded_at}"

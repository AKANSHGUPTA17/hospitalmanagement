"""
Management command to populate the database with sample test data.
Usage: python manage.py populate_sample_data
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.hashers import make_password
from django.utils import timezone
from datetime import date, time, timedelta
import random


class Command(BaseCommand):
    help = 'Populate database with sample test data'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')

        # Import models
        from apps.authentication.models import User
        from apps.doctors.models import Doctor, Specialization, SalaryPayment
        from apps.patients.models import Patient
        from apps.appointments.models import Appointment, DoctorSchedule
        from apps.billing.models import Bill, Payment

        # ==== Users ====
        admin, _ = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@hospital.com',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
                'password': make_password('admin123'),
            }
        )

        receptionist, _ = User.objects.get_or_create(
            username='reception1',
            defaults={
                'email': 'reception@hospital.com',
                'first_name': 'Priya',
                'last_name': 'Sharma',
                'role': 'receptionist',
                'phone': '9876543210',
                'password': make_password('recept123'),
            }
        )

        doc_user, _ = User.objects.get_or_create(
            username='dr_smith',
            defaults={
                'email': 'dr.smith@hospital.com',
                'first_name': 'Rajesh',
                'last_name': 'Smith',
                'role': 'doctor',
                'phone': '9123456789',
                'password': make_password('doctor123'),
            }
        )

        self.stdout.write(self.style.SUCCESS('✓ Users created'))

        # ==== Specializations ====
        specs_data = [
            'General Medicine', 'Cardiology', 'Orthopedics',
            'Gynecology', 'Pediatrics', 'ENT', 'Neurology', 'Dermatology'
        ]
        specs = {}
        for s in specs_data:
            spec, _ = Specialization.objects.get_or_create(name=s)
            specs[s] = spec

        self.stdout.write(self.style.SUCCESS('✓ Specializations created'))

        # ==== Doctors ====
        doctors_data = [
            ('Rajesh', 'Smith', 'General Medicine', 'MBBS', 10, '9123456789', 500, 80000, doc_user),
            ('Priya', 'Kumar', 'Cardiology', 'MD', 15, '9234567890', 800, 120000, None),
            ('Anil', 'Verma', 'Orthopedics', 'MS', 12, '9345678901', 700, 110000, None),
            ('Sunita', 'Patel', 'Gynecology', 'MD', 8, '9456789012', 600, 95000, None),
            ('Vikram', 'Mehta', 'Pediatrics', 'MBBS', 6, '9567890123', 400, 70000, None),
        ]

        doctors = []
        for fn, ln, spec_name, qual, exp, phone, fee, salary, user_obj in doctors_data:
            doc, _ = Doctor.objects.get_or_create(
                first_name=fn, last_name=ln,
                defaults={
                    'specialization': specs[spec_name],
                    'qualification': qual,
                    'experience_years': exp,
                    'phone': phone,
                    'consultation_fee': fee,
                    'monthly_salary': salary,
                    'user': user_obj,
                    'joining_date': date.today() - timedelta(days=exp * 365),
                    'available_days': 'Mon,Tue,Wed,Thu,Fri',
                    'consultation_start': time(9, 0),
                    'consultation_end': time(17, 0),
                }
            )
            doctors.append(doc)

            # Doctor schedules
            for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
                DoctorSchedule.objects.get_or_create(
                    doctor=doc, day_of_week=day,
                    defaults={'start_time': time(9, 0), 'end_time': time(17, 0), 'max_appointments': 20}
                )

        self.stdout.write(self.style.SUCCESS('✓ Doctors created'))

        # ==== Patients ====
        patients_data = [
            ('Ramesh', 'Gupta', 45, 'M', '9811111111', 'Agra, UP', False, ''),
            ('Sunita', 'Devi', 32, 'F', '9822222222', 'Mathura, UP', True, 'AY001234567'),
            ('Mohan', 'Lal', 67, 'M', '9833333333', 'Firozabad, UP', True, 'AY007654321'),
            ('Pooja', 'Singh', 28, 'F', '9844444444', 'Gwalior, MP', False, ''),
            ('Arun', 'Sharma', 55, 'M', '9855555555', 'Kanpur, UP', False, ''),
            ('Deepika', 'Yadav', 38, 'F', '9866666666', 'Aligarh, UP', True, 'AY009876543'),
            ('Suresh', 'Mishra', 42, 'M', '9877777777', 'Bareilly, UP', False, ''),
            ('Anjali', 'Kumari', 25, 'F', '9888888888', 'Lucknow, UP', False, ''),
        ]

        patients = []
        for fn, ln, age, gender, phone, addr, ayushman, card_no in patients_data:
            p, created = Patient.objects.get_or_create(
                phone=phone,
                defaults={
                    'first_name': fn,
                    'last_name': ln,
                    'age': age,
                    'gender': gender,
                    'address': addr,
                    'has_ayushman_card': ayushman,
                    'ayushman_card_number': card_no,
                    'city': addr.split(',')[0].strip() if ',' in addr else addr,
                    'state': addr.split(',')[1].strip() if ',' in addr else 'UP',
                    'entry_datetime': timezone.now() - timedelta(days=random.randint(0, 30)),
                    'is_admitted': random.choice([True, True, False]),
                    'blood_group': random.choice(['A+', 'B+', 'O+', 'AB+']),
                    'created_by': receptionist,
                }
            )
            patients.append(p)

        # Discharge some
        for p in patients[5:]:
            if not p.is_admitted:
                p.discharge_datetime = timezone.now() - timedelta(days=random.randint(1, 10))
                p.save()

        self.stdout.write(self.style.SUCCESS('✓ Patients created'))

        # ==== Bills ====
        for i, patient in enumerate(patients[:6]):
            doc = doctors[i % len(doctors)]
            bill, created = Bill.objects.get_or_create(
                patient=patient,
                defaults={
                    'doctor': doc,
                    'consultation_fee': doc.consultation_fee,
                    'entry_fee': 200,
                    'room_charges': random.choice([0, 1500, 3000]),
                    'medicine_charges': random.choice([0, 500, 1200]),
                    'lab_charges': random.choice([0, 800, 1500]),
                    'paid_amount': 0,
                    'is_ayushman': patient.has_ayushman_card,
                    'ayushman_claim_amount': 5000 if patient.has_ayushman_card else 0,
                    'payment_method': 'ayushman' if patient.has_ayushman_card else 'cash',
                    'payment_status': random.choice(['paid', 'paid', 'pending', 'partial']),
                    'bill_date': timezone.now() - timedelta(days=random.randint(0, 15)),
                    'created_by': receptionist,
                }
            )
            if created:
                # Set paid amount based on status
                if bill.payment_status == 'paid':
                    bill.paid_amount = bill.total_amount
                elif bill.payment_status == 'partial':
                    bill.paid_amount = bill.total_amount * 0.5
                bill.save()

        self.stdout.write(self.style.SUCCESS('✓ Bills created'))

        # ==== Appointments ====
        today = date.today()
        apt_statuses = ['pending', 'confirmed', 'completed', 'completed', 'cancelled']
        for i in range(10):
            patient = patients[i % len(patients)]
            doc = doctors[i % len(doctors)]
            apt_date = today + timedelta(days=random.randint(-5, 5))
            Appointment.objects.get_or_create(
                patient=patient,
                doctor=doc,
                appointment_date=apt_date,
                defaults={
                    'appointment_time': time(9 + (i % 8), 0),
                    'appointment_type': random.choice(['consultation', 'follow_up']),
                    'status': random.choice(apt_statuses),
                    'reason': 'General checkup',
                    'booked_by': receptionist,
                }
            )

        self.stdout.write(self.style.SUCCESS('✓ Appointments created'))

        # ==== Salary Payments ====
        this_month = date.today().replace(day=1)
        for doc in doctors[:3]:
            SalaryPayment.objects.get_or_create(
                doctor=doc,
                month=this_month,
                defaults={
                    'base_salary': doc.monthly_salary,
                    'bonus': random.choice([0, 5000, 10000]),
                    'deductions': random.choice([0, 2000]),
                    'payment_method': 'bank_transfer',
                    'status': 'paid',
                    'payment_date': today,
                    'paid_by': admin,
                }
            )

        self.stdout.write(self.style.SUCCESS('✓ Salary payments created'))

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('=' * 50))
        self.stdout.write(self.style.SUCCESS('✅ Sample data populated successfully!'))
        self.stdout.write('')
        self.stdout.write('Login credentials:')
        self.stdout.write('  Admin:       admin / admin123')
        self.stdout.write('  Doctor:      dr_smith / doctor123')
        self.stdout.write('  Receptionist: reception1 / recept123')
        self.stdout.write(self.style.SUCCESS('=' * 50))

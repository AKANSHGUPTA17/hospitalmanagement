# 🏥 Hospital Management System (HMS)

**Production-ready Hospital Management System built with Django, Bootstrap 5, MySQL, and REST APIs.**

---

## 📋 Table of Contents

1. [Project Structure](#project-structure)
2. [Features](#features)
3. [Tech Stack](#tech-stack)
4. [Database Schema](#database-schema)
5. [Setup Guide](#setup-guide)
6. [API Endpoints](#api-endpoints)
7. [User Roles](#user-roles)
8. [Sample Test Data](#sample-test-data)
9. [Production Deployment](#production-deployment)

---

## 📁 Project Structure

```
hospital_management/
├── hospital_mgmt/              # Core Django project
│   ├── settings.py             # All settings (DB, auth, apps, etc.)
│   ├── urls.py                 # Root URL routing
│   └── wsgi.py
├── apps/
│   ├── authentication/         # User management, login, roles
│   │   ├── models.py           # Custom User model
│   │   ├── views.py            # Login, logout, user CRUD
│   │   ├── forms.py
│   │   ├── decorators.py       # @admin_required, @doctor_required, etc.
│   │   ├── serializers.py      # DRF serializers
│   │   ├── api_views.py        # REST API views
│   │   ├── urls.py             # Web URLs
│   │   └── api_urls.py         # API URLs
│   ├── patients/               # Patient management module
│   │   ├── models.py           # Patient, PatientDocument, PatientVitals
│   │   ├── views.py            # Patient CRUD, discharge, upload docs
│   │   ├── forms.py
│   │   ├── api_views.py
│   │   ├── urls.py
│   │   └── api_urls.py
│   ├── billing/                # Fee & billing management
│   │   ├── models.py           # Bill, BillItem, Payment
│   │   ├── views.py            # Bill CRUD, PDF generation, revenue reports
│   │   ├── forms.py
│   │   ├── api_views.py
│   │   ├── urls.py
│   │   └── api_urls.py
│   ├── doctors/                # Doctor management
│   │   ├── models.py           # Doctor, Specialization, SalaryPayment
│   │   ├── views.py            # Doctor CRUD, salary management
│   │   ├── forms.py
│   │   ├── api_views.py
│   │   ├── urls.py
│   │   └── api_urls.py
│   ├── appointments/           # Appointment scheduling
│   │   ├── models.py           # Appointment, DoctorSchedule
│   │   ├── views.py            # Appointment booking, status updates
│   │   ├── forms.py
│   │   ├── api_views.py
│   │   ├── urls.py
│   │   └── api_urls.py
│   └── dashboard/              # Admin dashboard
│       ├── views.py            # Stats, charts, recent data
│       ├── urls.py
│       └── management/commands/
│           └── populate_sample_data.py
├── templates/                  # All HTML templates
│   ├── base.html               # Master layout with sidebar
│   ├── auth/
│   ├── patients/
│   ├── billing/
│   ├── doctors/
│   ├── appointments/
│   └── dashboard/
├── static/
│   ├── css/main.css            # Custom styles
│   └── js/main.js              # Sidebar, bill calc, autocomplete
├── media/                      # Uploaded files
├── logs/                       # Application logs
├── requirements.txt
├── manage.py
└── README.md
```

---

## ✨ Features

### 🔐 Authentication & Role-Based Access
- Custom User model with roles: **Admin, Doctor, Receptionist**
- Secure hashed passwords via Django's `make_password`
- Role-based decorators: `@admin_required`, `@doctor_required`, `@staff_required`
- Session-based auth + Token auth for REST APIs
- Role-specific dashboards and menu items

### 🏥 Patient Management
- Unique **Patient ID** auto-generated (e.g. `P20240100001`)
- Full patient profile: Name, Age, Gender, Blood Group, Phone, Address
- Auto-captured **entry date/time**
- **Discharge** workflow with discharge summary
- **Ayushman Bharat Card** toggle + card number field
- Document upload (prescriptions, reports, X-rays, etc.)
- Vitals recording (BP, Pulse, Temp, SpO2, Weight, Height)
- Search by name, phone, or patient ID
- Full history view

### 💰 Billing & Payments
- Itemized bills: Consultation, Entry, Room, Medicine, Lab, Other charges
- Discount and Tax support
- **Ayushman scheme billing** with claim amount tracking
- Multiple payment methods: Cash, Card, UPI, Net Banking, Ayushman, Cheque
- Payment status: Paid / Pending / Partial / Waived
- **PDF receipt generation** using ReportLab
- Payment recording with installment support
- Daily and monthly revenue reports with Chart.js graphs

### 👨‍⚕️ Doctor Management
- Doctor profiles with specialization, qualification, experience
- Doctor schedule management (days, timings)
- Consultation fee configuration
- **Salary management** with bonus/deduction support
- Monthly salary payment records
- Doctor-wise patient list
- Salary summary for admin

### 📅 Appointment Management
- Book appointments with patient + doctor + date/time
- Appointment types: Consultation, Follow-up, Emergency, Procedure
- Status tracking: Pending → Confirmed → Completed / Cancelled
- Diagnosis and prescription recording
- Doctor availability schedule
- Today's appointments on dashboard

### 📊 Admin Dashboard
- Live stats: Total patients, admitted, new today, discharged
- Revenue: Today's and monthly totals
- Pending bills amount
- Charts: Revenue (7-day bar), Gender distribution, Ayushman coverage
- Today's appointments list
- Recent patient registrations
- Doctor and salary summaries

### 🔌 REST API
- Full CRUD APIs for all modules
- Token-based authentication
- Pagination support
- JSON responses
- Revenue report APIs

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Backend | Python 3.10+, Django 4.2 |
| Frontend | HTML5, CSS3, Bootstrap 5.3, JavaScript |
| Icons | Bootstrap Icons 1.11 |
| Charts | Chart.js 4.4 |
| Database | MySQL 8.0 (with SQLite fallback) |
| PDF | ReportLab |
| REST API | Django REST Framework |
| File Serving | WhiteNoise (static), Django Media (uploads) |

---

## 🗄️ Database Schema

### `users` (Custom User)
```sql
id, username, password, email, first_name, last_name,
role ENUM('admin', 'doctor', 'receptionist'),
phone, profile_picture, is_active, created_at, updated_at
```

### `patients`
```sql
id, patient_id (UNIQUE, auto-generated), first_name, last_name,
age, date_of_birth, gender, blood_group, phone, alternate_phone,
email, address, city, state, pincode,
has_ayushman_card, ayushman_card_number,
emergency_contact_name, emergency_contact_phone, emergency_contact_relation,
entry_datetime, discharge_datetime, is_admitted,
notes, created_by_id, created_at, updated_at
```

### `patient_documents`
```sql
id, patient_id, document_type, title, file, uploaded_at, uploaded_by_id
```

### `patient_vitals`
```sql
id, patient_id, blood_pressure, pulse_rate, temperature, weight,
height, oxygen_saturation, notes, recorded_by_id, recorded_at
```

### `specializations`
```sql
id, name, description
```

### `doctors`
```sql
id, user_id, doctor_id (UNIQUE), first_name, last_name,
specialization_id, qualification, experience_years,
phone, email, registration_number, photo,
available_days, consultation_start, consultation_end, consultation_fee,
monthly_salary, joining_date, is_active, notes, created_at, updated_at
```

### `salary_payments`
```sql
id, doctor_id, month, base_salary, bonus, deductions, net_salary,
payment_method, status, payment_date, remarks, paid_by_id, created_at
UNIQUE(doctor_id, month)
```

### `bills`
```sql
id, bill_number (UNIQUE), patient_id, doctor_id,
consultation_fee, entry_fee, room_charges, medicine_charges,
lab_charges, other_charges, discount, tax,
subtotal, total_amount, paid_amount, due_amount,
is_ayushman, ayushman_claim_amount,
payment_status ENUM('paid','pending','partial','waived'),
payment_method, payment_date, notes, created_by_id, bill_date, created_at
```

### `payments`
```sql
id, bill_id, amount, payment_method, transaction_id,
payment_date, received_by_id, notes
```

### `appointments`
```sql
id, appointment_id (UNIQUE), patient_id, doctor_id,
appointment_date, appointment_time, appointment_type, status,
reason, notes, diagnosis, prescription,
booked_by_id, created_at, updated_at
```

### `doctor_schedules`
```sql
id, doctor_id, day_of_week, start_time, end_time,
max_appointments, is_available
UNIQUE(doctor_id, day_of_week)
```

---

## 🚀 Setup Guide

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- pip

### Step 1: Clone / Extract the project
```bash
cd hospital_management
```

### Step 2: Create and activate virtual environment
```bash
python -m venv venv

# Linux/Mac:
source venv/bin/activate

# Windows:
venv\Scripts\activate
```

### Step 3: Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Configure MySQL Database
```sql
-- Run in MySQL client
CREATE DATABASE hospital_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'hospital_user'@'localhost' IDENTIFIED BY 'SecurePass@123';
GRANT ALL PRIVILEGES ON hospital_db.* TO 'hospital_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 5: Update database settings
In `hospital_mgmt/settings.py`, update:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'hospital_db',
        'USER': 'hospital_user',
        'PASSWORD': 'SecurePass@123',
        'HOST': 'localhost',
        'PORT': '3306',
    }
}
```

Or use **SQLite for quick dev** — comment out MySQL block and uncomment:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### Step 6: Run Migrations
```bash
python manage.py makemigrations authentication patients billing doctors appointments dashboard
python manage.py migrate
```

### Step 7: Populate Sample Data
```bash
python manage.py populate_sample_data
```

### Step 8: Collect Static Files
```bash
python manage.py collectstatic --no-input
```

### Step 9: Start the Server
```bash
python manage.py runserver
```

Visit: **http://localhost:8000**  
Login at: **http://localhost:8000/auth/login/**

---

## 🔑 Default Login Credentials

| Role | Username | Password |
|------|----------|---------|
| Admin | `admin` | `admin123` |
| Doctor | `dr_smith` | `doctor123` |
| Receptionist | `reception1` | `recept123` |

---

## 🔌 API Endpoints

### Authentication
```
POST   /api/v1/auth/token/         — Get auth token (username + password)
GET    /api/v1/auth/me/            — Current user info
GET    /api/v1/auth/users/         — List all users (admin only)
```

### Patients
```
GET    /api/v1/patients/           — List all patients (with ?q= search)
POST   /api/v1/patients/           — Create patient
GET    /api/v1/patients/{id}/      — Patient details
PUT    /api/v1/patients/{id}/      — Update patient
GET    /api/v1/patients/search/    — Search patients
GET    /api/v1/patients/{id}/vitals/ — Patient vitals
POST   /api/v1/patients/{id}/vitals/ — Add vitals
```

### Billing
```
GET    /api/v1/billing/            — List bills
POST   /api/v1/billing/            — Create bill
GET    /api/v1/billing/{id}/       — Bill details
POST   /api/v1/billing/{id}/payments/ — Add payment
GET    /api/v1/billing/reports/daily/   — Daily revenue (30 days)
GET    /api/v1/billing/reports/monthly/ — Monthly revenue (12 months)
```

### Doctors
```
GET    /api/v1/doctors/            — List doctors
POST   /api/v1/doctors/            — Add doctor
GET    /api/v1/doctors/{id}/       — Doctor details
GET    /api/v1/doctors/{id}/salary/ — Salary history
POST   /api/v1/doctors/{id}/salary/ — Add salary payment
GET    /api/v1/doctors/specializations/ — List specializations
```

### Appointments
```
GET    /api/v1/appointments/       — List appointments
POST   /api/v1/appointments/       — Book appointment
GET    /api/v1/appointments/{id}/  — Appointment details
PUT    /api/v1/appointments/{id}/  — Update appointment
```

#### Example API Usage:
```bash
# Get auth token
curl -X POST http://localhost:8000/api/v1/auth/token/ \
  -d "username=admin&password=admin123"

# Search patients
curl http://localhost:8000/api/v1/patients/search/?q=Ramesh \
  -H "Authorization: Token <your-token>"

# Get daily revenue
curl http://localhost:8000/api/v1/billing/reports/daily/ \
  -H "Authorization: Token <your-token>"
```

---

## 👥 User Roles & Permissions

| Feature | Admin | Doctor | Receptionist |
|---------|-------|--------|-------------|
| Dashboard | ✅ Full | ✅ Limited | ✅ Limited |
| Add/Edit Patients | ✅ | ❌ | ✅ |
| View Patients | ✅ | ✅ | ✅ |
| Upload Documents | ✅ | ✅ | ✅ |
| Record Vitals | ✅ | ✅ | ✅ |
| Create Bills | ✅ | ❌ | ✅ |
| Manage Doctors | ✅ | ❌ | ❌ |
| Manage Salaries | ✅ | ❌ | ❌ |
| User Management | ✅ | ❌ | ❌ |
| Revenue Reports | ✅ | ❌ | ✅ |
| Book Appointments | ✅ | ✅ | ✅ |
| Update Apt Status | ✅ | ✅ | ✅ |

---

## 🏭 Production Deployment

### Environment Variables (recommended)
Create a `.env` file:
```
SECRET_KEY=your-super-secret-key-here
DEBUG=False
DB_NAME=hospital_db
DB_USER=hospital_user
DB_PASSWORD=SecurePass@123
DB_HOST=localhost
DB_PORT=3306
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
```

Update `settings.py` to use `python-decouple`:
```python
from decouple import config
SECRET_KEY = config('SECRET_KEY')
DEBUG = config('DEBUG', default=False, cast=bool)
```

### With Gunicorn + Nginx
```bash
# Install gunicorn (already in requirements.txt)
gunicorn hospital_mgmt.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --timeout 120

# Nginx config (example)
server {
    listen 80;
    server_name yourdomain.com;
    
    location /static/ { root /var/www/hospital; }
    location /media/ { root /var/www/hospital; }
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Security Checklist for Production
- [ ] Set `DEBUG = False`
- [ ] Set strong `SECRET_KEY`
- [ ] Set `ALLOWED_HOSTS` to your domain
- [ ] Use HTTPS (SSL certificate)
- [ ] Configure proper database password
- [ ] Set up database backups
- [ ] Configure email for error notifications
- [ ] Run `python manage.py check --deploy`

---

## 📦 Sample Test Data

After running `python manage.py populate_sample_data`, you'll have:

- **3 Users**: Admin, Doctor (dr_smith), Receptionist
- **8 Specializations**: General Medicine, Cardiology, Orthopedics, etc.
- **5 Doctors**: With specializations, schedules, and salary records
- **8 Patients**: Mix of admitted/discharged, some with Ayushman cards
- **6 Bills**: With various payment statuses
- **10 Appointments**: Across various dates and statuses
- **3 Salary Payments**: For the current month

---

## 🎨 UI Features

- **Responsive sidebar navigation** with collapse support
- **Role-based menu** (Admin sees all, Doctor sees limited)
- **Color-coded status badges** (Admitted=Green, Discharged=Grey, etc.)
- **Ayushman card visual indicator** throughout the app
- **Interactive charts** on dashboard (Bar, Doughnut)
- **PDF bill generation** with hospital letterhead
- **Auto-dismiss alerts** (5 seconds)
- **Bill total calculator** (live JS calculation)
- **Patient ID search autocomplete** (AJAX)
- **Print support** (navbar and buttons hidden on print)

---

*Built for Indian hospital management with full Ayushman Bharat / PMJAY support.*

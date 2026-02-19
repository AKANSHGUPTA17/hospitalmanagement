from django import forms
from .models import Patient, PatientDocument, PatientVitals


class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        exclude = ['patient_id', 'created_by', 'created_at', 'updated_at',
                   'entry_datetime', 'discharge_datetime', 'is_admitted']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'min': 0, 'max': 150}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10-digit mobile number'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control'}),
            'has_ayushman_card': forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'hasAyushman'}),
            'ayushman_card_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ayushman Card Number',
                'id': 'ayushmanNumber'
            }),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'form-control'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': 'form-control'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def clean(self):
        cleaned_data = super().clean()
        has_ayushman = cleaned_data.get('has_ayushman_card')
        ayushman_number = cleaned_data.get('ayushman_card_number')
        if has_ayushman and not ayushman_number:
            raise forms.ValidationError('Please enter the Ayushman Card number.')
        return cleaned_data


class PatientDocumentForm(forms.ModelForm):
    class Meta:
        model = PatientDocument
        fields = ['document_type', 'title', 'file']
        widgets = {
            'document_type': forms.Select(attrs={'class': 'form-select'}),
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Document title'}),
            'file': forms.FileInput(attrs={'class': 'form-control'}),
        }


class PatientVitalsForm(forms.ModelForm):
    class Meta:
        model = PatientVitals
        fields = ['blood_pressure', 'pulse_rate', 'temperature', 'weight',
                  'height', 'oxygen_saturation', 'notes']
        widgets = {
            'blood_pressure': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '120/80'}),
            'pulse_rate': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '72 bpm'}),
            'temperature': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '98.6'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'kg'}),
            'height': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'cm'}),
            'oxygen_saturation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '98%'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
        }


class PatientDischargeForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['notes']
        widgets = {
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4,
                                           'placeholder': 'Discharge summary and instructions'}),
        }

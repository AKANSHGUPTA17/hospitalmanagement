from rest_framework import generics, serializers
from .models import Appointment


class AppointmentSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = '__all__'
        read_only_fields = ['appointment_id', 'created_at']

    def get_patient_name(self, obj):
        return obj.patient.full_name

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.full_name}"


class AppointmentListCreateView(generics.ListCreateAPIView):
    queryset = Appointment.objects.all().select_related('patient', 'doctor')
    serializer_class = AppointmentSerializer

    def perform_create(self, serializer):
        serializer.save(booked_by=self.request.user)


class AppointmentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Appointment.objects.all()
    serializer_class = AppointmentSerializer

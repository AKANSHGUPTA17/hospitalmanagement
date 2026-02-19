from rest_framework import generics, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Q
from .models import Patient, PatientVitals


class PatientSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Patient
        fields = '__all__'
        read_only_fields = ['patient_id', 'created_at', 'updated_at']

    def get_full_name(self, obj):
        return obj.full_name

    def get_status(self, obj):
        return obj.status


class PatientVitalsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientVitals
        fields = '__all__'
        read_only_fields = ['recorded_at']


class PatientListCreateView(generics.ListCreateAPIView):
    serializer_class = PatientSerializer

    def get_queryset(self):
        qs = Patient.objects.all()
        q = self.request.query_params.get('q')
        if q:
            qs = qs.filter(
                Q(first_name__icontains=q) | Q(last_name__icontains=q) |
                Q(phone__icontains=q) | Q(patient_id__icontains=q)
            )
        return qs

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class PatientDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Patient.objects.all()
    serializer_class = PatientSerializer


@api_view(['GET'])
def patient_search(request):
    q = request.query_params.get('q', '')
    patients = Patient.objects.filter(
        Q(first_name__icontains=q) | Q(last_name__icontains=q) |
        Q(phone__icontains=q) | Q(patient_id__icontains=q)
    )[:10]
    serializer = PatientSerializer(patients, many=True)
    return Response(serializer.data)


class PatientVitalsView(generics.ListCreateAPIView):
    serializer_class = PatientVitalsSerializer

    def get_queryset(self):
        return PatientVitals.objects.filter(patient_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(
            patient_id=self.kwargs['pk'],
            recorded_by=self.request.user
        )

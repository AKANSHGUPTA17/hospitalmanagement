from rest_framework import generics, serializers
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum
from datetime import date, timedelta
from .models import Bill, Payment


class BillSerializer(serializers.ModelSerializer):
    patient_name = serializers.SerializerMethodField()
    doctor_name = serializers.SerializerMethodField()

    class Meta:
        model = Bill
        fields = '__all__'
        read_only_fields = ['bill_number', 'subtotal', 'total_amount', 'due_amount', 'created_at']

    def get_patient_name(self, obj):
        return obj.patient.full_name if obj.patient else ''

    def get_doctor_name(self, obj):
        return str(obj.doctor) if obj.doctor else ''


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = '__all__'


class BillListCreateView(generics.ListCreateAPIView):
    queryset = Bill.objects.all().select_related('patient', 'doctor')
    serializer_class = BillSerializer

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)


class BillDetailView(generics.RetrieveUpdateAPIView):
    queryset = Bill.objects.all()
    serializer_class = BillSerializer


class PaymentListCreateView(generics.ListCreateAPIView):
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(bill_id=self.kwargs['pk'])

    def perform_create(self, serializer):
        serializer.save(bill_id=self.kwargs['pk'], received_by=self.request.user)


@api_view(['GET'])
def daily_revenue_report(request):
    today = date.today()
    data = []
    for i in range(29, -1, -1):
        day = today - timedelta(days=i)
        revenue = Bill.objects.filter(
            bill_date__date=day, payment_status='paid'
        ).aggregate(total=Sum('paid_amount'))['total'] or 0
        data.append({'date': day.isoformat(), 'revenue': float(revenue)})
    return Response(data)


@api_view(['GET'])
def monthly_revenue_report(request):
    today = date.today()
    data = []
    for i in range(11, -1, -1):
        if today.month - i > 0:
            month, year = today.month - i, today.year
        else:
            month, year = today.month - i + 12, today.year - 1
        revenue = Bill.objects.filter(
            bill_date__year=year, bill_date__month=month, payment_status='paid'
        ).aggregate(total=Sum('paid_amount'))['total'] or 0
        data.append({'year': year, 'month': month, 'revenue': float(revenue)})
    return Response(data)

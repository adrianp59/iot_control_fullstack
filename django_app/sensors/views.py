from rest_framework import viewsets, filters
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Sensor, TemperatureReading, HumidityReading
from .serializers import HumidityReadingSerializer, SensorSerializer, TemperatureReadingSerializer
from .filters import HumidityReadingFilter, TemperatureReadingFilter


class SensorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sensor.objects.all().order_by('name')
    serializer_class = SensorSerializer
    lookup_field = 'device_id'


class TemperatureReadingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TemperatureReading.objects.select_related('sensor').all()
    serializer_class = TemperatureReadingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = TemperatureReadingFilter
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

class HumidityReadingViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = HumidityReading.objects.select_related('sensor').all()
    serializer_class = HumidityReadingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_class = HumidityReadingFilter
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    

class ACOffViewSet(viewsets.ViewSet):
    def create(self, request):
        
        return Response({"message": "AC unit turned off"}, status=200)
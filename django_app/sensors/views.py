import time
import logging
from rest_framework import viewsets, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .utils import command_picker, MQTTOptions
from .models import Sensor, TemperatureReading, HumidityReading
from .serializers import (
    ACControlSerializer,
    CommandSerializer, 
    HumidityReadingSerializer, 
    SensorSerializer, 
    TemperatureReadingSerializer
)
from .filters import HumidityReadingFilter, TemperatureReadingFilter

logger = logging.getLogger(__name__)

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
    

class ACControlAPIView(APIView):
    def post(self, request):
        device_id = request.data.get('device_id')
        command = request.data.get('command')
        validated_data = ACControlSerializer(data={'device_id': device_id, 'command': command})
        
        if validated_data.is_valid():
            try:
                send_mqtt_message(f"home/sensors/{device_id}/ac_control", command)
                return Response({"status": "success", "message": f"Command '{command}' sent to device '{device_id}'"})
            except Exception as e:
                return Response({"status": "error", "message": str(e)}, status=500)
        else:
            return Response({"status": "error", "errors": validated_data.errors}, status=400)


class ACControlV2APIView(APIView):
    def post(self, request):
        serializer = CommandSerializer(data=request.data)
        start_time = time.time()
        if serializer.is_valid():
            payload = dict(serializer.validated_data)
            device_id = payload.get('device_id')
            command = command_picker(payload)
            try:
                command_topic = f"home/sensors/{device_id}/ac_control"
                status_topic = f"home/sensors/{device_id}/status"

                status_payload = MQTTOptions.send_and_wait_for_message(
                    publish_topic=command_topic,
                    payload=command,
                    subscribe_topic=status_topic,
                    timeout=5.0,
                )
                end_time = time.time()
                processing_time_ms = (end_time - start_time) * 1000
                logger.info(f"--- LATENCY TEST: Django processing: {processing_time_ms:.2f} ms ---")
                
                if status_payload == 'EXECUTED SUCCESSFULLY':
                    return Response({
                        "status": "success",
                        "message": f"Command '{command}' sent to device '{device_id}' and executed successfully",
                        "deviceStatus": status_payload,
                    })
                elif status_payload == 'EMPTY COMMAND':
                    return Response({
                        "status": "error",
                        "message": f"Command '{command}' sent to device '{device_id}' is empty",
                        "deviceStatus": status_payload,
                    })
                elif status_payload == 'UNKNOWN COMMAND':
                    return Response({
                        "status": "error",
                        "message": f"Command '{command}' sent to device '{device_id}' is unknown",
                        "deviceStatus": status_payload,
                    })
            except Exception as e:
                return Response({"status": "error", "message": str(e)}, status=500)
        else:
            return Response({"status": "error", "errors": serializer.errors}, status=400)

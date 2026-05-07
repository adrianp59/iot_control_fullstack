
from rest_framework import serializers
from .models import HumidityReading, Sensor, TemperatureReading


class SensorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sensor
        fields = ['device_id', 'name', 'location', 'created_at']
        

class TemperatureReadingSerializer(serializers.ModelSerializer):
    sensor_detail = SensorSerializer(source='sensor', read_only=True)

    class Meta:
        model = TemperatureReading
        fields = ['sensor', 'sensor_detail', 'timestamp', 'value']


class HumidityReadingSerializer(serializers.ModelSerializer):
    sensor_detail = SensorSerializer(source='sensor', read_only=True)

    class Meta:
        model = HumidityReading
        fields = ['sensor', 'sensor_detail', 'timestamp', 'value']


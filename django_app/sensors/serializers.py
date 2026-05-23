
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


class ACControlSerializer(serializers.Serializer):
    device_id = serializers.CharField()
    command = serializers.CharField()
    
    def validate_command(self, value):
        permitted_commands = {'ac_off', 'ac_cool_25', 'ac_heat_25', 'ac_cool_max_fan_24'}
        if value not in permitted_commands:
            raise serializers.ValidationError(f"Command must be one of {', '.join(permitted_commands)}")
        return value
    
    def validate_device_id(self, value):
        if not Sensor.objects.filter(device_id=value).exists():
            raise serializers.ValidationError("Device ID does not exist")
        return value


class ACControlV2Serializer(serializers.Serializer):
    device_id = serializers.CharField()
    command = serializers.DictField()
    
    # def validate_command(self, value):
    #     permitted_commands = {'ac_off', 'ac_cool_25', 'ac_heat_25', 'ac_cool_max_fan_24'}
    #     if value not in permitted_commands:
    #         raise serializers.ValidationError(f"Command must be one of {', '.join(permitted_commands)}")
    #     return value
    
    def validate_device_id(self, value):
        if not Sensor.objects.filter(device_id=value).exists():
            raise serializers.ValidationError("Device ID does not exist")
        return value


class CommandSerializer(serializers.Serializer):
    power = serializers.IntegerField(required=True)
    mode = serializers.CharField(required=False)
    temp = serializers.IntegerField(required=False)
    fan = serializers.CharField(required=False)
    device_id = serializers.CharField()

    def validate_device_id(self, value):
        if not Sensor.objects.filter(device_id=value).exists():
            raise serializers.ValidationError("Device ID does not exist")
        return value
    
    def validate_power(self, value):
        if value not in {0, 1}:
            raise serializers.ValidationError("Power must be 0 (off) or 1 (on)")
        return value
    
    def validate_mode(self, value):
        if value not in {'cool', 'heat', 'auto', 'dry'}:
            raise serializers.ValidationError("Mode must be one of 'cool', 'heat', 'auto', or 'dry'")
        return value
    
    def validate_temp(self, value):
        if not (16 <= value <= 30):
            raise serializers.ValidationError("Temperature must be between 16 and 30 degrees Celsius")
        return value
    
    def validate_fan(self, value):
        if value not in {'eco', 'high'}:
            raise serializers.ValidationError("Fan speed must be one of 'eco' or 'high'")
        return value
    
    def validate(self, attrs):
        mode = attrs.get('mode')
        temp = attrs.get('temp')
        power = attrs.get('power')
        fan = attrs.get('fan')
        
        if power == 0:
            return attrs

        if mode is None:
            raise serializers.ValidationError({'mode': "Mode is required when power is on"})

        if temp is None:
            raise serializers.ValidationError({'temp': "Temperature is required when power is on"})
        
        temp_ranges = {
            'cool': (18, 25),
            'heat': (20, 30),
            'auto': (18, 30),
            'dry': (18, 30),
        }
        
        if mode in temp_ranges:
            min_temp, max_temp = temp_ranges[mode]
            if not (min_temp <= temp <= max_temp):
                raise serializers.ValidationError({'temp': f"Temperature for mode '{mode}' must be between {min_temp} and {max_temp} degrees Celsius"})

        if mode == 'auto' and fan is not None:
            raise serializers.ValidationError({'fan': "Fan speed is not supported in auto mode"})

        if mode in {'cool', 'heat', 'dry'} and fan is None:
            raise serializers.ValidationError({'fan': f"Fan speed is required for mode '{mode}'"})
        
        return attrs
from django.db import models

class TemperatureReading(models.Model):
    id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey('Sensor', on_delete=models.CASCADE, related_name='readings', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()

    def __str__(self):
        return f"{self.value}°C at {self.timestamp}"


class Sensor(models.Model):
    device_id = models.SlugField(unique=True, help_text="Unique identifier for the sensor device; e.g., 'living-room-temp'")
    name = models.CharField(max_length=100, help_text="Name of the sensor")
    location = models.CharField(max_length=100, blank=True, help_text="Physical location of the sensor; e.g., 'Living Room'")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.device_id})"


class HumidityReading(models.Model):
    id = models.AutoField(primary_key=True)
    sensor = models.ForeignKey(Sensor, on_delete=models.CASCADE, related_name='humidity_readings', null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    value = models.FloatField()

    def __str__(self):
        return f"{self.value}% at {self.timestamp}"
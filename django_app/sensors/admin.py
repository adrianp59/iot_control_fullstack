from django.contrib import admin
from .models import HumidityReading, TemperatureReading, Sensor

@admin.register(TemperatureReading)
class TemperatureReadingAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'value')
    ordering = ('-timestamp',)

@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    list_display = ('device_id', 'name', 'location', 'created_at')
    search_fields = ('device_id', 'name', 'location')
    ordering = ('-created_at',)
    
@admin.register(HumidityReading)
class HumidityReadingAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'value')
    ordering = ('-timestamp',)
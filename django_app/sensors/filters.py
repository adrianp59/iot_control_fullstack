import django_filters
from .models import HumidityReading, TemperatureReading


class TemperatureReadingFilter(django_filters.FilterSet):
    sensor_id = django_filters.CharFilter(field_name='sensor__device_id')
    since = django_filters.IsoDateTimeFilter(field_name='timestamp', lookup_expr='gte')

    class Meta:
        model = TemperatureReading
        fields = ['sensor_id', 'since']

class HumidityReadingFilter(django_filters.FilterSet):
    sensor_id = django_filters.CharFilter(field_name='sensor__device_id')
    since = django_filters.IsoDateTimeFilter(field_name='timestamp', lookup_expr='gte')

    class Meta:
        model = HumidityReading
        fields = ['sensor_id', 'since']
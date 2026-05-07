from rest_framework.routers import DefaultRouter
from .views import SensorViewSet, TemperatureReadingViewSet, HumidityReadingViewSet

router = DefaultRouter()
router.register(r'sensors', SensorViewSet, basename='sensor')
router.register(r'readings', TemperatureReadingViewSet, basename='reading')
router.register(r'humidity-readings', HumidityReadingViewSet, basename='humidity-reading')

urlpatterns = router.urls

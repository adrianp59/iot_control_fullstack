from rest_framework.routers import DefaultRouter
from .views import ACControlAPIView, ACControlV2APIView, SensorViewSet, TemperatureReadingViewSet, HumidityReadingViewSet
from django.urls import path
    
router = DefaultRouter()
router.register(r'sensors', SensorViewSet, basename='sensor')
router.register(r'readings', TemperatureReadingViewSet, basename='reading')
router.register(r'humidity-readings', HumidityReadingViewSet, basename='humidity-reading')

urlpatterns = router.urls
urlpatterns += [
    path('ac-control/', ACControlAPIView.as_view(), name='ac-control'),
    path('ac-control/v2/', ACControlV2APIView.as_view(), name='ac-control-v2'),
]
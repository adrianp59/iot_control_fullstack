from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Sensor
from .serializers import CommandSerializer


class CommandSerializerTests(TestCase):
    def setUp(self):
        self.sensor = Sensor.objects.create(
            device_id='living-room-ac',
            name='Living Room AC',
            location='Living Room',
        )

    def test_accepts_dry_mode_with_fan(self):
        serializer = CommandSerializer(data={
            'device_id': self.sensor.device_id,
            'power': 1,
            'mode': 'dry',
            'temp': 24,
            'fan': 'eco',
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)

    def test_requires_temp_when_power_is_on(self):
        serializer = CommandSerializer(data={
            'device_id': self.sensor.device_id,
            'power': 1,
            'mode': 'cool',
            'fan': 'high',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('temp', serializer.errors)

    def test_rejects_mode_specific_out_of_range_temp(self):
        serializer = CommandSerializer(data={
            'device_id': self.sensor.device_id,
            'power': 1,
            'mode': 'cool',
            'temp': 30,
            'fan': 'eco',
        })

        self.assertFalse(serializer.is_valid())
        self.assertIn('temp', serializer.errors)

    def test_accepts_power_off_with_minimal_payload(self):
        serializer = CommandSerializer(data={
            'device_id': self.sensor.device_id,
            'power': 0,
        })

        self.assertTrue(serializer.is_valid(), serializer.errors)


class ACControlV2APIViewTests(APITestCase):
    def setUp(self):
        self.sensor = Sensor.objects.create(
            device_id='bedroom-ac',
            name='Bedroom AC',
            location='Bedroom',
        )
        user_model = get_user_model()
        self.user = user_model.objects.create_user(username='tester', password='secretpass123')
        self.client.force_authenticate(user=self.user)

    @patch('sensors.views.send_mqtt_message')
    def test_auto_mode_without_fan_succeeds(self, mocked_send):
        response = self.client.post('/api/ac-control/v2/', {
            'deviceId': self.sensor.device_id,
            'power': 1,
            'mode': 'auto',
            'temp': 24,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('ac_auto_p_0', response.data['message'])
        mocked_send.assert_called_once_with(
            f'home/sensors/{self.sensor.device_id}/ac_control',
            'ac_auto_p_0',
        )

    @patch('sensors.views.send_mqtt_message')
    def test_power_off_payload_succeeds(self, mocked_send):
        response = self.client.post('/api/ac-control/v2/', {
            'deviceId': self.sensor.device_id,
            'power': 0,
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('ac_off', response.data['message'])
        mocked_send.assert_called_once_with(
            f'home/sensors/{self.sensor.device_id}/ac_control',
            'ac_off',
        )

    def test_missing_temp_returns_validation_error(self):
        response = self.client.post('/api/ac-control/v2/', {
            'deviceId': self.sensor.device_id,
            'power': 1,
            'mode': 'heat',
            'fan': 'high',
        }, format='json')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['status'], 'error')
        self.assertIn('temp', response.data['errors'])

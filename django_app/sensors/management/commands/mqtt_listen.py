from django.conf import settings
from django.core.management.base import BaseCommand
import paho.mqtt.client as mqtt
from sensors.models import Sensor, TemperatureReading, HumidityReading

class Command(BaseCommand):
    help = 'MQTT listener for temperature and humidity readings'

    def handle(self, *args, **options):
        # Connection settings - using the container name from docker-compose
        MQTT_BROKER = settings.MQTT_BROKER
        MQTT_PORT = settings.MQTT_PORT
        MQTT_USER = settings.MQTT_USER
        MQTT_PASSWORD = settings.MQTT_PASSWORD
        MQTT_TOPIC = "home/sensors/+/temp"
        MQTT_TOPIC_HUMIDITY = "home/sensors/+/humidity"
        
        self.stdout.write(f"DEBUG: Broker={MQTT_BROKER}:{MQTT_PORT}")
        self.stdout.write(f"DEBUG: Username='{MQTT_USER}', Password='{MQTT_PASSWORD}'")

        def on_connect(client, userdata, flags, rc):
            self.stdout.write(self.style.SUCCESS(f"Connected to MQTT Broker with code: {rc}"))
            client.subscribe(MQTT_TOPIC)
            client.subscribe(MQTT_TOPIC_HUMIDITY)

        def on_message(client, userdata, msg):
            try:
                topic_parts = msg.topic.split('/')
                device_id = topic_parts[2]
                reading_type = topic_parts[-1]
                
                payload = msg.payload.decode('utf-8')
                value = float(payload)
                
                # Save to the database
                sensor, created = Sensor.objects.get_or_create(device_id=device_id)
                self.stdout.write(f"Topic type: {reading_type}, value: {value}")
                if reading_type == 'temp':
                    TemperatureReading.objects.create(sensor=sensor, value=value)
                    self.stdout.write(f"Recorded temperature: {value}°C")
                elif reading_type == 'humidity':
                    HumidityReading.objects.create(sensor=sensor, value=value)
                    self.stdout.write(f"Recorded humidity: {value}%")
                else:
                    self.stdout.write(f"Unknown reading type: {reading_type}")
                    
            except ValueError:
                self.stdout.write(f"Invalid data format: {payload}")
            except Exception as e:
                self.stdout.write(f"Error saving data: {e}")

        client = mqtt.Client()
        
        if MQTT_USER and MQTT_PASSWORD:
            client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
            self.stdout.write("Credentials set successfully.")
        else:
            self.stdout.write("Credentials failure.")
            
        client.on_connect = on_connect
        client.on_message = on_message

        self.stdout.write(self.style.NOTICE("Starting MQTT listener..."))
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.loop_forever()
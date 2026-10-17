import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from threading import Event
from django.conf import settings

class MQTTOptions:

    @staticmethod
    def send_mqtt_message(topic: str, payload: str) -> None:
        publish.single(
            topic, 
            payload=payload, 
            hostname=settings.MQTT_BROKER, 
            port=settings.MQTT_PORT
        )
    
    @staticmethod
    def send_and_wait_for_message(
        publish_topic: str,
        payload: str,
        subscribe_topic: str,
        timeout: float = 5.0,
        qos: int = 1,
    ) -> str:
        done = Event()
        result = {"payload": None, "error": None}

        def on_connect(client, userdata, flags, rc):
            if rc != 0:
                result["error"] = f"MQTT connect failed rc={rc}"
                done.set()
                return
            client.subscribe(subscribe_topic, qos=qos)

        def on_subscribe(client, userdata, mid, granted_qos):
            client.publish(publish_topic, payload=payload, qos=qos)

        def on_message(client, userdata, msg):
            if msg.topic == subscribe_topic:
                result["payload"] = msg.payload.decode("utf-8", errors="replace")
                done.set()

        client = mqtt.Client()
        if settings.MQTT_USER and settings.MQTT_PASSWORD:
            client.username_pw_set(settings.MQTT_USER, settings.MQTT_PASSWORD)
            
        client.on_connect = on_connect
        client.on_subscribe = on_subscribe
        client.on_message = on_message

        client.connect(settings.MQTT_BROKER, settings.MQTT_PORT, 60)
        client.loop_start()
        received = done.wait(timeout)
        client.loop_stop()
        client.disconnect()

        if result["error"]:
            raise RuntimeError(result["error"])
        if not received:
            raise TimeoutError(f"No message on {subscribe_topic} within {timeout}s")

        return result["payload"]
import paho.mqtt.publish as publish
import paho.mqtt.client as mqtt
from django.conf import settings
from threading import Event


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
    

def command_picker(input_data: dict) -> str:
    """
    Convert structured AC control input into a device command string.

    The function reads control fields from input_data and returns the final
    MQTT command payload expected by the AC device protocol.

    Behavior:
    - If power is 0, returns ac_off immediately.
    - For cool, heat, and dry:
    - returns ac_<mode>_<temp>_<fan> when fan is present
    - returns ac_<mode>_<temp> when fan is missing or falsy
    - For auto:
    - delegates to _pick_auto_mode_command(temp)
    - fan is ignored in this branch

    Expected input_data keys:
    - power (int): 0 for off, 1 for on.
    - mode (str): cool, heat, auto, or dry.
    - temp (int): target temperature.
    - fan (str, optional): fan profile for non-auto modes.

    Returns:
    - str: Command payload to publish to the AC control topic.

    Raises:
    - ValueError: If mode is not one of the supported modes.

    Notes:
    - This function assumes upstream validation already checked ranges/types.
    - In auto mode, invalid temp values may produce commands with None from the
    helper mapping (see _pick_auto_mode_command).
    """
    power = input_data.get('power')
    mode = input_data.get('mode')
    temp = input_data.get('temp')
    fan = input_data.get('fan')
    
    if power == 0:
        return "ac_off"
    
    mode_handlers = {
        'cool': lambda: f"ac_cool_{temp}_{fan}" if fan else f"ac_cool_{temp}",
        'heat': lambda: f"ac_heat_{temp}_{fan}" if fan else f"ac_heat_{temp}",
        'auto': lambda: _pick_auto_mode_command(temp),
        'dry':  lambda: f"ac_dry_{temp}_{fan}" if fan else f"ac_dry_{temp}",
    }
    
    handler = mode_handlers.get(mode)
    if handler is None:
        raise ValueError(f"Unsupported mode: {mode}")
    
    return handler()


def _pick_auto_mode_command(temp: int) -> str:
    """
    Build the AC auto-mode command from a target temperature.

    This function converts a temperature setpoint into the protocol format:
    ac_auto_p_<level> or ac_auto_m_<level>.

    Mapping rules:
    - Supported temperatures are 18 through 30 (inclusive).
    - The internal level is symmetric around 24:
      24 -> 0, 23/25 -> 1, 22/26 -> 2, ..., 18/30 -> 6.
    - Prefix selection:
      - p is used when temp >= 24
      - m is used when temp < 24

    Parameters:
    - temp (int): Desired setpoint in degrees Celsius.

    Returns:
    - str: Auto-mode command string for MQTT payloads.

    Current behavior note:
    - If temp is outside 18..30, the lookup returns None and produces a command
      like ac_auto_p_None or ac_auto_m_None. Upstream validation is expected.
    """
    temperature_settings = {
        30: 6,
        29: 5,
        28: 4,
        27: 3,
        26: 2,
        25: 1,
        24: 0,
        23: 1,
        22: 2,
        21: 3,
        20: 4,
        19: 5,
        18: 6,
    }
    
    if temp >= 24:
        return f"ac_auto_p_{temperature_settings.get(temp)}"
    else:
        return f"ac_auto_m_{temperature_settings.get(temp)}"
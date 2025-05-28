from senders.http_sender import HttpSender
from senders.mqtt_sender import MqttSender


def create_sender(config):
    protocol = config.GATEWAY_CONFIG['protocol']

    if protocol.lower() == 'mqtt':
        return MqttSender(config.MQTT_CONFIG, config.GATEWAY_CONFIG['device_id'])

    if protocol.lower() == 'http':
        return HttpSender(config.HTTP_CONFIG, config.GATEWAY_CONFIG['device_id'])

    raise ValueError("No valid sender configuration found")
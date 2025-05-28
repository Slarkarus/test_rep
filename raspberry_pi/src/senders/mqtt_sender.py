import paho.mqtt.client as mqtt
import logging
import copy


class MqttSender:
    def __init__(self, config, device_id):
        # Создаем копию конфига, чтобы не менять оригинал
        self.config = copy.deepcopy(config)
        self.config['client_id'] = device_id

        # Извлекаем параметры ПЕРЕД инициализацией клиента
        self.broker = self.config.get('broker')
        self.port = self.config.get('port', 8883)
        self.topic = self.config.get('topic', 'sensors/data')
        self.tls_config = self.config.get('tls', {})

        self.client = None
        self._setup_client()  # Теперь вызываем после инициализации параметров

    def _setup_client(self):
        # Создаем клиента с указанным client_id
        self.client = mqtt.Client(
            client_id=self.config.get('client_id'),
            clean_session=True
        )

        # Настраиваем TLS только если есть конфигурация
        if self.tls_config:
            self.client.tls_set(
                ca_certs=self.tls_config.get('ca_certs'),
                certfile=self.tls_config.get('certfile'),
                keyfile=self.tls_config.get('keyfile'),
                tls_version=mqtt.ssl.PROTOCOL_TLSv1_2
            )

            self.client.username_pw_set(
                username=self.tls_config.get('username'),
                password=self.tls_config.get('password')
            )

        # Callback'и
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect

        try:
            self.client.connect(self.broker, self.port, keepalive=60)
        except Exception as e:
            logging.error(f"Initial connection failed: {str(e)}")

    def _on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logging.info("Successfully connected to MQTT Broker")
        else:
            logging.error(f"Connection failed with code: {rc}")

    def _on_disconnect(self, client, userdata, rc):
        logging.warning(f"Disconnected from MQTT Broker (rc: {rc})")
        if rc != 0:
            self._reconnect()

    def _reconnect(self):
        logging.info("Attempting MQTT reconnection...")
        try:
            self.client.reconnect()
        except Exception as e:
            logging.error(f"Reconnection failed: {str(e)}")

    def send_data(self, payload):
        try:
            if not self.client.is_connected():
                self._reconnect()

            self.client.loop_start()

            result = self.client.publish(
                topic=self.topic,
                payload=payload,
                qos=1,
                retain=False
            )

            result.wait_for_publish(timeout=2)
            return result.is_published()

        except Exception as e:
            logging.error(f"MQTT send error: {str(e)}")
            return False
        finally:
            self.client.loop_stop()
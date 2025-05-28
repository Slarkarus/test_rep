import schedule
import time
from modbus_reader import ModbusReader
import logging
import json
import os


class GatewayCore:
    def __init__(self, modbus_config, data_sender, gateway_config):
        self.device_id = gateway_config['device_id']
        self.buffer_size = modbus_config.get('buffer_size', 100)
        self.sync_interval = gateway_config.get('sync_interval', 60)

        self.modbus_reader = ModbusReader(
            port=modbus_config['port'],
            baudrate=modbus_config['baudrate'],
            devices=modbus_config['devices'],
            parity=modbus_config['parity']
        )

        self.data_sender = data_sender

        self.buffer = []
        self._load_buffer()
        self._setup_scheduler()
        self._setup_sync_scheduler()
        logging.basicConfig(level=logging.INFO)

    def _setup_scheduler(self):
        for device in self.modbus_reader.devices_config:
            interval = device.get('poll_interval', 10)
            schedule.every(interval).seconds.do(
                self._polling_task_for_device,
                device['slave_id']
            )

    def _setup_sync_scheduler(self):
        schedule.every(self.sync_interval).seconds.do(
            self._force_sync_task
        )

    def _polling_task_for_device(self, slave_id):
        try:
            device = next(d for d in self.modbus_reader.devices_config
                          if d['slave_id'] == slave_id)
            data = self.modbus_reader.read_device(device)

            if data:
                self._process_reading(data, device)

        except Exception as e:
            logging.error(f"Polling error for device {slave_id}: {str(e)}")

    def _force_sync_task(self):
        if self.buffer:
            self._process_buffer()

    def _process_reading(self, data, device):
        formatted_data = self._format_data(data)
        if not self.data_sender.send_data(formatted_data):
            self._buffer_data(formatted_data)
        else:
            self._process_buffer()

    def _format_data(self, raw_data):
        measurements = []
        for name, value in raw_data['data'].items():
            measurements.append({
                'name': name,
                'value': value,
                'timestamp': raw_data['timestamp']
            })

        return {
            'device_id': self.device_id,
            'measurements': measurements
        }

    def _buffer_data(self, data):
        self.buffer.append(data)
        if len(self.buffer) > self.buffer_size:
            self.buffer.pop(0)
        self._save_buffer()

    def _process_buffer(self):
        while self.buffer:
            data = self.buffer[0]
            if self.data_sender.send_data(data):
                self.buffer.pop(0)
                self._save_buffer()
            else:
                break

    def _save_buffer(self):
        try:
            with open('buffer.json', 'w') as f:
                json.dump(self.buffer, f)
        except Exception as e:
            logging.error(f"Buffer save failed: {str(e)}")

    def _load_buffer(self):
        try:
            if os.path.exists('buffer.json'):
                with open('buffer.json', 'r') as f:
                    self.buffer = json.load(f)
        except Exception as e:
            logging.error(f"Buffer load failed: {str(e)}")

    def run(self):
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == "__main__":
    import config
    from data_sender import create_sender  # Фабричный метод

    sender = create_sender(config)
    gateway = GatewayCore(
        modbus_config=config.MODBUS_CONFIG,
        data_sender=sender,
        gateway_config=config.GATEWAY_CONFIG
    )
    gateway.run()
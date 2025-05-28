from pymodbus.client import ModbusSerialClient
import logging
import struct
import time


class ModbusReader:
    def __init__(self, port, baudrate, parity, devices):
        self.devices_config = devices
        self.client = ModbusSerialClient(
            port=port,
            baudrate=baudrate,
            parity=parity,
            stopbits=1,
            bytesize=8,
            framer='rtu',
            timeout=1
        )

    def _convert_value(self, registers, param_config):
        data_type = param_config.get('data_type', 'int16')
        byte_order = param_config.get('byte_order', 'AB')

        try:
            if data_type == 'float32':
                # Обработка формата CDAB (little-endian с перестановкой слов)
                if byte_order == 'CDAB':
                    combined = struct.pack('>HH', registers[1], registers[0])
                else:
                    combined = struct.pack('>HH', registers[0], registers[1])
                return struct.unpack('<f', combined)[0]

            elif data_type == 'int16':
                return registers[0] if registers[0] < 32768 else registers[0] - 65536

            elif data_type == 'uint16':
                return registers[0]

        except Exception as e:
            logging.error(f"Conversion error: {str(e)}")
            return None

    def _read_decimals(self, device_config):
        try:
            response = self.client.read_input_registers(
                address=8,
                count=1,
                unit=device_config['slave_id']
            )
            return response.registers[0] if not response.isError() else 1
        except:
            return 1

    def read_device(self, device_config):
        try:
            if not self.client.connect():
                raise ConnectionError("MODBUS connection failed")

            result = {'slave_id': device_config['slave_id'], 'data': {}}
            decimals = self._read_decimals(device_config)

            for param in device_config['parameters']:
                count = 2 if param.get('data_type') == 'float32' else 1
                response = self.client.read_input_registers(
                    address=param['address'],
                    count=count,
                    unit=device_config['slave_id']
                )

                if response.isError():
                    continue

                value = self._convert_value(response.registers, param)

                # Применяем делитель для определенных параметров
                if param.get('apply_decimals'):
                    divisor = 10 ** decimals
                    value = round(value / divisor, decimals) if value else 0

                result['data'][param['name']] = value

            result['timestamp'] = time.time()
            return result

        except Exception as e:
            logging.error(f"Read error for device {device_config['slave_id']}: {str(e)}")
            return None

        finally:
            self.client.close()

    def set_sensor_address(self, new_address):
        try:
            self.client.connect()
            self.client.write_register(
                address=0x000A,
                value=new_address,
                unit=0xFA
            )
            return True
        except Exception as e:
            logging.error(f"Address change failed: {str(e)}")
            return False
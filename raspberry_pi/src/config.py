MODBUS_CONFIG = {
    'port': '/dev/ttyUSB0',
    'baudrate': 9600,
    'parity': 'N',
    'devices': [
        {
            'slave_id': 1,
            'poll_interval': 5,
            'parameters': [
                {
                    'name': 'concentration',
                    'address': 0x0000,
                    'data_type': 'int16',
                    'apply_decimals': True
                },
                {
                    'name': 'wind_speed',
                    'address': 0x0000,
                    'data_type': 'float32',
                    'byte_order': 'CDAB'
                },
                {
                    'name': 'adc_value',
                    'address': 0x0012,
                    'data_type': 'uint16'
                }
            ]
        }
    ]
}

MQTT_CONFIG = {
    'broker': 'mqtt.example.com',
    'port': 8883,
    'topic': 'sensors',
    'tls': {
        'ca_certs': '/path/to/ca.crt',
        'certfile': '/path/to/client.crt',
        'keyfile': '/path/to/client.key'
    }
}

HTTP_CONFIG = {
    'url': 'https://example.com/api/sensor-data',
    'headers': {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer YOUR_API_TOKEN'
    },
    'timeout': 10,
    'verify_ssl': True,
    'ca_cert': '/path/to/ca.crt'
}

GATEWAY_CONFIG = {
    'device_id': 'gateway-001',
    'sync_interval': 60,
    'protocol': 'http'
}
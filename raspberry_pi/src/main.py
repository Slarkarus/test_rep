from gateway_core import GatewayCore
import config
from senders.data_sender import create_sender

if __name__ == "__main__":
    sender = create_sender(config)
    gateway = GatewayCore(
        modbus_config=config.MODBUS_CONFIG,
        data_sender=sender,
        gateway_config=config.GATEWAY_CONFIG
    )
    gateway.run()
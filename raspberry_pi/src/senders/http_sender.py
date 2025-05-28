import requests
import logging
import json


class HttpSender:
    def __init__(self, config, device_id):
        self.config = config
        self.device_id = device_id
        self.url = config.get('url')
        self.headers = config.get('headers', {'Content-Type': 'application/json'})
        self.timeout = config.get('timeout', 10)
        self.auth = config.get('auth')
        self.verify_ssl = config.get('verify_ssl', True)
        self.ca_cert = config.get('ca_cert')

    def send_data(self, data):
        try:
            # Если нужно добавить device_id в каждое сообщение
            # data['device_id'] = self.device_id

            response = requests.post(
                url=self.url,
                headers=self.headers,
                data=json.dumps(data),
                auth=self.auth,
                timeout=self.timeout,
                verify=self.ca_cert if self.ca_cert else self.verify_ssl
            )

            if response.status_code == 200:
                logging.info("Data sent successfully")
                return True
            else:
                logging.error(f"HTTP error {response.status_code}: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            logging.error(f"HTTP request failed: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return False
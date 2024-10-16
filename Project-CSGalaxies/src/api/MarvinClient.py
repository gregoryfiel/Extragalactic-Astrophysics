import logging
import requests
from requests.adapters import HTTPAdapter, Retry

class Marvin():
    """Classe Marvin que consome a API do Marvin e gera um documento XXX
    """
    def __init__(self, retry=3, timeout=5):
        logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s')
        self.retry = retry
        self.timeout = timeout
        self.__url = "https://XXXXXXX.com"

    def configureSession(self):
        self.session = requests.Session()
        retries = Retry(total=self.retry,
                        backoff_factor=0.1,
                        status_forcelist=[502, 503, 504])
        self.session.mount('http://', HTTPAdapter(max_retries=retries))

    def get_api(self, url, params=None):
        self.configuraSession()
        try:
            response = self.session.get(url,
                                        timeout=self.timeout,
                                        params=params)
            
            response.raise_for_status()
            json_data = response.json()

            return json_data

        except Exception as e:
            logging.error(f"error during HTTP request: {str(e)}")
            raise

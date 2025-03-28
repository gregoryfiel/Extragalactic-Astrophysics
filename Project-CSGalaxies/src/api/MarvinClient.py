import logging
import requests
from requests.adapters import HTTPAdapter, Retry
from requests.auth import HTTPBasicAuth
import netrc

class Marvin():
    """Classe Marvin que consome a API do Marvin e gera um documento JSON."""

    def __init__(self, retry=3, timeout=5):
        logging.basicConfig(format='%(asctime)s - %(levelname)s:%(message)s')
        self.retry = retry
        self.timeout = timeout
        self.__url = "https://api.sdss.org/marvin/maps/"
        self.auth = self.load_credentials()

    def load_credentials(self):
        try:
            netrc_info = netrc.netrc()
            login, _, password = netrc_info.authenticators('api.sdss.org')
            return HTTPBasicAuth(login, password)

        except Exception as e:
            logging.error(f"Error loading credentials: {e}")
            raise

    def configureSession(self):
        self.session = requests.Session()
        retries = Retry(total=self.retry,
                        backoff_factor=0.1,
                        status_forcelist=[502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def get_api(self, map_name=None, bintype=None, template=None, property_name=None, channel=None):
        self.configureSession()
        try:
            url = f"{self.__url}{map_name}/{bintype}/{template}/map/{property_name}/{channel}"
            response = self.session.post(url,
                                         params={
                                             'release':'DR17'},
                                         auth=self.auth,
                                         timeout=self.timeout)
            
            response.raise_for_status()
            json_data = response.json()

            return json_data['data']

        except Exception as e:
            logging.error(f"Error during HTTP request: {str(e)}")
            raise

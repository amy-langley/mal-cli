import logging
import requests
import requests_cache
import time

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from services.ConfigService import ConfigService

# https://requests-cache.readthedocs.io/en/latest/user_guide.html#usage
requests_cache.install_cache('./cache/mal', expire_after=300)
logger = logging.getLogger('Jikan')

retry_strategy = Retry(
    total=5,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"],
    backoff_factor=1 # use exponential backoff for 429
)

class JikanService:
    session = None
    configured = False

    @classmethod
    def configure(cls):
        if not cls.configured:
            adapter = HTTPAdapter(max_retries=retry_strategy)
            http = requests.Session()
            http.mount("https://", adapter)
            http.mount("http://", adapter)
            cls.session = http
            # https://findwork.dev/blog/advanced-usage-python-requests-timeouts-retries-hooks/#retry-on-failure
            # https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html
        cls.configured = True

    @classmethod
    def fetchPerson(cls, mal_id):
        return cls.getRequest(f'person/{mal_id}')

    @classmethod
    def fetchMedia(cls, mal_id):
        return cls.getRequest(f'anime/{mal_id}')

    @classmethod
    def fetchContributors(cls, mal_id):
        return cls.getRequest(f'anime/{mal_id}/characters_staff')

    @classmethod
    def getRequest(cls, uri):
        cls.configure()
        logger.info(f'Fetching {uri}')
        time.sleep(ConfigService.jikanThrottle)
        response = cls.session.get(f'{ConfigService.jikanUri}/{uri}')
        return response.json()

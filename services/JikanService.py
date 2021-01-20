import logging
import requests
import time

# TODO: transparent cache for requests library
# currently this just hangs for a while and then returns an error
import requests_cache
requests_cache.install_cache('./cache/mal', expire_after=300)
# https://requests-cache.readthedocs.io/en/latest/user_guide.html#usage

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

logger = logging.getLogger('Jikan')

retry_strategy = Retry(
    total=3,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "OPTIONS"],
    backoff_factor=1 # use exponential backoff for 429
)

class JikanService:
    session = None
    configured = False
    interceptor = {}
    jikan_uri = "https://api.jikan.moe/v3"
    rate_limit = 1

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
        return cls.getRequest(f'{cls.jikan_uri}/person/{mal_id}')

    @classmethod
    def fetchMedia(cls, mal_id):
        return cls.getRequest(f'{cls.jikan_uri}/anime/{mal_id}')

    @classmethod
    def fetchContributors(cls, mal_id):
        return cls.getRequest(f'{cls.jikan_uri}/anime/{mal_id}/characters_staff')

    @classmethod
    def getRequest(cls, uri):
        cls.configure()
        if cls.interceptor.__contains__(uri):
            logger.info(f'Using stored response for {uri}')
        else:
            logger.info(f'Fetching {uri}')
            time.sleep(cls.rate_limit)
            response = cls.session.get(uri)
            cls.interceptor[uri] = response.json()

        return cls.interceptor[uri]

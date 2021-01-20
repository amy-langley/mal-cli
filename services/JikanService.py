import logging
import requests
import time

# TODO: transparent cache for requests library
# currently this just hangs for a while and then returns an error
#import requests_cache
#requests_cache.install_cache('./cache/mal')
# https://requests-cache.readthedocs.io/en/latest/user_guide.html#usage

logger = logging.getLogger('Jikan')

class JikanService:
    interceptor = {}

    jikan_uri = "https://api.jikan.moe/v3"
    rate_limit = 2

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
        if cls.interceptor.__contains__(uri):
            logger.info(f'Using stored response for {uri}')
        else:
            logger.info(f'Fetching {uri}')
            time.sleep(cls.rate_limit)
            cls.interceptor[uri] = requests.get(uri).json()

        return cls.interceptor[uri]

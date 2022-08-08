import threading
import requests
import logging

TOKEN_URL = "https://id.twitch.tv/oauth2/token?client_id={0}&client_secret={1}&grant_type=client_credentials"

logger = logging.getLogger(__name__)


def synchronized(func):
    func.__lock__ = threading.Lock()

    def synced_func(*args, **kws):
        with func.__lock__:
            return func(*args, **kws)

    return synced_func


class TwitchAuthenticator:
    cached_token = None

    def __init__(self, client_id, client_secret, username):
        self.username = username
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = TOKEN_URL.format(self.client_id, self.client_secret)

    @synchronized
    def get_token(self):
        if self.cached_token is None:
            self._fetch_token()

        return self.cached_token

    @synchronized
    def refresh_token(self):
        # TODO what if both will call refresh ?
        self._fetch_token()
        return self.cached_token

    def _fetch_token(self):
        token_response = requests.post(self.token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()
        self.cached_token = token["access_token"]

        logger.info("Fetched new token %s", self.cached_token)

import datetime
import enum
import logging
import os
import subprocess
import time
import requests

TOKEN_URL = "https://id.twitch.tv/oauth2/token?client_id={0}&client_secret={1}&grant_type=client_credentials"
HELIX_STREAM_URL = "https://api.twitch.tv/helix/streams?user_login={0}"

logger = logging.getLogger(__name__)


class TwitchStreamerStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4


class TwitchRecorder:
    access_token = None

    def __init__(self, client_id, client_secret, username, output_path, quality="480p", on_download=None):
        # global configuration
        self.disable_ffmpeg = False
        self.refresh_timeout = 15
        self.output_path = output_path
        self.stream_uid = None
        self.on_download = on_download

        # twitch configuration
        self.username = username
        self.quality = quality
        self.client_id = client_id
        self.client_secret = client_secret
        self.token_url = TOKEN_URL.format(self.client_id, self.client_secret)

    def fetch_access_token(self):
        token_response = requests.post(self.token_url, timeout=15)
        token_response.raise_for_status()
        token = token_response.json()
        return token["access_token"]

    def run(self):
        # path to recorded stream
        recording_path = os.path.join(self.output_path, "recorded", self.username)

        # create directory for recordedPath and processedPath if not exist
        if os.path.isdir(recording_path) is False:
            os.makedirs(recording_path)

        # make sure the interval to check user availability is not less than 15 seconds
        if self.refresh_timeout < 15:
            logger.warning("check interval should not be lower than 15 seconds")
            self.refresh_timeout = 15
            logger.warning("check interval set to 15 seconds")

        self.access_token = self.fetch_access_token()
        self.loop_check(recording_path)

    def loop_check(self, recording_path):
        logger.info("checking for %s every %s seconds, recording with %s quality",
                    self.username, self.refresh_timeout, self.quality)
        while True:
            status, info = self.check_user()
            if status == TwitchStreamerStatus.NOT_FOUND:
                logger.error("username not found, invalid username or typo")
                time.sleep(self.refresh_timeout)
            elif status == TwitchStreamerStatus.ERROR:
                logger.error("%s unexpected error. will try again in 5 minutes",
                             datetime.datetime.now().strftime("%Hh%Mm%Ss"))
                time.sleep(300)
            elif status == TwitchStreamerStatus.OFFLINE:
                logger.info("%s currently offline, checking again in %s seconds", self.username, self.refresh_timeout)
                time.sleep(self.refresh_timeout)
            elif status == TwitchStreamerStatus.UNAUTHORIZED:
                logger.info("unauthorized, will attempt to log back in immediately")
                self.access_token = self.fetch_access_token()
            elif status == TwitchStreamerStatus.ONLINE:
                logger.info("%s online, stream recording in session", self.username)

                channels = info["data"]
                channel = next(iter(channels), None)

                recorded_filename = self.download_stream(channel, recording_path)

                logger.info("recording stream is done")

                if self.on_download is not None:
                    self.on_download(recorded_filename)

                time.sleep(self.refresh_timeout)

    def check_user(self):
        info = None
        status = TwitchStreamerStatus.ERROR
        try:
            headers = {"Client-ID": self.client_id, "Authorization": "Bearer " + self.access_token}
            r = requests.get(HELIX_STREAM_URL.format(self.username), headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchStreamerStatus.OFFLINE
            else:
                status = TwitchStreamerStatus.ONLINE
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchStreamerStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchStreamerStatus.NOT_FOUND
        return status, info

    def download_stream(self, channel, recording_path):
        filename = self.username + " - " + datetime.datetime.now() \
            .strftime("%Y-%m-%d %Hh%Mm%Ss") + " - " + channel.get("title") + ".mp4"

        filename = "".join(x for x in filename if x.isalnum() or x in [" ", "-", "_", "."])
        recorded_filename = os.path.join(recording_path, filename)

        # start streamlink process
        subprocess.call([
            "streamlink",
            "--twitch-disable-ads",
            "twitch.tv/" + self.username,
            self.quality,
            "-o",
            recorded_filename
        ])

        return recorded_filename

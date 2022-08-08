import datetime
import enum
import logging
import os
import subprocess
import requests
import time

HELIX_STREAM_URL = "https://api.twitch.tv/helix/streams?user_login={0}"

logger = logging.getLogger(__name__)


class TwitchStreamStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4


class TwitchVideoRecorder:
    access_token = None

    def __init__(self, authenticator, streamer_name, output_path, quality="480p", on_finish=None):
        # global configuration
        self.disable_ffmpeg = False
        self.refresh_timeout = 15
        self.output_path = output_path
        self.stream_uid = None
        self.on_finish = on_finish

        # twitch configuration
        self.streamer_name = streamer_name
        self.quality = quality
        self.authenticator = authenticator

    def run(self):
        # path to recorded stream
        recording_path = os.path.join(self.output_path, "recorded", self.streamer_name)

        # create directory for recordedPath and processedPath if not exist
        if os.path.isdir(recording_path) is False:
            os.makedirs(recording_path)

        # make sure the interval to check user availability is not less than 15 seconds
        if self.refresh_timeout < 15:
            logger.warning("check interval should not be lower than 15 seconds")
            self.refresh_timeout = 15
            logger.warning("check interval set to 15 seconds")

        self.loop_check(recording_path)

    def loop_check(self, recording_path):
        logger.info("checking for %s every %s seconds, recording with %s quality",
                    self.streamer_name, self.refresh_timeout, self.quality)
        while True:
            status, info = self.check_user()
            if status == TwitchStreamStatus.NOT_FOUND:
                logger.error("streamer_name not found, invalid streamer_name or typo")
                time.sleep(self.refresh_timeout)
            elif status == TwitchStreamStatus.ERROR:
                logger.error("%s unexpected error. will try again in 5 minutes",
                             datetime.datetime.now().strftime("%Hh%Mm%Ss"))
                time.sleep(300)
            elif status == TwitchStreamStatus.OFFLINE:
                logger.info("%s currently offline, checking again in %s seconds", self.streamer_name,
                            self.refresh_timeout)
                time.sleep(self.refresh_timeout)
            elif status == TwitchStreamStatus.UNAUTHORIZED:
                logger.info("unauthorized, will attempt to log back in immediately")
                self.access_token = self.authenticator.refresh_token()
            elif status == TwitchStreamStatus.ONLINE:
                logger.info("%s online, stream recording in session", self.streamer_name)

                channels = info["data"]
                channel = next(iter(channels), None)

                recorded_filename = self.record_stream(channel, recording_path)

                logger.info("recording stream is done")

                if self.on_finish is not None:
                    self.on_finish(channel, recorded_filename)

                time.sleep(self.refresh_timeout)

    # TODO use twitch library instead of pure requests
    def check_user(self):

        info = None
        status = TwitchStreamStatus.ERROR
        try:
            headers = {"Client-ID": self.authenticator.client_id,
                       "Authorization": "Bearer {}".format(self.authenticator.get_token())}
            r = requests.get(HELIX_STREAM_URL.format(self.streamer_name), headers=headers, timeout=15)
            r.raise_for_status()
            info = r.json()
            if info is None or not info["data"]:
                status = TwitchStreamStatus.OFFLINE
            else:
                status = TwitchStreamStatus.ONLINE
        except requests.exceptions.RequestException as e:
            if e.response:
                if e.response.status_code == 401:
                    status = TwitchStreamStatus.UNAUTHORIZED
                if e.response.status_code == 404:
                    status = TwitchStreamStatus.NOT_FOUND
        return status, info

    def record_stream(self, channel, recording_path):
        filename = self.streamer_name + " - " + datetime.datetime.now() \
            .strftime("%Y-%m-%d %Hh%Mm%Ss") + " - " + channel.get("title") + ".mp4"

        filename = "".join(x for x in filename if x.isalnum() or x in [" ", "-", "_", "."])
        recorded_filename = os.path.join(recording_path, filename)

        # start streamlink process
        subprocess.call([
            "streamlink",
            "--twitch-disable-ads",
            "twitch.tv/" + self.streamer_name,
            self.quality,
            "-o",
            recorded_filename
        ])

        return recorded_filename

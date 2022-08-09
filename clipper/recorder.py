import logging
import time
import sys

from clipper.api import TwitchApi, TwitchStreamStatus
from clipper.chat import TwitchChatRecorder

logger = logging.getLogger(__name__)


class RecorderConfig:
    def __init__(self, tw_client, tw_secret, tw_streamer, tw_quality, output_path):
        self.output_path = output_path
        self.tw_quality = tw_quality
        self.tw_streamer = tw_streamer
        self.tw_secret = tw_secret
        self.tw_client = tw_client


class Recorder:
    def __init__(self, config):
        self.config = config
        self.api = TwitchApi(config.tw_client, config.tw_secret)
        # self.video_recorder = TwitchVideoRecorder(self.api,)
        self.chat_recorder = TwitchChatRecorder(self.api, config.tw_streamer)

    def run(self):
        while True:
            logger.info("Start watching streamer %s", self.config.tw_streamer)
            status = self.api.get_user_status(self.config.tw_streamer)
            if status == TwitchStreamStatus.ONLINE:
                logger.info("Streamer %s is online. Start recording", self.config.tw_streamer)
                self.chat_recorder.run()
                # TODO run video record and join to it.. Run 2 threads?
                logger.info("Streamer %s finished his stream", self.config.tw_streamer)
                time.sleep(15)

            if status == TwitchStreamStatus.OFFLINE:
                logger.info("Streamer %s is offline. Waiting for it 60 sec", self.config.tw_streamer)
                time.sleep(60)

            if status == TwitchStreamStatus.ERROR:
                logger.critical("Error occurred. Exit", self.config.tw_streamer)
                sys.exit(1)

    # def run(self):
    #     logger.info("Start watching streamer %s", self.config.tw_streamer)
    #
    #     while True:
    #         status, info = self.api.check_user_status(self.config.tw_streamer)
    #         if status == TwitchStreamStatus.NOT_FOUND:
    #             logger.error("streamer_name not found, invalid streamer_name or typo")
    #             sys.exit(1)
    #         elif status == TwitchStreamStatus.ERROR:
    #             logger.error("%s unexpected error. will try again in 5 minutes",
    #                          datetime.datetime.now().strftime("%Hh%Mm%Ss"))
    #             time.sleep(300)
    #         elif status == TwitchStreamStatus.OFFLINE:
    #             logger.info("%s currently offline, checking again in %s seconds", self.streamer_name,
    #                         self.refresh_timeout)
    #             time.sleep(self.refresh_timeout)
    #         elif status == TwitchStreamStatus.UNAUTHORIZED:
    #             logger.info("unauthorized, will attempt to log back in immediately")
    #             self.access_token = self.authenticator.refresh_token()
    #         elif status == TwitchStreamStatus.ONLINE:
    #             logger.info("%s online, stream recording in session", self.streamer_name)
    #
    #             channels = info["data"]
    #             channel = next(iter(channels), None)
    #
    #             recorded_filename = self.record_stream(channel, recording_path)
    #
    #             logger.info("recording stream is done")
    #
    #             if self.on_finish is not None:
    #                 self.on_finish(channel, recorded_filename)
    #
    #             time.sleep(self.refresh_timeout)

    # def start_record(self):
    #     pass

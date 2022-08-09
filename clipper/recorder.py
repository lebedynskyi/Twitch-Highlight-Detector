import logging
import os
import time
import sys
from datetime import datetime

from clipper.api import TwitchApi, TwitchStreamStatus
from clipper.chat import TwitchChatRecorder
from clipper.video import TwitchVideoRecorder

logger = logging.getLogger(__name__)


class RecorderConfig:
    def __init__(self, tw_client, tw_secret, tw_streamer, tw_quality, output_folder):
        self.output_folder = output_folder
        self.tw_quality = tw_quality
        self.tw_streamer = tw_streamer
        self.tw_secret = tw_secret
        self.tw_client = tw_client


class Recorder:
    audio_thread = None
    video_thread = None

    def __init__(self, config):
        self.config = config
        self.api = TwitchApi(config.tw_client, config.tw_secret)
        self.recording_folder = os.path.join(self.config.output_folder, self.config.tw_streamer)
        self.video_recorder = TwitchVideoRecorder(self.api, config.tw_streamer, self.recording_folder)
        self.chat_recorder = TwitchChatRecorder(self.api, config.tw_streamer, self.recording_folder)

    def run(self):
        if os.path.isdir(self.recording_folder) is False:
            logger.info("Recording folder `%s` does not exists. Create it", self.recording_folder)
            os.makedirs(self.recording_folder)

        while True:
            logger.info("Start watching streamer %s", self.config.tw_streamer)
            status = self.api.get_user_status(self.config.tw_streamer)
            if status == TwitchStreamStatus.ONLINE:
                logger.info("Streamer %s is online. Start recording", self.config.tw_streamer)

                now = datetime.now()
                file_template = "{0}-{1}".format(self.config.tw_streamer, now.strftime("%H-%M-%S"))
                self.chat_recorder.run(file_template)
                # self.video_recorder.run(file_template)

                logger.info("Streamer %s has finished stream", self.config.tw_streamer)
                time.sleep(15)

            if status == TwitchStreamStatus.OFFLINE:
                logger.info("Streamer %s is offline. Waiting for 300 sec", self.config.tw_streamer)
                time.sleep(300)

            if status == TwitchStreamStatus.ERROR:
                logger.critical("Error occurred. Exit", self.config.tw_streamer)
                sys.exit(1)

            if status == TwitchStreamStatus.NOT_FOUND:
                logger.critical(f"Streamer %s not found, invalid streamer_name or typo", self.config.tw_streamer)
                sys.exit(1)

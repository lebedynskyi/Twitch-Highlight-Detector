import logging
import os
import time
import sys
import threading
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
        self.streamer_folder = os.path.join(self.config.output_folder, self.config.tw_streamer)
        self.video_recorder = TwitchVideoRecorder()
        self.chat_recorder = TwitchChatRecorder(self.api, debug=True)

    def run(self):
        while True:
            logger.info("Start watching streamer %s", self.config.tw_streamer)
            status = self.api.get_user_status(self.config.tw_streamer)
            if status == TwitchStreamStatus.ONLINE:
                logger.info("Streamer %s is online. Start recording", self.config.tw_streamer)

                start_time = datetime.now()
                record_folder_name = start_time.strftime("%d-%m-%Y_%H-%M-%S")
                record_folder = os.path.join(self.streamer_folder, record_folder_name)
                os.makedirs(record_folder)

                chat_file = os.path.join(record_folder,  "chat.txt")
                video_file = os.path.join(record_folder, "video.mp4")

                self.chat_recorder.run(self.config.tw_streamer, chat_file)
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

import logging
import os
import subprocess
import time
import sys
from datetime import datetime

from clipper.analyser import ChatAnalyser
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
    def __init__(self, config):
        self.config = config
        self.api = TwitchApi(config.tw_client, config.tw_secret)
        self.streamer_folder = os.path.join(self.config.output_folder, self.config.tw_streamer)
        self.video_recorder = TwitchVideoRecorder()
        self.chat_recorder = TwitchChatRecorder(self.api, debug=True)
        self.chat_analyser = ChatAnalyser()

    def run(self):
        logger.info("Start recording streamer %s", self.config.tw_streamer)
        status = self.api.get_user_status(self.config.tw_streamer)

        while True:
            if status == TwitchStreamStatus.ONLINE:
                logger.info("Streamer %s is online. Start recording", self.config.tw_streamer)

                start_time = datetime.now()
                record_folder_name = start_time.strftime("%d-%m-%Y_%H-%M-%S")
                record_folder = os.path.join(self.streamer_folder, record_folder_name)
                os.makedirs(record_folder)

                output_video_file = os.path.join(record_folder, "video.mp4")
                output_chat_file = os.path.join(record_folder, "chat.txt")
                output_chat_peaks_file = os.path.join(record_folder, "chat_peaks.txt")
                output_chat_chart_file = os.path.join(record_folder, "chat_chart.png")

                self.chat_recorder.run(self.config.tw_streamer, output_chat_file)
                self.video_recorder.run(self.config.tw_streamer, output_video_file, quality="160p")
                self._loop_recording()
                self._post_process_video(output_chat_file, output_chat_peaks_file, output_chat_chart_file)

            elif status == TwitchStreamStatus.OFFLINE:
                logger.info("Streamer %s is offline. Waiting for 300 sec", self.config.tw_streamer)
                time.sleep(300)

            if status == TwitchStreamStatus.ERROR:
                logger.critical("Error occurred. Exit", self.config.tw_streamer)
                sys.exit(1)

            elif status == TwitchStreamStatus.NOT_FOUND:
                logger.critical(f"Streamer %s not found, invalid streamer_name or typo", self.config.tw_streamer)
                sys.exit(1)

    def _loop_recording(self):
        while True:
            if self.video_recorder.is_running or self.chat_recorder.is_running:
                if not (self.video_recorder.is_running and self.chat_recorder.is_running):
                    self.video_recorder.stop()
                    self.chat_recorder.stop()
                    break
                logger.info("Recording in progress. Wait 1m")
                time.sleep(60)
                continue
            break

    def _post_process_video(self, output_chat_file, output_chat_peaks_file, output_chat_chart_file):
        peaks = self.chat_analyser.run(output_chat_file, output_chat_peaks_file, output_chat_chart_file)
        logger.info("Found peaks: %s for file %s", len(peaks), output_chat_file)

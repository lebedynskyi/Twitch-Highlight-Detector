import logging
import subprocess

logger = logging.getLogger(__name__)


class TwitchVideoRecorder:
    is_running = False
    refresh_timeout = 15
    streamlink_process = None

    def run(self, streamer_name, output_file, quality="720p"):
        self.is_running = True
        self._record_stream(streamer_name, output_file, quality)

    def stop(self):
        try:
            if self.streamlink_process:
                self.streamlink_process.terminate()

            self.streamlink_process = None
            logger.error("Video stopped")
        except BaseException as e:
            logger.error("Unable to stop video")
            logger.error(e)

        self.is_running = False

    def _record_stream(self, streamer_name, output_file, quality):
        try:
            self.streamlink_process = subprocess.Popen([
                "streamlink",
                "--twitch-disable-ads",
                "twitch.tv/" + streamer_name,
                quality,
                "-o",
                output_file
            ])

        except BaseException as e:
            logger.error("Unable to run streamlink")
            logger.error(e)
            self.is_running = False

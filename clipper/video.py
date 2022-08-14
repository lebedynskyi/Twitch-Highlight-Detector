import logging
import subprocess

logger = logging.getLogger(__name__)


class TwitchVideoRecorder:
    is_running = False
    refresh_timeout = 15
    streamlink_process = None

    def run(self, streamer_name, output_file, quality="480p"):
        self._record_stream(streamer_name, output_file, quality)

    def stop(self):
        if self.streamlink_process:
            self.streamlink_process.kill()

    def _record_stream(self, streamer_name, output_file, quality):
        # subprocess.call()
        self.streamlink_process = subprocess.Popen([
            "streamlink",
            "--twitch-disable-ads",
            "twitch.tv/" + streamer_name,
            quality,
            "-o",
            output_file
        ])

        self.is_running = True

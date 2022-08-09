import datetime
import logging
import os
import subprocess

logger = logging.getLogger(__name__)


class TwitchVideoRecorder:
    access_token = None

    def __init__(self, authenticator, streamer_name, recording_folder, quality="480p", on_finish=None):
        # global configuration
        self.disable_ffmpeg = False
        self.refresh_timeout = 15
        self.recording_folder = recording_folder
        self.stream_uid = None
        self.on_finish = on_finish

        # twitch configuration
        self.streamer_name = streamer_name
        self.quality = quality
        self.authenticator = authenticator

    def run(self):
        # make sure the interval to check user availability is not less than 15 seconds
        if self.refresh_timeout < 15:
            logger.warning("check interval should not be lower than 15 seconds")
            self.refresh_timeout = 15
            logger.warning("check interval set to 15 seconds")

        self.record_stream(self.streamer_name, recording_path)

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

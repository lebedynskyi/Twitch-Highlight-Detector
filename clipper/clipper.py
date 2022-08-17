import logging
import os
import subprocess
from datetime import datetime
from datetime import timedelta

logger = logging.getLogger(__name__)


class Clipper:
    def run(self, video_file, chat_peaks_file, output_folder):
        try:
            self._run(video_file, chat_peaks_file, output_folder)
        except BaseException as e:
            logger.error(e)

    def _run(self, video_file, chat_peaks_file, output_folder):
        if not os.path.isdir(output_folder):
            os.mkdir(output_folder)

        with open(chat_peaks_file, "r") as stream:
            lines = stream.readlines()

        if not lines:
            logger.error("No peaks found")
            return

        counter = 1
        for line in lines:
            # l = "2022-08-17 10:15 -> (1.0, 42.0)"
            time_part = line.split("->")[1].strip()  # (1.0, 42.0)
            time = time_part.replace("(", "").replace(")", "").split(",")
            video_time = datetime(2000, 1, 1, int(float(time[0])), int(float(time[1])), 0, 0)
            start_time = video_time - timedelta(minutes=1)
            end_time = video_time + timedelta(minutes=1)

            ffmpeg_start_time = start_time.strftime("%H:%M:00")
            ffmpeg_end_time = end_time.strftime("%H:%M:00")
            output_file = os.path.join(output_folder, f"clip_{counter}.mp4")
            self._cut_clip(video_file, ffmpeg_start_time, ffmpeg_end_time, output_file)
            counter = counter + 1

    def _cut_clip(self, video_file, start_time, end_time, output_name):
        #  ffmpeg -ss 00:01:00 -to 00:02:00  -i input.mp4 -c copy output.mp4
        try:
            subprocess.call([
                "ffmpeg",
                "-err_detect",
                "ignore_err",
                "-ss",
                start_time,
                "-to",
                end_time,
                "-i",
                video_file,
                "-c",
                "copy",
                output_name
            ])

        except BaseException as e:
            logger.error("Unable to run streamlink")
            logger.error(e)


if __name__ == "__main__":
    "/Users/vetalll/Projects/Python/TwitchClipper/recorded/"
    video = "/Users/vetalll/Projects/Python/TwitchClipper/recorded/icebergdoto/17-08-2022_13-30-20/video.mp4"
    peaks = "/Users/vetalll/Projects/Python/TwitchClipper/recorded/icebergdoto/17-08-2022_13-30-20/chat_peaks.txt"
    result = "/Users/vetalll/Projects/Python/TwitchClipper/recorded/icebergdoto/17-08-2022_13-30-20/clips"
    clipper = Clipper()
    clipper.run(video, peaks, result)

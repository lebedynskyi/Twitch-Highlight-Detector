import scipy
import numpy as np
import logging
import matplotlib.pyplot as plt

from datetime import datetime

logger = logging.getLogger(__name__)


class ChatAnalyser:
    def __init__(self, ignore_commands=True, ignored_users=None):
        if ignored_users is None:
            ignored_users = ["moobot", "nightbot"]

        self.ignored_users = ignored_users
        self.ignore_commands = ignore_commands

    def run(self, chat_file, peaks_output_file, peaks_output_chart, start_time):
        dates = self._read_message_dates(chat_file)
        messages_per_minute = self._group_dates(dates)
        peaks = self._find_peeks(messages_per_minute, peaks_output_file, peaks_output_chart)
        return peaks

    def _read_message_dates(self, chat_file):
        dates = []

        with open(chat_file, "r") as stream:
            while True:

                line = stream.readline()
                if not line:
                    break

                message_data = line.split("<~|~>")
                if len(message_data) != 3:
                    # Wrong line format
                    continue

                if message_data[1].lower() in self.ignored_users:
                    continue

                if self.ignore_commands and message_data[2].startswith("!"):
                    continue

                date = message_data[0]
                try:
                    dates.append(self._parse_date(date))
                except BaseException as e:
                    logger.error(e)

        return dates

    def _parse_date(self, date_str):
        return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")

    def _group_dates(self, dates):
        groups = {}
        for d in dates:
            key = datetime.strftime(d, "%Y-%m-%d %H:%M")
            if key in groups.keys():
                groups[key] = groups[key] + 1
            else:
                groups[key] = 0

        groups.values()
        return groups

    def _find_peeks(self, messages_per_minute, peaks_output_file, peaks_output_chart):
        y_coordinates = list(messages_per_minute.values())
        x_coordinates = list(messages_per_minute.keys())
        peak_indices = scipy.signal.find_peaks_cwt(np.array(y_coordinates), 0.5)

        fig, ax = plt.subplots()
        ax.plot(range(0, len(y_coordinates), 1), y_coordinates)
        plt.xlabel("Video Minutes")
        plt.ylabel("Message count")
        plt.title("Stream chat reaction")
        plt.savefig(peaks_output_chart)

        start_time = None
        if len(x_coordinates) > 0:
            start_time = datetime.strptime(x_coordinates[0], "%Y-%m-%d %H:%M")

        max_value = max(y_coordinates)
        trash_hold_value = max_value * 0.75
        filtered_values = [x_coordinates[index] for index in peak_indices if y_coordinates[index] > trash_hold_value]
        with open(peaks_output_file, "w") as stream:
            for peak in filtered_values:
                if start_time:
                    peak_time = datetime.strptime(peak, "%Y-%m-%d %H:%M")
                    diff = peak_time - start_time
                    minutes = divmod(diff.total_seconds() / 60, 60)
                    stream.writelines(f"{peak} -> {minutes}\n")
                else:
                    stream.writelines(f"{peak}\n")

        return peak_indices


if __name__ == "__main__":
    anal = ChatAnalyser()
    chat_file = "/Users/vetalll/Projects/Python/TwitchClipper/recorded/vovapain/17-08-2022_08-33-23/chat.txt"
    out_file = "/Users/vetalll/Projects/Python/TwitchClipper/recorded/vovapain/17-08-2022_08-33-23/chat_peaks.txt"
    out_hraph = "/Users/vetalll/Projects/Python/TwitchClipper/recorded/vovapain/17-08-2022_08-33-23/chat_chart.png"

    anal.run(chat_file, out_file, out_hraph, datetime(2022, 8, 15, 20, 38, 49))

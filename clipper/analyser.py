import scipy
import numpy as np
import logging
import matplotlib.pyplot as plt

from datetime import datetime

from clipper.chat import CHAT_DIVIDER

logger = logging.getLogger(__name__)


class ChatAnalyser:
    def run(self, chat_file, peaks_output_file, peaks_output_chart):
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

                message_data = line.split(CHAT_DIVIDER)
                if len(message_data) != 3:
                    # Wrong line format
                    continue

                date = message_data[0]
                dates.append(self._parse_date(date))
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
        peak_indices = scipy.signal.find_peaks_cwt(np.array(y_coordinates), 1)

        x_hours = [x.split(" ")[1] for x in x_coordinates]
        fig, ax = plt.subplots()
        ax.plot(x_hours, y_coordinates)
        fig.autofmt_xdate()
        plt.xlabel("Time")
        plt.ylabel("Count")
        plt.title("Stream chat reaction")
        plt.savefig(peaks_output_chart)

        peak_values = [x_coordinates[index] for index in peak_indices]
        with open(peaks_output_file, "w") as stream:
            for peak in peak_values:
                stream.writelines(f"{peak}\n")

        return peak_indices

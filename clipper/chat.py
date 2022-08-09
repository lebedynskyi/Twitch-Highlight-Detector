import logging
import os

logger = logging.getLogger(__name__)


def parse_msg(msg):
    """Breaks a message from an IRC server into its prefix, command, and arguments.
    """
    prefix = ''
    trailing = []
    if not msg:
        raise ValueError("Empty line.")

    if msg[0] == ':':
        prefix, msg = msg[1:].split(' ', 1)
    if msg.find(' :') != -1:
        msg, trailing = msg.split(' :', 1)
        args = msg.split()
        args.append(trailing)
    else:
        args = msg.split()
    command = args.pop(0)
    return prefix, command, args


class TwitchChatRecorder:
    def __init__(self, api, streamer_name, recording_folder):
        self.recording_folder = recording_folder
        self.streamer_name = streamer_name
        self.api = api

    def run(self, file_template):
        file_name = os.path.join(self.recording_folder, f"{file_template}.txt", )
        with open(file_name, "w") as stream:
            def on_message(twitch_msg):
                prefix, command, args = parse_msg(twitch_msg)
                stream.writelines(str(args))

            self.api.start_chat(self.streamer_name, on_message)

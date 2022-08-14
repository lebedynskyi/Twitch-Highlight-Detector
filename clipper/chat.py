import logging
from datetime import datetime

logger = logging.getLogger(__name__)

CHAT_DIVIDER = "<~|~>"


class TwitchChatRecorder:
    is_running = False

    def __init__(self, api, debug=False):
        self.debug = debug
        self.api = api

    def run(self, streamer_name, output_file):
        with open(output_file, "w") as stream:
            def on_message(twitch_msg):
                user, msg = self.parse_msg(twitch_msg)
                if msg:
                    msg_line = f"{str(datetime.now())}{CHAT_DIVIDER}{user}{CHAT_DIVIDER}{msg}"
                    stream.write(msg_line)
                    stream.flush()

                    if self.debug:
                        logger.info("Chat: %s", msg_line)

            self.is_running = True
            self.api.start_chat(streamer_name, on_message)

    def parse_msg(self, msg):
        try:
            return msg[1:].split('!')[0], msg.split(":", 2)[2]
        except BaseException as e:
            return None, None

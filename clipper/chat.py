import logging
from datetime import datetime
import multiprocessing

logger = logging.getLogger(__name__)

CHAT_DIVIDER = "<~|~>"


class TwitchChatRecorder:
    chat_process = None

    def __init__(self, api, debug=False):
        self.debug = debug
        self.api = api

    def run(self, streamer_name, output_file):
        self.chat_process = multiprocessing.Process(target=self._record_chat, args=(streamer_name, output_file))
        self.chat_process.start()

    def stop(self):
        try:
            if self.chat_process:
                self.chat_process.terminate()

            self.chat_process = None
            logger.info("Chat stopped")
        except BaseException as e:
            logger.error("Unable to stop chat")
            logger.error(e)

    def is_running(self):
        return self.chat_process is not None and self.chat_process.is_alive()

    def _record_chat(self, streamer_name, output_file):
        with open(output_file, "w") as stream:
            def on_message(twitch_msg):
                user, msg = self.parse_msg(twitch_msg)
                if msg:
                    msg_line = f"{str(datetime.now())}{CHAT_DIVIDER}{user}{CHAT_DIVIDER}{msg}"
                    stream.write(msg_line)
                    stream.flush()

                    if self.debug:
                        logger.info("Chat: %s", msg_line)

            self.api.start_chat(streamer_name, on_message)

    def parse_msg(self, msg):
        try:
            return msg[1:].split('!')[0], msg.split(":", 2)[2]
        except BaseException as e:
            return None, None

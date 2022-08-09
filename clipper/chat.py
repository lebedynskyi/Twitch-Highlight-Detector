import logging

logger = logging.getLogger(__name__)


class TwitchChatRecorder:
    def __init__(self, api, streamer_name, ignored_prefix=["!"], on_finish=None):
        self.ignored_prefix = ignored_prefix
        self.on_finish = on_finish
        self.streamer_name = streamer_name
        self.api = api

    def run(self):
        self.api.start_chat(self.streamer_name)

    def on_error(self, error):
        logger.error(error)

    def on_message(self, msg):
        logger.info("New message %s", msg)

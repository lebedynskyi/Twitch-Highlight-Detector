import twitch
import logging

logger = logging.getLogger(__name__)


class TwitchChatRecorder:
    def __init__(self, authenticator, streamer_name, on_finish=None):
        self.on_finish = on_finish
        self.streamer_name = streamer_name
        self.authenticator = authenticator

    def run(self):
        chat = twitch.Chat(self.streamer_name, self.authenticator.username, self.authenticator.get_token())
        logger.info("Subscribing to chat for %s as %s", self.streamer_name, self.authenticator.username)
        chat.subscribe(on_next=self.on_message, on_error=self.on_error)

    def on_error(self, error):
        logger.error(error)

    def on_message(self, msg):
        logger.info("New message %s", msg)

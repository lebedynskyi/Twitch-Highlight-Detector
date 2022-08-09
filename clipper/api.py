import enum
import logging
import socket
import time

from twitchAPI import Twitch, AuthScope

logger = logging.getLogger(__name__)

TW_CHAT_SERVER = 'irc.chat.twitch.tv'
TW_CHAT_PORT = 6667


class TwitchStreamStatus(enum.Enum):
    ONLINE = 0
    OFFLINE = 1
    NOT_FOUND = 2
    UNAUTHORIZED = 3
    ERROR = 4


class TwitchApi:
    _cached_token = None

    def __init__(self, client_id, client_secret):
        self.client_id = client_id
        self.client_secret = client_secret
        self.twitch = Twitch(self.client_id, self.client_secret, target_app_auth_scope=[AuthScope.CHAT_READ])
        self.twitch.authenticate_app([AuthScope.CHAT_READ])

    def get_user_status(self, streamer):
        try:
            streams = self.twitch.get_streams(user_login=streamer)
            if streams is None or len(streams) < 1:
                return TwitchStreamStatus.OFFLINE
            else:
                return TwitchStreamStatus.ONLINE
        except:
            return TwitchStreamStatus.ERROR

    def start_chat(self, streamer_name):
        logger.info("Connecting to %s:%s", TW_CHAT_SERVER, TW_CHAT_PORT)
        connection = ChatConnection(streamer_name, self.twitch)

        self.twitch.get_app_token()
        connection.run()


class ChatConnection:
    connection = None

    def __init__(self, streamer_name, twitch):
        self.twitch = twitch
        self.streamer_name = streamer_name

    def run(self):
        # Need to verify channel name.. case sensative
        streams = self.twitch.get_streams(user_login=self.streamer_name)
        if streams is None or len(streams) < 1:
            return

        channel = streams["data"][0]["user_login"]

        self.connection = socket.socket()
        self.connection.connect((TW_CHAT_SERVER, TW_CHAT_PORT))
        self.connection.send(f"PASS sdwrerrwsdawerew\n".encode("utf-8"))
        self.connection.send(f"NICK justinfan123\n".encode("utf-8"))
        self.connection.send(f"JOIN #{channel}\n".encode("utf-8"))

        while True:
            resp = self.connection.recv(4096).decode('utf-8')
            logger.warning(f"Message: {resp}")
            time.sleep(1)


    def disconnect(self, msg="I'll be back!"):
        logger.info("Disconnected  ")

    def on_welcome(self, c, e):
        logger.info("Joining channel ")
        c.join("#" + self.streamer_name)
        logger.info("Joined????? ")

    def on_pubmsg(self, c, e):
        logger.info("On message %s  <->  %s", c, e)

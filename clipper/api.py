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
            if streams is None or len(streams["data"]) < 1:
                return TwitchStreamStatus.OFFLINE
            else:
                return TwitchStreamStatus.ONLINE
        except:
            return TwitchStreamStatus.ERROR

    def start_chat(self, streamer_name, on_message):
        logger.info("Connecting to %s:%s", TW_CHAT_SERVER, TW_CHAT_PORT)
        connection = ChatConnection(streamer_name, self, on_message)

        self.twitch.get_app_token()
        connection.run()

    def get_user_chat_channel(self, streamer_name):
        streams = self.twitch.get_streams(user_login=streamer_name)
        if streams is None or len(streams["data"]) < 1:
            return None
        return streams["data"][0]["user_login"]


class ChatConnection:
    logger = logging.getLogger(__name__)

    connection = None

    def __init__(self, streamer_name, api, on_message):
        self.on_message = on_message
        self.api = api
        self.streamer_name = streamer_name

    def run(self):
        # Need to verify channel name.. case sensitive
        channel = self.api.get_user_chat_channel(self.streamer_name)
        if not channel:
            logger.error("Cannot find streamer channel, Offline?")
            return

        self.connect_to_chat(f"#{channel}")

    def connect_to_chat(self, channel):
        self.connection = socket.socket()
        self.connection.connect((TW_CHAT_SERVER, TW_CHAT_PORT))
        # public data to join hat
        self.connection.send(f"PASS couldBeRandomString\r\n".encode("utf-8"))
        self.connection.send(f"NICK justinfan113\r\n".encode("utf-8"))
        self.connection.send(f"JOIN {channel}\r\n".encode("utf-8"))

        logger.info("Connected to %s", channel)

        try:
            while True:
                msg = self.connection.recv(1024).decode('utf-8')
                if "PING :tmi.twitch.tv" in msg:
                    self.connection.send(bytes("PONG :tmi.twitch.tv\r\n", "UTF-8"))
                    logger.info("RECEIVED Ping from server. Answered")
                    continue
                if self.on_message:
                    self.on_message(msg)
        except BaseException as e:
            logger.error(e)
            logger.error("Error happened during reading chat")

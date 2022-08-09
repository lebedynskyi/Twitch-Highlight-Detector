import argparse
import os
import sys
import logging

from clipper import recorder


def parse_arguments():
    parser = argparse.ArgumentParser(description='Twitch highlighter')
    parser.add_argument('--client', "-c", help='Twitch client id', required=True, dest="tw_client")
    parser.add_argument('--secret', "-s", help='Twitch secret id', required=True, dest="tw_secret")
    parser.add_argument('--streamer', "-t", help='Twitch streamer username', required=True, dest="tw_streamer")
    parser.add_argument('--quality', "-q", help='Video downloading quality', dest="tw_quality", default="360p")
    parser.add_argument('--output_path', "-o", help='Video download folder', dest="output_path",
                        default=os.path.join(os.getcwd(), "recorded"))

    return parser.parse_args()


def on_video_recorded(streamer, filename):
    pass


def on_chat_recorded(streamer, filename):
    pass


if __name__ == "__main__":
    # TODO configure logging
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    args = parse_arguments()

    config = recorder.RecorderConfig(args.tw_client, args.tw_secret, args.tw_streamer, args.tw_quality,
                                     args.output_path)
    recorder = recorder.Recorder(config)
    recorder.run()

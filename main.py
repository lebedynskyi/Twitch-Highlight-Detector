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
    parser.add_argument('--output_path', "-o", help='Video download folder', dest="output_path", default=os.getcwd())

    return parser.parse_args()


def on_video_recorded(streamer, filename):
    pass


def on_chat_recorded(streamer, filename):
    pass


if __name__ == "__main__":
    # TODO configure logging
    # TODO rework authentication and status check. recorder should only record
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    args = parse_arguments()

    config = recorder.RecorderConfig(args.tw_client, args.tw_secret, args.tw_streamer, args.tw_quality, args.output_path)
    recorder = recorder.Recorder(config)
    recorder.run()

# Twitch downloader
# def main(argv):
#     twitch_recorder = TwitchRecorder()
#     usage_message = "twitch-recorder.py -u <username> -q <quality>"
#     logging.basicConfig(filename="twitch-recorder.log", level=logging.INFO)
#     logging.getLogger().addHandler(logging.StreamHandler())
#
#     try:
#         opts, args = getopt.getopt(argv, "hu:q:l:",
#                                    ["username=", "quality=", "log=", "logging=", "disable-ffmpeg", 'uid='])
#     except getopt.GetoptError:
#         print(usage_message)
#         sys.exit(2)
#     print(opts)
#     for opt, arg in opts:
#         if opt == "-h":
#             print(usage_message)
#             sys.exit()
#         elif opt in ("-u", "--username"):
#             twitch_recorder.username = arg
#         elif opt in ("-q", "--quality"):
#             twitch_recorder.quality = arg
#         elif opt in ("-l", "--log", "--logging"):
#             logging_level = getattr(logging, arg.upper(), None)
#             if not isinstance(logging_level, int):
#                 raise ValueError("invalid log level: %s" % logging_level)
#             logging.basicConfig(level=logging_level)
#             logging.info("logging configured to %s", arg.upper())
#         elif opt in "--uid":
#             twitch_recorder.stream_uid = arg
#         elif opt == "--disable-ffmpeg":
#             twitch_recorder.disable_ffmpeg = True
#             logging.info("ffmpeg disabled")
#
#     twitch_recorder.run()
#
#
# if __name__ == "__main__":
#     main(sys.argv[1:])

# # fix videos from previous recording session
#        try:
#            video_list = [f for f in os.listdir(recorded_path) if os.path.isfile(os.path.join(recorded_path, f))]
#            if len(video_list) > 0:
#                logging.info("processing previously recorded files")
#            for f in video_list:
#                recorded_filename = os.path.join(recorded_path, f)
#                processed_filename = os.path.join(processed_path, f)
#                self.process_recorded_file(recorded_filename, processed_filename)
#        except Exception as e:
#            logging.error(e)

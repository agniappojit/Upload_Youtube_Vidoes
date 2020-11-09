from simple_youtube_api.YouTubeVideo import YouTubeVideo
from simple_youtube_api.Channel import Channel
from simple_youtube_api.YouTube import YouTube
from youtube_dl import YoutubeDL

from modules.youtube import (
    is_video_uploaded_on_destination_channel,
    get_channel_videos_list,
)


def pretty_time_delta(seconds):
    seconds = int(seconds)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if days > 0:
        return "%d:%d:%d:%d" % (days, hours, minutes, seconds)
    elif hours > 0:
        return "%d:%d:%d" % (hours, minutes, seconds)
    elif minutes > 0:
        return "%d:%d" % (minutes, seconds)
    else:
        return "%d" % (seconds,)


common_ytdl_opts = {
    "ignoreerrors": True,
    "skip_download": True,
    "quiet": True,
}

extra_ytdl_opts = {
    "dump_single_json": True,
}

ytdl_opts = {**common_ytdl_opts, **extra_ytdl_opts}
ydl = YoutubeDL(ytdl_opts)

channel_uploads_playlist_info = ydl.extract_info(
    "UUo6ncI0ONM6qE4i-GtFYGhA", download=False
)

uploads = {}
for e in channel_uploads_playlist_info["entries"]:
    # skipping deleted videos
    if not e:
        continue

    print(pretty_time_delta(e["duration"]))
    # print(parse_duration(e["duration"]))


# print(
#     str(uploads).replace("'", '"'),
#     file=open("output" + str(extra_ytdl_opts) + ".json", "w"),
# )
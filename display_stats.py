from collections import OrderedDict
import time

from dateutil.parser import parse
import pandas as pd
from tabulate import tabulate
from youtube_dl import YoutubeDL


class StatsLogger(object):
    def debug(self, msg):
        pass

    def warning(self, msg):
        pass

    def error(self, msg):
        pass


common_ytdl_opts = {
    "ignoreerrors": True,
    "skip_download": True,
    "quiet": True,
    "verbose": False,
    # Needed to avoid displaying Errors with extract_info when videos have been deleted
    "logger": StatsLogger(),
}

extra_ytdl_opts = {
    "dump_single_json": True,
}

ytdl_opts = {**common_ytdl_opts, **extra_ytdl_opts}
ytdl = YoutubeDL(ytdl_opts)

ALL_UPLOADS_PLAYLIST_ID = "UUJoZcIAkUodPyA95oOF-ucQ"
channel_uploads_playlist_info = ytdl.extract_info(
    ALL_UPLOADS_PLAYLIST_ID, download=False
)

t = time.time()
todayYYYYMMDD = time.strftime("%Y%m%d", time.localtime(t))

upload_dates_counts_dict = {}
total_uploads_count = 0

for entry in channel_uploads_playlist_info["entries"]:
    # skipping deleted videos
    if not entry:
        continue

    if entry["upload_date"] in upload_dates_counts_dict:
        upload_dates_counts_dict[entry["upload_date"]] += 1
    else:
        upload_dates_counts_dict[entry["upload_date"]] = 1

    total_uploads_count += 1

upload_dates_counts_dict = OrderedDict(sorted(upload_dates_counts_dict.items()))

upload_dates_counts_listoflists = [["Date", "Count"]]

for upload_date, count in upload_dates_counts_dict.items():
    upload_date = parse(upload_date)
    upload_date = upload_date.strftime("%b %d %Y")
    upload_dates_counts_listoflists.append([upload_date, count])

upload_dates_counts_listoflists.append(["TOTAL", total_uploads_count])

print(tabulate(upload_dates_counts_listoflists, headers="firstrow"))
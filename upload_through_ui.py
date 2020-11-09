# Standard library imports
from __future__ import unicode_literals
import argparse
from ftplib import FTP_TLS
import questionary
import os
from os import remove, path
from pathlib import Path
import subprocess
from subprocess import CalledProcessError
import sys
import time
import urllib.request
from urllib.parse import urlparse
from urllib.error import HTTPError
import yaml

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

# Third party imports
from googleapiclient.errors import ResumableUploadError
import gspread
import requests

# User imports
from settings import *

from modules.worksheet import (
    get_worksheet,
    get_start_row_num,
    is_valid_row,
    set_youtube_link_in_google_sheet,
    set_uploaded_in_google_sheet,
    set_status_in_google_sheet,
    set_file_link_in_google_sheet,
    set_all_fields_same_value,
)
from modules.youtube import (
    is_video_uploaded_on_destination_channel,
    get_channel_videos_list,
    extract_youtube_video_id,
    upload_to_youtube,
)

from modules.get_video_file import get_video_file
from modules.run_command import run_command
from modules.set_video_public import set_video_public
from modules.get_video_duration import get_video_duration

# FLOW

# 1. do we have videos in folder? V2
# 2. connect to Google Sheets
# 3. get youtube links of videos already uploaded
# 4. Are all links downloaded?
# 5. No. Download all cells values
# STEP_GET_VIDEO_DATA
# 6. get the next row of the video to download
# 7. extract the metadata from the all cells values data structure for this row
# 8. download the video locally
#
# 9. upload the video with the metadata
# 10. wait for completion of upload
# 11. Write target youtube channel link, status in Google Sheet in corresponding row
# GO BACK TO STEP_GET_VIDEO_DATA

DESTINATION_CHANNELS_NAMES = DESTINATION_CHANNELS_CONFIG.keys()

parser = argparse.ArgumentParser()
parser.add_argument(
    "-d",
    "--dest",
    dest="destination_channel",
    help="Choose a destination channel",
    choices=DESTINATION_CHANNELS_NAMES,
)
parser.add_argument(
    "-n",
    dest="max_video_uploads",
    help="Stops upload process after processing the number of videos specified",
)

args = parser.parse_args()
if not args.destination_channel:
    args.destination_channel = questionary.select(
        "On which channel do you want to upload the videos",
        choices=DESTINATION_CHANNELS_NAMES,
    ).ask()

if not args.destination_channel:
    sys.exit()

DESTINATION_CHANNEL_CONFIG = DESTINATION_CHANNELS_CONFIG[args.destination_channel]
YOUTUBE_CHANNEL_ID = DESTINATION_CHANNEL_CONFIG["id"]
ALL_UPLOADS_PLAYLIST_ID = DESTINATION_CHANNEL_CONFIG["uploads_playlist_id"]
PROGRESS_GOOGLE_SHEET_ID = DESTINATION_CHANNEL_CONFIG[
    "uploads_progress_google_sheet_id"
]
CHANNEL_CREDENTIALS_FILE = CREDENTIALS_FOLDER / (
    "channel_credentials_" + YOUTUBE_CHANNEL_ID + ".json"
)

print(
    "--- Upload videos to " + args.destination_channel.title() + " YouTube channel ---"
)

print("Connecting to Google sheets")
worksheet = get_worksheet(PROGRESS_GOOGLE_SHEET_ID)

print("Getting row start number: ", end="")
current_row_num = get_start_row_num(worksheet)
# current_row_num = worksheet.row_count
print(str(current_row_num))

all_records = worksheet.get_all_records()
current_record_num = current_row_num - 2

i = 0
is_api_upload_limit_exceeded = False

while is_valid_row(current_row_num):
    if args.max_video_uploads and i == args.max_video_uploads:
        sys.exit()

    current_video_metadata = all_records[current_record_num]
    title = current_video_metadata["Title"]

    print()
    print("---------")
    print("Row number " + str(current_row_num))
    print("-")
    print(title)
    print("-")

    if is_video_uploaded_on_destination_channel(YOUTUBE_CHANNEL_ID, title):
        print("Video already on destination channel")

        print("> Google Sheet: Setting destination channel YouTube link", end=" ")
        current_video_id = get_channel_videos_list(ALL_UPLOADS_PLAYLIST_ID)[
            current_video_metadata["Title"]
        ]
        set_youtube_link_in_google_sheet(
            worksheet, current_row_num, "https://youtu.be/" + current_video_id
        )
        print("[DONE]")

        print('> Google Sheet: Setting status to "Uploaded"', end=" ")
        set_uploaded_in_google_sheet(worksheet, current_row_num)
        print("[DONE]")

        current_row_num = current_row_num - 1
        current_record_num = current_record_num - 1
        i += 1
        continue

    source_channel_yt_link = current_video_metadata["Link"]
    print("source: " + source_channel_yt_link)

    print()
    print("Getting video file...")
    try:
        video_file = get_video_file(title, source_channel_yt_link)
    except Exception as e:
        print(str(e))
        print("Check YouTube Video Region Restrictions Online")
        check_restriction_url = (
            "https://watannetwork.com/tools/blocked/#url="
            + extract_youtube_video_id(source_channel_yt_link)
        )
        print(check_restriction_url)
        print(
            '> Google Sheet: Setting "CHECK_SOURCE_VIDEO_RESTRICTIONS" for all fields',
            end=" ",
        )
        set_all_fields_same_value(
            worksheet,
            current_row_num,
            "CHECK_SOURCE_VIDEO_RESTRICTIONS " + check_restriction_url,
        )
        print("[KO]")
        current_row_num = current_row_num - 1
        current_record_num = current_record_num - 1
        i += 1
        continue

    print("> Google Sheet: Setting video file link", end=" ")
    set_file_link_in_google_sheet(
        worksheet,
        current_row_num,
        FTP_PUBLIC_VIDEOS_FOLDER_URL_PATH + video_file["name_with_extension"],
    )
    print("[DONE]")

    print()
    print("Uploading " + video_file["name_with_extension"] + " to YouTube")

    command = (
        "node upload-through-ui.js "
        + "--channel-id "
        + YOUTUBE_CHANNEL_ID
        + " --cookies-file ./studio.youtube.com.cookies."
        + args.destination_channel
        + ".json "
        + "--video-file "
        + str(video_file["path_in_local_folder"])
    )

    return_code, output_lines = run_command(command.split(" "))
    youtube_link = output_lines[len(output_lines) - 1]
    # set_video_public(
    #     CHANNEL_CREDENTIALS_FILE,
    #     extract_youtube_video_id(youtube_link),
    #     title,
    #     current_video_metadata["Description"],
    # )

    youtube_video_id = extract_youtube_video_id(youtube_link)
    if youtube_video_id is None or youtube_video_id == "":
        print("Error while retrieving YouTube video link")
        print('text provided as "link":')
        print(youtube_link)
        current_row_num = current_row_num - 1
        current_record_num = current_record_num - 1
        i += 1
        continue

    print("> Google Sheet: Setting destination channel YouTube link", end=" ")
    set_youtube_link_in_google_sheet(worksheet, current_row_num, youtube_link)
    print("[DONE]")

    print('> Google Sheet: Setting status to "draft"', end=" ")
    set_status_in_google_sheet(worksheet, current_row_num, "draft")
    print("[DONE]")

    print("Removing the file from local folder", end=" ")
    os.remove(video_file["path_in_local_folder"])
    print("[DONE]")

    current_row_num = current_row_num - 1
    current_record_num = current_record_num - 1
    i += 1

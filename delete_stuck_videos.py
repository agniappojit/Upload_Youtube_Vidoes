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
    get_draft_start_row_num,
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
from modules.status import get_status
from modules.delete_video import delete_video

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

print("Getting max row start number: ", end="")
# current_row_num = worksheet.row_count
current_row_num = 4331
print(current_row_num)

print("Get all records...", end=" ")
all_records = worksheet.get_all_records()
print("[DONE]")
current_record_num = current_row_num - 2

i = 0
is_api_upload_limit_exceeded = False

while is_valid_row(current_row_num):
    if args.max_video_uploads and i == args.max_video_uploads:
        sys.exit()

    current_video_metadata = all_records[current_record_num]
    title = current_video_metadata["Title"]

    # print("Row number " + str(current_row_num))

    if current_video_metadata["HPedia YouTube link"] == "":
        current_row_num = current_row_num - 1
        current_record_num = current_record_num - 1
        i += 1
        continue

    youtube_video_id = extract_youtube_video_id(
        current_video_metadata["HPedia YouTube link"]
    )

    if youtube_video_id is None:
        # TODO handle CHECK_SOURCE_VIDEO_RESTRICTIONS videos
        # print("Video not uploaded")
        current_row_num = current_row_num - 1
        current_record_num = current_record_num - 1
        i += 1
        continue

    status = get_status(CHANNEL_CREDENTIALS_FILE, youtube_video_id)
    uploadStatus = status["uploadStatus"]

    if uploadStatus == "processed":
        print(str(current_row_num), end=" ")
        sys.stdout.flush()
        current_row_num = current_row_num - 1
        current_record_num = current_record_num - 1
        i += 1
        continue

    print()
    print(str(current_row_num))
    print("upload status: ", end="")
    print(status["uploadStatus"])

    if uploadStatus == "deleted":
        print("> Google Sheet: Removing status...", end=" ")
        set_status_in_google_sheet(worksheet, current_row_num, "")
        print("[DONE]")

        print("> Google Sheet: Removing destination channel YouTube link...", end=" ")
        set_youtube_link_in_google_sheet(worksheet, current_row_num, "")
        print("[DONE]")
        current_row_num = current_row_num - 1
        current_record_num = current_record_num - 1
        i += 1
        continue

    processing_status = status["processingStatus"]
    if uploadStatus == "uploaded" and processing_status == "processing":
        command = (
            "node get-upload-status.js "
            + " --cookies-file ./studio.youtube.com.cookies."
            + args.destination_channel
            + ".json "
            + "--video-id "
            + str(youtube_video_id)
        )

        return_code, output_lines = run_command(command.split(" "))
        video_status = output_lines[len(output_lines) - 1]

        if video_status == "uploading" or video_status == "processing":
            print(
                "> Deleting " + current_video_metadata["HPedia YouTube link"] + " ...",
                end=" ",
            )

            if not delete_video(CHANNEL_CREDENTIALS_FILE, youtube_video_id):
                print("[ERROR]")
                current_row_num = current_row_num - 1
                current_record_num = current_record_num - 1
                i += 1
                continue

            print("[DONE]")

            print("> Google Sheet: Removing status...", end=" ")
            set_status_in_google_sheet(worksheet, current_row_num, "")
            print("[DONE]")

            print(
                "> Google Sheet: Removing destination channel YouTube link...", end=" "
            )
            set_youtube_link_in_google_sheet(worksheet, current_row_num, "")
            print("[DONE]")

        current_row_num = current_row_num - 1
        current_record_num = current_record_num - 1
        i += 1
        continue

    if "processingStatus" in status:
        print("processing status: ", end="")
        print(status["processingStatus"])

    current_row_num = current_row_num - 1
    current_record_num = current_record_num - 1
    i += 1
    time.sleep(2)
    continue

    if status not in ["processing", "deleted"]:
        input("Press Enter to continue...")
        sys.exit()

    command = (
        "node get-upload-status.js "
        + " --cookies-file ./studio.youtube.com.cookies."
        + args.destination_channel
        + ".json "
        + "--video-id "
        + str(youtube_video_id)
    )

    return_code, output_lines = run_command(command.split(" "))
    video_status = output_lines[len(output_lines) - 1]

    if video_status not in ["uploading", "removed", "unavailable", "processing"]:
        input("Press Enter to continue...")
        current_row_num = current_row_num - 1
        current_record_num = current_record_num - 1
        i += 1
        continue

    if video_status == "uploading":
        print(
            "> Deleting " + current_video_metadata["HPedia YouTube link"] + " ...",
            end=" ",
        )

        if not delete_video(CHANNEL_CREDENTIALS_FILE, youtube_video_id):
            print("[ERROR]")
            current_row_num = current_row_num - 1
            current_record_num = current_record_num - 1
            i += 1
            continue

        print("[DONE]")

    print("> Google Sheet: Removing status...", end=" ")
    set_status_in_google_sheet(worksheet, current_row_num, "")
    print("[DONE]")

    print("> Google Sheet: Removing destination channel YouTube link...", end=" ")
    set_youtube_link_in_google_sheet(worksheet, current_row_num, "")
    print("[DONE]")

    current_row_num = current_row_num - 1
    current_record_num = current_record_num - 1
    i += 1

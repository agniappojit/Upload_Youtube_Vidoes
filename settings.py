from pathlib import Path

# Folders
LOCAL_VIDEOS_FOLDER_PATH = Path("./videos/")
CREDENTIALS_FOLDER = Path("./credentials/")


# FTP
FTP_HOST = "sripriyesha.com"
FTP_LOGIN = "ntvarchives@ntvarchives.sripriyesha.com"
FTP_PASSWORD = "W(wrQ}a~@'bg2fg9b2@vCN:Ad6(]"
FTP_PUBLIC_VIDEOS_FOLDER_URL_PATH = "https://ntvarchives.sripriyesha.com/videos/"

# Worksheet
# gspread: read, update google sheet
GSPREAD_SERVICE_ACCOUNT_FILE = CREDENTIALS_FOLDER / "gspread_service_account.json"
# Sri Nithya Priyeshananda's Google Api Key for gspread
API_KEY_GOOGLE = "AIzaSyBK3ozMZg05M8q9ryLjsb2xm4DbYoNjYpg"

# Youtube
# Secret file used by YT-Porting Google Developers Console App
# See with Sri Sadashivamaya
CLIENT_SECRET_FILE = (
    CREDENTIALS_FOLDER
    / "client_secret_911040133095-q2dq6cph2rfito618pctmlu66hajnup4.apps.googleusercontent.com.json"
)
URL_YOUTUBE_API_VIDEOS = "https://www.googleapis.com/youtube/v3/videos"

DESTINATION_CHANNELS_CONFIG = {
    "nithyanandapedia": {
        "id": "UCJoZcIAkUodPyA95oOF-ucQ",
        "uploads_playlist_id": "UUJoZcIAkUodPyA95oOF-ucQ",
        "uploads_progress_google_sheet_id": "18LG9ObPpzgRzjumq_NhmRysQYw_0mROkmwuK3ds06zI",
    },
    "hinduismpedia": {
        "id": "UCv9RGgBGA9JccpynizPFXiQ",
        "uploads_playlist_id": "UUv9RGgBGA9JccpynizPFXiQ",
        "uploads_progress_google_sheet_id": "1JxBR6hPLN-ptSgnJKSeQuxrw1edB0wwEKDa27Zl4X6A",
    },
    "kailasapedia": {
        "id": "UCQ821ncUTmeuTwAsycMhTdw",
        "uploads_playlist_id": "UUQ821ncUTmeuTwAsycMhTdw",
        "uploads_progress_google_sheet_id": "1wtX9GcuLl_mAuiTCbip9laV7RQEsY-VS3Rfr5zWrEOs",
    },
}

UPLOAD_LIMIT_EXCEEDED_ERROR = (
    "The user has exceeded the number of videos they may upload."
)

# Enable and change URL if Zapier used
# ZAPIER_UPLOAD_TO_YOUTUBE_WEBHOOK_URL = (
#     "https://hooks.zapier.com/hooks/catch/8063241/owt0hwf"
# )

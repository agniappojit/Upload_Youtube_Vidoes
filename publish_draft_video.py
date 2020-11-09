from simple_youtube_api.YouTubeVideo import YouTubeVideo
from simple_youtube_api.Channel import Channel
from simple_youtube_api.YouTube import YouTube


# youtube = YouTube()
# # API KEY
# youtube.login("AIzaSyBK3ozMZg05M8q9ryLjsb2xm4DbYoNjYpg")

# video = youtube.search_by_video_id("hAvdYjkhIe0")

channel = Channel()
channel.login(
    "./credentials/client_secret_911040133095-q2dq6cph2rfito618pctmlu66hajnup4.apps.googleusercontent.com",
    "./credentials/channel_credentials_UCJoZcIAkUodPyA95oOF-ucQ.json",
)

response = (
    channel.get_login()
    .videos()
    .update(
        body={
            "id": "w6B6fMwAm5w",
            "snippet": {
                "title": "Pranayama for Gradual Kundalini Awakening Patanjali Yoga Sutras 101 Nithyananda satsang 24 Jan 2011",
                "description": """This was the 3rd day of the Pranayama discourse by Paramahamsa Nithyananda.  He went deeper into the sutra. Yesterday's technique was for Instant Enlightenment - Whether breathing is going in, out, whatever time or space, if it is creating a thought - stop it. The negative aspect of this is, if your body is not ready for this, you may get frustrated. So the next technique - Don't stop the breathing - If you can't stop the breathing, at least elongate it! Whether it is inhaling, exhaling, holding, whenever you notice that a thought is created - elongate the breathing. This is the technique for gradual enlightenment. This will work for everyone. But it will take time. 

Elongate breathing and you will experience Enlightenment.

Paramashivoham: 22-day Ultimate Spiritual Journey with the Avatar HDH Nithyananda Paramashivam 
Learn more: https://paramashivoham.nithyananda.org""",
                "categoryId": 29,
            },
            "status": {"privacyStatus": "public"},
        },
        part="snippet,status",
    )
    .execute()
)


# video.update(channel, status={"privacyStatus": "public"})

# res = (
#     youtube.youtube.playlistItems()
#     .list(playlistId="UUJoZcIAkUodPyA95oOF-ucQ", part="snippet,status", maxResults=50)
#     .execute()
# )
# )

# print(res)

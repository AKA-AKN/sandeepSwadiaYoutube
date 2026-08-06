import os
from googleapiclient.discovery import build
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("YOUTUBE_API_KEY")

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)


def get_channel_id(username: str):
    username = username.replace("@", "")

    request = youtube.search().list(
        part="snippet",
        q=username,
        type="channel",
        maxResults=1
    )

    response = request.execute()

    items = response.get("items", [])

    if not items:
        raise Exception("Channel not found")

    return items[0]["snippet"]["channelId"]


def get_channel_stats(channel_id):
    request = youtube.channels().list(
        part="snippet,statistics,contentDetails",
        id=channel_id
    )

    response = request.execute()

    return response["items"][0]


def get_upload_playlist(channel):
    return channel["contentDetails"]["relatedPlaylists"]["uploads"]


def get_recent_videos(playlist_id):
    """
    Fetch EVERY upload from the channel.
    """

    video_ids = []

    next_page = None

    while True:

        request = youtube.playlistItems().list(
            part="contentDetails",
            playlistId=playlist_id,
            maxResults=50,
            pageToken=next_page
        )

        response = request.execute()

        for item in response["items"]:
            video_ids.append(
                item["contentDetails"]["videoId"]
            )

        next_page = response.get("nextPageToken")

        if next_page is None:
            break

    return video_ids

def get_video_statistics(video_ids):

    all_videos = []

    for i in range(0, len(video_ids), 50):

        ids = ",".join(video_ids[i:i+50])

        request = youtube.videos().list(
            part="snippet,statistics",
            id=ids,
            maxResults=50
        )

        response = request.execute()

        all_videos.extend(response["items"])

    return all_videos
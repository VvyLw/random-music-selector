from flask import Flask, render_template
import random
import googleapiclient.discovery
import os
from dotenv import load_dotenv

app = Flask(__name__)

def get_random_video_from_playlist(api_key, playlist_id):
    youtube = googleapiclient.discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=999,
        playlistId=playlist_id
    )
    response = request.execute()
    items = response.get('items', [])
    if not items: return None
    filtered_items = []
    for item in items:
        video_title = item['snippet']['title']
        video_id = item['snippet']['resourceId']['videoId']
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        video_request = youtube.videos().list(
            part='status'
            id=video_id
        )
        video_response = video_request.execute()
        video_status = video_response['items'][0]['status']['privacyStatus']
        if video_status == 'private': continue
        filtered_items.append(items)
    random_video = random.choice(filtered_items)
    video_title = random_video['snippet']['title']
    video_id = random_video['snippet']['resourceId']['videoId']
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    return video_title, video_url

def get_random_video_from_multiple_playlists(api_key, playlist_ids):
    selected_videos = []
    for playlist_id in playlist_ids:
        video = get_random_video_from_playlist(api_key, playlist_id)
        if video: selected_videos.append(video)
    if not selected_videos: return None
    return random.choice(selected_videos)

@app.route('/')
def index():
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    playlist_ids = [
        "PLNnw2DXHmqD80GWMOKoJu4tL3BEHb18aX",   # Music 1
        "PLNnw2DXHmqD9p9jbbfpLXgA24ONtrWKst"    # Music 2
    ]
    video = get_random_video_from_multiple_playlists(api_key, playlist_ids)
    if video:
        video_title, video_url = video
        return render_template('index.html', video_title=video_title, video_url=video_url)
    else: return render_template('index.html', error="No video found in the provided playlists.")

if __name__ == "__main__":
    app.run(debug=False)
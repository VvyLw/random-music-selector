from flask import Flask, render_template
import random
from googleapiclient import discovery
import os
from dotenv import load_dotenv
import time

app = Flask(__name__)
cache = {}
deadline = 3 * 24 * 60 * 60

def get_cached_videos(api_key, playlist_id):
    now = time.time()
    if playlist_id in cache:
        cache_entry = cache[playlist_id]
        if now - cache_entry['timestamp'] < deadline: return cache_entry['videos']
    videos = get_videos_from_playlist(api_key, playlist_id)
    cache[playlist_id] = {
        'videos': videos,
        'timestamp': now
    }
    return videos

def get_videos_from_playlist(api_key, playlist_id):
    youtube = discovery.build("youtube", "v3", developerKey=api_key)
    request = youtube.playlistItems().list(
        part="snippet",
        maxResults=999,
        playlistId=playlist_id
    )
    response = request.execute()
    videos = response.get('items', [])
    if not videos:
        print(f"Void playlist: {playlist_id}")
        return None
    filtered_videos = []
    for video in videos:
        video_title = video['snippet']['title']
        video_id = video['snippet']['resourceId']['videoId']
        video_request = youtube.videos().list(
            part='status',
            id=video_id
        )
        video_response = video_request.execute()
        if not video_response.get('items', []): continue
        video_status = video_response['items'][0]['status']['privacyStatus']
        if video_status == 'private': continue
        filtered_videos.append((video_title, video_id))
    if filtered_videos: return filtered_videos
    else:
        print("No more available videos")
        return None

def get_random_video(api_key, playlist_ids):
    videos = []
    for playlist_id in playlist_ids:
        temp = get_cached_videos(api_key, playlist_id)
        if temp: videos.extend(temp)
    if not videos: return None
    return random.choice(videos)

@app.route('/')
def index():
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")
    playlist_ids = [
        "PLNnw2DXHmqD80GWMOKoJu4tL3BEHb18aX",   # Music 1
        "PLNnw2DXHmqD9p9jbbfpLXgA24ONtrWKst",   # Music 2
        "PLNnw2DXHmqD8ea-gGyC0uZdGufJrlbhHy",   # Vocaloid
    ]
    video = get_random_video(api_key, playlist_ids)
    if video:
        video_title, video_id = video
        return render_template('index.html', video_title=video_title, video_id=video_id)
    else: return render_template('index.html', error="No video found in the provided playlists.")

if __name__ == "__main__": app.run(debug=False)
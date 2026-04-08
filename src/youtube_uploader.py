"""
YouTube Uploader untuk Anime Shorts Generator
Menggunakan OAuth refresh token yang disimpan di GitHub Secrets
"""
import os
import json
import datetime
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request


def get_credentials():
    """
    Ambil credentials dari environment variable YOUTUBE_TOKEN_JSON.
    Format JSON berisi: client_id, client_secret, refresh_token
    """
    token_json = os.getenv("YOUTUBE_TOKEN_JSON")
    if not token_json:
        raise EnvironmentError(
            "YOUTUBE_TOKEN_JSON tidak ditemukan di environment.\n"
            "Jalankan: python setup_youtube_token.py\n"
            "Lalu copy output JSON-nya ke GitHub Secrets."
        )

    token_data = json.loads(token_json)

    creds = Credentials(
        token=None,
        refresh_token=token_data["refresh_token"],
        client_id=token_data["client_id"],
        client_secret=token_data["client_secret"],
        token_uri="https://oauth2.googleapis.com/token",
        scopes=["https://www.googleapis.com/auth/youtube.upload"],
    )

    creds.refresh(Request())
    return creds


def upload_to_youtube(video_path, title=None, description=None, tags=None):
    """
    Upload video ke YouTube.

    Args:
        video_path: Path ke file MP4
        title: Judul video (auto-generate jika None)
        description: Deskripsi video
        tags: List tag video
    """
    if not os.path.exists(video_path):
        raise FileNotFoundError(f"File video tidak ditemukan: {video_path}")

    print(f"[YT] Menghubungkan ke YouTube...")
    creds = get_credentials()
    youtube = build("youtube", "v3", credentials=creds)

    if title is None:
        title = "Anime Facts You Didn't Know 🔥 #shorts"

    if description is None:
        description = (
            "#shorts #anime #animefacts\n\n"
            "🔥 Did you know this about anime? Mind-blowing facts from Naruto, One Piece, and Attack on Titan!\n\n"
            "👉 Subscribe for daily anime facts!\n"
            "🔔 Turn on notifications so you never miss a video!\n\n"
            "📌 Tags:\n"
            "#anime #naruto #onepiece #attackontitan #animeshorts "
            "#animefacts #didyouknow #animetrivia #otaku #animelover"
        )

    if tags is None:
        tags = [
            "anime", "anime facts", "did you know anime",
            "naruto facts", "one piece facts", "attack on titan facts",
            "anime shorts", "anime trivia", "otaku", "anime lover",
            "anime 2024", "shorts", "viral anime", "anime moments",
            "animefacts"
        ]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "24",
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",
            "selfDeclaredMadeForKids": False,
            "madeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 5,
    )

    print(f"[YT] Mengupload: {title}")
    request = youtube.videos().insert(
        part="snippet,status",
        body=body,
        media_body=media,
    )

    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            pct = int(status.progress() * 100)
            print(f"[YT] Upload progress: {pct}%")

    video_id = response.get("id")
    print(f"[YT] ✅ Upload berhasil!")
    print(f"[YT] 🔗 https://www.youtube.com/watch?v={video_id}")
    return video_id

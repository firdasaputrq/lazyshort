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

    # Refresh token untuk dapat access token baru
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

    # Auto-generate title dengan tanggal jika tidak disediakan
    today = datetime.datetime.now().strftime("%B %d, %Y")
    if title is None:
        title = f"Did You Know? Anime Facts | {today} #shorts"

    if description is None:
        description = (
            "Amazing anime facts you probably didn't know! 🔥\n\n"
            "#anime #animefacts #didyouknow #shorts #naruto #onepiece #attackontitan\n\n"
            "Subscribe for daily anime content! 🔔"
        )

    if tags is None:
        tags = [
            "anime", "animefacts", "didyouknow", "shorts",
            "naruto", "onepiece", "attackontitan", "animeshorts",
            "animetrivia", "funfacts"
        ]

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags,
            "categoryId": "24",  # Entertainment
            "defaultLanguage": "en",
        },
        "status": {
            "privacyStatus": "public",  # Ganti ke "private" untuk test dulu
            "selfDeclaredMadeForKids": False,
            "madeForKids": False,
        },
    }

    media = MediaFileUpload(
        video_path,
        mimetype="video/mp4",
        resumable=True,
        chunksize=1024 * 1024 * 5,  # 5MB per chunk
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

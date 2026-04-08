"""
Script untuk generate YouTube OAuth token di lokal.
Jalankan SEKALI di PC kamu, lalu copy output-nya ke GitHub Secrets.

Cara pakai:
1. Buka https://console.cloud.google.com/
2. Buat project baru (atau pakai yang ada)
3. Enable "YouTube Data API v3"
4. Buat OAuth 2.0 Client ID (tipe: Desktop app)
5. Download client_secret.json
6. Jalankan: python setup_youtube_token.py
7. Login Google di browser yang muncul
8. Copy output JSON ke GitHub Secret: YOUTUBE_TOKEN_JSON
"""

import json
import os
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def main():
    print("=" * 60)
    print("  Setup YouTube OAuth Token")
    print("=" * 60)
    print()

    client_secret_path = "client_secret.json"
    if not os.path.exists(client_secret_path):
        print(f"[ERROR] File '{client_secret_path}' tidak ditemukan!")
        print()
        print("Langkah:")
        print("1. Buka https://console.cloud.google.com/")
        print("2. APIs & Services → Credentials")
        print("3. Create Credentials → OAuth Client ID → Desktop App")
        print("4. Download JSON → simpan sebagai 'client_secret.json'")
        print("   di folder project ini")
        return

    flow = InstalledAppFlow.from_client_secrets_file(client_secret_path, SCOPES)
    
    print("Browser akan terbuka untuk login Google...")
    print("Pilih akun YouTube channel kamu.")
    print()
    
    creds = flow.run_local_server(port=0)

    # Baca client_id dan client_secret dari file
    with open(client_secret_path) as f:
        client_data = json.load(f)
    
    client_info = client_data.get("installed") or client_data.get("web", {})

    token_data = {
        "client_id": client_info["client_id"],
        "client_secret": client_info["client_secret"],
        "refresh_token": creds.refresh_token,
    }

    token_json = json.dumps(token_data)

    print()
    print("=" * 60)
    print("  ✅ Token berhasil digenerate!")
    print("=" * 60)
    print()
    print("Copy teks di bawah ini ke GitHub Secret bernama: YOUTUBE_TOKEN_JSON")
    print()
    print("-" * 60)
    print(token_json)
    print("-" * 60)
    print()
    print("Cara tambah GitHub Secret:")
    print("  Repo → Settings → Secrets and variables → Actions → New secret")
    print("  Name: YOUTUBE_TOKEN_JSON")
    print("  Value: (paste JSON di atas)")
    
    # Juga simpan ke file lokal untuk backup
    with open("youtube_token.json", "w") as f:
        json.dump(token_data, f, indent=2)
    print()
    print("Token juga disimpan lokal di: youtube_token.json")
    print("(JANGAN commit file ini ke GitHub!)")


if __name__ == "__main__":
    main()

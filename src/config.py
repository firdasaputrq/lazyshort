import os
from dotenv import load_dotenv

load_dotenv()

# API Keys - hanya Gemini yang dibutuhkan (GRATIS)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# TTS Voice (edge-tts) - bisa diganti sesuai selera
# Daftar voice: jalankan `edge-tts --list-voices` di terminal
TTS_VOICE = os.getenv("TTS_VOICE", "en-US-GuyNeural")

# Paths
SCRIPT_PATH = os.path.join("input", "script.txt")
IMAGE_DIR = os.path.join("input", "images")
AUDIO_DIR = "audio"
OUTPUT_PATH = os.path.join("output", "final_video.mp4")

# Ensure necessary directories exist
os.makedirs(IMAGE_DIR, exist_ok=True)
os.makedirs(AUDIO_DIR, exist_ok=True)
os.makedirs(os.path.dirname(SCRIPT_PATH), exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

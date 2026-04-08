import os
import re
import time
from google import genai
from src.config import GEMINI_API_KEY, SCRIPT_PATH

def generate_anime_script():
    print("Gemini key length:", len(GEMINI_API_KEY))
    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY tidak ditemukan. Daftar gratis di https://aistudio.google.com/apikey"
        )
    client = genai.Client(api_key=GEMINI_API_KEY)
    user_prompt = (
        "You are a scriptwriter for short-form anime trivia content. "
        "Write a 60-second 'Did You Know?' style script about ONE surprising fact from Naruto, One Piece, or Attack on Titan. "
        "Structure the script as alternating lines:\n\n"
        "[image search prompt]\n"
        "narration sentence\n\n"
        "Rules:\n"
        "- Total 10-12 lines\n"
        "- Each image prompt must be specific but searchable\n"
        "- Use character names, actions, or objects\n"
        "- No intros, no outros, no narrator labels\n"
        "- Focus only on the trivia fact\n\n"
        "Example prompts:\n"
        "[naruto young sasuke with family]\n"
        "[one piece luffy showing scar]\n"
        "[attack on titan zeke yelling]"
    )
    response = None
    models_to_try = [
    "gemini-2.0-flash-lite",
    "gemini-2.0-flash",
    "gemini-2.5-flash-preview-05-20",
    ]
    for model_name in models_to_try:
        print(f"Mencoba model: {model_name}")
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=user_prompt
                )
                print(f"[OK] Berhasil dengan model: {model_name}")
                break
            except Exception as e:
                err_str = str(e)
                print(f"Gemini error ({model_name}, attempt {attempt+1}): {err_str[:200]}")
                if "404" in err_str or "NOT_FOUND" in err_str:
                    break
                elif "limit: 0" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                    time.sleep(5)
                    if attempt >= 1:
                        break
                else:
                    time.sleep(15)
        if response is not None:
            break
    if response is None:
        raise RuntimeError(
            "Semua model Gemini gagal.\n"
            "Solusi:\n"
            "1. Buka https://aistudio.google.com/apikey - pastikan API key aktif\n"
            "2. Quota free tier reset setiap hari, coba lagi besok\n"
            "3. Atau buat API key baru dari Google account lain"
        )
    script_text = response.text.strip()
    script_text = re.sub(r"(\[[^\]]+\])\s+(?!\n)", r"\1\n", script_text)
    os.makedirs(os.path.dirname(SCRIPT_PATH), exist_ok=True)
    with open(SCRIPT_PATH, "w", encoding="utf-8") as f:
        f.write(script_text)
    print(f"[OK] Script berhasil digenerate: {SCRIPT_PATH}")

def clean_prompt(raw):
    raw = raw.strip("[]")
    for prefix in ["Scene:", "Final shot:", "Opening:", "Shot:"]:
        if raw.lower().startswith(prefix.lower()):
            return raw[len(prefix):].strip()
    return raw

def parse_script(script_path):
    with open(script_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
    if len(lines) % 2 != 0:
        raise ValueError("Script should have even number of lines.")
    return [(clean_prompt(lines[i]), lines[i+1]) for i in range(0, len(lines), 2)]

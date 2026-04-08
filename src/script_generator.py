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
        "- Total 10–12 lines\n"
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

    # retry jika Gemini error / quota sementara
    for i in range(5):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash",
                contents=user_prompt
            )
            break
        except Exception as e:
            print("Gemini error:", e)
            time.sleep(15)

    if response is None:
        raise RuntimeError("Gemini gagal setelah 5 percobaan")

    script_text = response.text.strip()

    # memastikan format [image] berada di baris sendiri
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

import os
import re
import google.generativeai as genai
from src.config import GEMINI_API_KEY, SCRIPT_PATH


def generate_anime_script():
    if not GEMINI_API_KEY:
        raise EnvironmentError(
            "GEMINI_API_KEY tidak ditemukan. Daftar gratis di https://aistudio.google.com/apikey"
        )

    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        system_instruction=(
            "You are a scriptwriter for short-form anime trivia content. Your job is to write 60-second 'Did You Know?' style scripts for fans of ONE specific anime (Naruto, One Piece, or Attack on Titan). "
            "Each script should focus on one obscure, surprising, or strange fact — not a summary or moral. "
            "Structure the script as ~10-12 alternating lines: one image tag in square brackets, followed by one narration sentence. "
            "Each [image description] should be specific enough to help find a relevant image, but not so specific it becomes too rare or obscure. "
            "Use terms like character names, key objects, expressions, or settings (e.g., [one piece young luffy with dagger], [attack on titan eren touching basement key]). "
            "Avoid overly long tags or deep cut scene references. Keep tags searchable. "
            "No 'Narrator:' labels. No summaries, no morals, no intros or outros - only focused trivia with matching visual tags."
        ),
    )

    user_prompt = (
        "Write a short anime 'Did You Know?' video script focused on one obscure or surprising fact from Naruto, One Piece, or Attack on Titan. "
        "Pick just one fact and expand on it using multiple angles. "
        "Structure the script as alternating lines of [image search prompt] and a short narration sentence. "
        "Each image prompt should include character names, context, or actions - but stay reasonably general and searchable "
        "(e.g., [one piece luffy showing scar], [naruto young sasuke with family], [attack on titan zeke yelling]). "
        "Do not use vague prompts like [anime scene] or [battle shot], but also don't go too narrow. "
        "Keep it 10-12 lines total, no intro/outro."
    )

    response = model.generate_content(user_prompt)
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
    with open(script_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    if len(lines) % 2 != 0:
        raise ValueError("Script should have even number of lines.")
    return [(clean_prompt(lines[i]), lines[i+1]) for i in range(0, len(lines), 2)]

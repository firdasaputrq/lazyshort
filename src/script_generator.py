import os
import re
from groq import Groq
from src.config import SCRIPT_PATH

def generate_anime_script():
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise EnvironmentError("GROQ_API_KEY tidak ditemukan.")

    client = Groq(api_key=api_key)

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

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": user_prompt}],
        max_tokens=1000,
    )

    script_text = response.choices[0].message.content.strip()
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
        raw_lines = [line.strip() for line in f if line.strip()]

    # Pisahkan baris [image] dan narasi
    image_lines = []
    narration_lines = []

    i = 0
    while i < len(raw_lines):
        line = raw_lines[i]
        if line.startswith("[") and line.endswith("]"):
            image_lines.append(line)
            # Ambil baris berikutnya sebagai narasi
            if i + 1 < len(raw_lines):
                next_line = raw_lines[i + 1]
                if not (next_line.startswith("[") and next_line.endswith("]")):
                    narration_lines.append(next_line)
                    i += 2
                    continue
                else:
                    # Dua [image] berturut-turut, skip yang kedua
                    narration_lines.append("...")
                    i += 1
                    continue
            else:
                narration_lines.append("...")
                i += 1
        else:
            i += 1

    # Pastikan jumlah seimbang
    min_len = min(len(image_lines), len(narration_lines))
    pairs = [(clean_prompt(image_lines[j]), narration_lines[j]) for j in range(min_len)]

    if not pairs:
        raise ValueError("Script tidak valid: tidak ada pasangan [image] + narasi.")

    return pairs

import asyncio
import os
import time

def generate_tts(text, path, max_retries=3):
    """Generate TTS dengan retry. Fallback ke gTTS jika edge-tts gagal."""
    for attempt in range(1, max_retries + 1):
        try:
            asyncio.run(_generate_tts_async(text, path))
            if os.path.exists(path) and os.path.getsize(path) > 0:
                print(f"[OK] TTS digenerate: {path}")
                return []
        except Exception as e:
            print(f"[WARN] edge-tts gagal (percobaan {attempt}): {e}")
            if os.path.exists(path):
                os.remove(path)
            if attempt < max_retries:
                time.sleep(2)

    # Fallback ke gTTS
    print(f"[FALLBACK] Mencoba gTTS untuk: {path}")
    try:
        from gtts import gTTS
        tts = gTTS(text=text, lang="en", slow=False)
        tts.save(path)
        if os.path.exists(path) and os.path.getsize(path) > 0:
            print(f"[OK] gTTS berhasil: {path}")
            return []
    except Exception as e:
        print(f"[ERROR] gTTS juga gagal: {e}")
        raise RuntimeError(f"Semua TTS gagal untuk: {path}")

async def _generate_tts_async(text, path):
    import edge_tts
    communicate = edge_tts.Communicate(text, voice="en-US-AriaNeural")
    await communicate.save(path)

import os
import asyncio
import edge_tts
from src.config import TTS_VOICE


def generate_tts(text, path):
    """Generate TTS audio menggunakan edge-tts (GRATIS, tanpa API key)."""
    os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)
    asyncio.run(_generate_tts_async(text, path))
    # edge-tts tidak mengembalikan word timings, return list kosong
    return []


async def _generate_tts_async(text, path):
    communicate = edge_tts.Communicate(text, TTS_VOICE)
    await communicate.save(path)
    print(f"[OK] TTS digenerate: {path}")

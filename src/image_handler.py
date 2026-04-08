import os
import requests
import time
from PIL import Image
from duckduckgo_search import DDGS


def fetch_image_url(query, max_attempts=5):
    """Cari gambar gratis via DuckDuckGo (tanpa API key)."""
    print(f"[IMG] Mencari gambar untuk: '{query}'")

    for search_query in (query, "anime background art"):
        try:
            with DDGS() as ddgs:
                results = list(ddgs.images(
                    keywords=search_query,
                    type_image="photo",
                    max_results=max_attempts * 2,
                ))

            for item in results[:max_attempts]:
                url = item.get("image")
                if not url:
                    continue
                try:
                    r = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
                    content_type = r.headers.get("Content-Type", "")
                    if content_type.startswith("image"):
                        print(f"[OK] Gambar ditemukan: {url}")
                        return url
                except Exception as e:
                    print(f"[SKIP] Gagal validasi: {e}")
                    continue

        except Exception as e:
            print(f"[WARN] DuckDuckGo search gagal untuk '{search_query}': {e}")
            time.sleep(1)
            continue

    raise ValueError(f"Tidak ada gambar ditemukan untuk '{query}'")


def download_image(image_url, save_path, original_prompt=None, max_attempts=5):
    current_url = image_url
    for attempt in range(1, max_attempts + 1):
        print(f"[DL] Download gambar (percobaan {attempt}): {current_url}")
        try:
            r = requests.get(current_url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            content_type = r.headers.get("Content-Type", "")
            if not content_type.startswith("image"):
                raise ValueError(f"Bukan gambar: {content_type}")

            with open(save_path, "wb") as f:
                f.write(r.content)

            if not is_valid_image(save_path):
                raise ValueError("File gambar tidak valid")

            print(f"[OK] Gambar tersimpan: {save_path}")
            return

        except Exception as e:
            print(f"[RETRY] Download gagal: {e}")
            if os.path.exists(save_path):
                os.remove(save_path)
            if attempt == max_attempts:
                raise RuntimeError(f"Download gagal setelah {max_attempts} percobaan untuk '{original_prompt or current_url}'")

            retry_prompt = original_prompt if original_prompt else "anime background"
            current_url = fetch_image_url(retry_prompt)


def is_valid_image(path):
    try:
        with Image.open(path) as img:
            img.verify()
        return True
    except Exception as e:
        print(f"[INVALID] Gambar tidak valid di {path}: {e}")
        return False

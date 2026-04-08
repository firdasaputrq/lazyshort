import os
import requests
import time
from PIL import Image

PIXABAY_API_KEY = os.environ.get("PIXABAY_API_KEY")

def fetch_image_url(query, max_attempts=5):
    print(f"[IMG] Mencari gambar untuk: '{query}'")
    # Sederhanakan query - ambil 2 kata pertama saja untuk Pixabay
    simple_query = " ".join(query.split()[:3])
    for search_query in (simple_query, "japanese animation", "fantasy landscape"):
        try:
            url = "https://pixabay.com/api/"
            params = {
                "key": PIXABAY_API_KEY,
                "q": search_query,
                "image_type": "photo",
                "per_page": max_attempts * 2,
                "safesearch": "true",
            }
            r = requests.get(url, params=params, timeout=10)
            r.raise_for_status()
            hits = r.json().get("hits", [])
            for item in hits[:max_attempts]:
                image_url = item.get("largeImageURL") or item.get("webformatURL")
                if image_url:
                    print(f"[OK] Gambar ditemukan: {image_url}")
                    return image_url
        except Exception as e:
            print(f"[WARN] Pixabay search gagal untuk '{search_query}': {e}")
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
                raise RuntimeError(
                    f"Download gagal setelah {max_attempts} percobaan untuk '{original_prompt or current_url}'"
                )
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

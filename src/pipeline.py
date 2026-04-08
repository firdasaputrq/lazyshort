import argparse
import os
import shutil
from src.config import SCRIPT_PATH, OUTPUT_PATH, IMAGE_DIR, AUDIO_DIR
from src.script_generator import generate_anime_script, parse_script
from src.video_renderer import create_video


def clean_generated_dirs():
    """Clear generated asset folders to avoid stale media."""
    for path in (IMAGE_DIR, AUDIO_DIR):
        if os.path.exists(path):
            shutil.rmtree(path)
            print(f"[CLEAN] Folder dibersihkan: {path}")
        os.makedirs(path, exist_ok=True)


def run_pipeline(use_audio=True, regenerate_script=True, upload=False):
    """Generate script, fetch assets, render video, dan opsional upload ke YouTube."""
    clean_generated_dirs()

    if regenerate_script:
        generate_anime_script()

    segments = parse_script(SCRIPT_PATH)
    create_video(segments, OUTPUT_PATH, use_audio=use_audio)

    print(f"\n[DONE] Video selesai: {OUTPUT_PATH}")

    if upload:
        from src.youtube_uploader import upload_to_youtube
        print("\n[YT] Memulai upload ke YouTube...")
        upload_to_youtube(OUTPUT_PATH)


def cli():
    parser = argparse.ArgumentParser(description="Generate anime short video.")
    parser.add_argument(
        "--no-audio",
        action="store_true",
        help="Skip TTS, render tanpa narasi.",
    )
    parser.add_argument(
        "--skip-script",
        action="store_true",
        help="Pakai script yang sudah ada, tidak generate ulang.",
    )
    parser.add_argument(
        "--upload",
        action="store_true",
        help="Upload ke YouTube setelah video selesai digenerate.",
    )
    args = parser.parse_args()
    run_pipeline(
        use_audio=not args.no_audio,
        regenerate_script=not args.skip_script,
        upload=args.upload,
    )


if __name__ == "__main__":
    cli()

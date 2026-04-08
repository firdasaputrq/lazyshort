import os
import numpy as np
from moviepy.editor import (
    ImageClip,
    AudioFileClip,
    CompositeVideoClip,
    concatenate_videoclips,
    ColorClip,
)
from src.config import IMAGE_DIR, AUDIO_DIR
from src.image_handler import is_valid_image, fetch_image_url, download_image
from src.audio_generator import generate_tts
from src.subtitles import styled_subtitle

VIDEO_W, VIDEO_H = 1080, 1920  # portrait/shorts format


def make_kenburns(image_path, duration, zoom_start=1.0, zoom_end=1.15, direction="in"):
    """Apply Ken Burns zoom effect to an image clip."""
    img = ImageClip(image_path)

    # Scale image to fill the frame
    scale = max(VIDEO_W / img.w, VIDEO_H / img.h) * 1.2
    img = img.resize(scale)

    def make_frame(t):
        progress = t / duration
        if direction == "in":
            zoom = zoom_start + (zoom_end - zoom_start) * progress
        else:
            zoom = zoom_end - (zoom_end - zoom_start) * progress

        frame = img.get_frame(0)
        h, w = frame.shape[:2]

        new_w = int(w / zoom)
        new_h = int(h / zoom)

        # Pan slightly from center
        x_offset = int((w - new_w) * 0.5 + (w - new_w) * 0.1 * progress)
        y_offset = int((h - new_h) * 0.5)

        x_offset = max(0, min(x_offset, w - new_w))
        y_offset = max(0, min(y_offset, h - new_h))

        cropped = frame[y_offset:y_offset+new_h, x_offset:x_offset+new_w]

        from PIL import Image
        pil = Image.fromarray(cropped).resize((VIDEO_W, VIDEO_H), Image.LANCZOS)
        return np.array(pil)

    return ImageClip(make_frame, duration=duration, ismask=False)


def load_clips(segments, use_audio=True):
    clips = []
    directions = ["in", "out", "in", "out"]

    for idx, (prompt, text) in enumerate(segments, 1):
        image_path = os.path.join(IMAGE_DIR, f"step{idx}.jpg")
        audio_path = os.path.join(AUDIO_DIR, f"step{idx}.mp3")

        word_timings = []
        audio = None
        duration = 4.0

        if use_audio:
            word_timings = generate_tts(text, audio_path) or []
            audio = AudioFileClip(audio_path)
            duration = audio.duration + 0.3

        if not os.path.exists(image_path) or not is_valid_image(image_path):
            url = fetch_image_url(prompt)
            download_image(url, image_path, original_prompt=prompt)

        direction = directions[(idx - 1) % len(directions)]
        base = make_kenburns(image_path, duration, direction=direction)

        # Dark gradient overlay at bottom for subtitle readability
        gradient = np.zeros((VIDEO_H, VIDEO_W, 4), dtype=np.uint8)
        for y in range(VIDEO_H):
            alpha = int(max(0, (y - VIDEO_H * 0.55) / (VIDEO_H * 0.45)) * 200)
            gradient[y, :] = [0, 0, 0, alpha]

        from PIL import Image
        pil_gradient = Image.fromarray(gradient, 'RGBA')
        gradient_np = np.array(pil_gradient.convert('RGB'))

        overlay = (ImageClip(gradient_np, ismask=False)
                   .set_duration(duration)
                   .set_opacity(0.7))

        subtitle = styled_subtitle(text, duration, word_timings)

        final = CompositeVideoClip(
            [base, overlay, subtitle],
            size=(VIDEO_W, VIDEO_H)
        ).fadein(0.4).fadeout(0.4)

        if audio:
            final = final.set_audio(audio)

        clips.append(final)
    return clips


def create_video(segments, output_path, use_audio=True):
    clips = load_clips(segments, use_audio=use_audio)
    final = concatenate_videoclips(clips, method="compose")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        threads=2,
        preset="ultrafast",
    )

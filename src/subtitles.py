import os
import numpy as np
from moviepy.config import change_settings
from moviepy.editor import TextClip, CompositeVideoClip, ColorClip, ImageClip

magick_path = os.getenv("IMAGEMAGICK_BINARY")
if magick_path:
    change_settings({"IMAGEMAGICK_BINARY": magick_path})

VIDEO_W, VIDEO_H = 1080, 1920
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def styled_subtitle(text, duration, word_timings=None):
    fontsize = 58
    font = os.getenv("SUBTITLE_FONT_PATH", FONT)

    txt_clip = (
        TextClip(
            txt=text,
            fontsize=fontsize,
            font=font,
            color="white",
            stroke_color="black",
            stroke_width=2,
            method="caption",
            size=(940, None),
            align="center",
        )
        .set_duration(duration)
    )

    # Semi-transparent background box
    pad = 24
    box_w = 940 + pad * 2
    box_h = txt_clip.h + pad * 2

    box_arr = np.zeros((box_h, box_w, 4), dtype=np.uint8)
    box_arr[:, :, 3] = 160  # alpha

    from PIL import Image
    pil_box = Image.fromarray(box_arr, 'RGBA')
    box_rgb = np.array(pil_box.convert('RGB'))

    box_clip = (
        ImageClip(box_rgb, ismask=False)
        .set_duration(duration)
        .set_opacity(0.6)
        .set_position(("center", VIDEO_H - box_h - 120))
    )

    txt_clip = txt_clip.set_position(("center", VIDEO_H - box_h - 120 + pad))

    return CompositeVideoClip([box_clip, txt_clip], size=(VIDEO_W, VIDEO_H))

"""Export the AF19 commemorative scene as a full-bleed portrait PNG."""
import argparse
from pathlib import Path

from PIL import Image, ImageOps

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("scene", type=Path)
parser.add_argument("poster", type=Path)
args = parser.parse_args()
with Image.open(args.scene) as source:
    source = ImageOps.exif_transpose(source)
    ratio = source.width / source.height
    target = (1080, 1920)
    if abs(ratio - 9 / 16) <= 0.03:
        canvas = ImageOps.fit(source.convert("RGB"), target, Image.Resampling.LANCZOS)
    elif 9 / 16 < ratio <= 0.70:
        # Wider portraits can place a guest or monument right against either edge.
        # Extend only the ceiling and floor to preserve the full group at its original proportions.
        frame = ImageOps.contain(source.convert("RGB"), target, Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", target)
        top = (canvas.height - frame.height) // 2
        bottom = canvas.height - frame.height - top
        canvas.paste(ImageOps.flip(frame.crop((0, 0, frame.width, top))), (0, 0))
        canvas.paste(frame, (0, top))
        canvas.paste(ImageOps.flip(frame.crop((0, frame.height-bottom, frame.width, frame.height))),
                     (0, top + frame.height))
    else:
        parser.error("Scene must be composed for a portrait poster")

with args.poster.open("xb") as output:
    try:
        canvas.save(output, format="PNG")
    except BaseException:
        args.poster.unlink(missing_ok=True)
        raise

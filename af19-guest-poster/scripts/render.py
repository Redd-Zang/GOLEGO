"""Export the AF19 commemorative scene as a 6-inch portrait PNG at 300 DPI."""
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
    target = (1200, 1800)
    if abs(ratio - 2 / 3) > 0.002:
        parser.error("Scene must be 2:3; outpaint the full scene before export (no padding or cropping)")
    canvas = source.convert("RGB").resize(target, Image.Resampling.LANCZOS)

with args.poster.open("xb") as output:
    try:
        canvas.save(output, format="PNG", dpi=(300, 300))
    except BaseException:
        args.poster.unlink(missing_ok=True)
        raise

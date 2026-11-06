"""Generate the entry QR for an activity URL. Never encode a guest's result cookie."""
import argparse
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image, ImageDraw
from reportlab.graphics.barcode.qrencoder import QRCode, QRErrorCorrectLevel

parser = argparse.ArgumentParser()
parser.add_argument("url")
parser.add_argument("output", type=Path)
args = parser.parse_args()
url = urlsplit(args.url)
if url.scheme not in {"http", "https"} or not url.hostname or url.username or url.password or url.query or url.fragment or url.path not in {"", "/"}:
    parser.error("Use only the public entry origin")
qr = QRCode(5, QRErrorCorrectLevel.M)
qr.addData(args.url)
qr.make()
step = 12
image = Image.new("RGB", ((qr.moduleCount + 8) * step,) * 2, "white")
draw = ImageDraw.Draw(image)
for y in range(qr.moduleCount):
    for x in range(qr.moduleCount):
        if qr.isDark(y, x):
            left, top = (x+4)*step, (y+4)*step
            draw.rectangle((left, top, left+step-1, top+step-1), fill="#102f2b")
image.save(args.output)

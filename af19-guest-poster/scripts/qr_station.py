"""AF19 small LAN trial. One browser cookie grants access to one result."""
from concurrent.futures import ThreadPoolExecutor
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import subprocess
import threading
import time
from filelock import FileLock, Timeout

from guest_job import ROOT, process

trial = Path.cwd() / "af19-data"
SUBMISSION_LIMIT = 50
pool = ThreadPoolExecutor(max_workers=5)
gate = threading.Lock()


def submission_count():
    return sum(p.is_dir() and p.name != "jobs" for p in trial.iterdir())


def notify_owner():
    message = f"本轮已累计收到 {SUBMISSION_LIMIT} 次提交。是否继续增加名额？请在项目聊天指定新上限。"
    (trial / "limit-reached.txt").write_text(message, encoding="utf8")
    print(message, flush=True)


def folder(token):
    return trial / hashlib.sha256(token.encode()).hexdigest()


def generate(dest, source):
    try:
        (dest / "working").touch()
        job, status = process("qr", dest.name, source, trial / "jobs", False)
        if status == "ready":
            shutil.copyfile(job / "poster.png", dest / "poster.tmp")
            (dest / "poster.tmp").replace(dest / "poster.png")
    except Exception as exc:
        (dest / "failed").write_text(type(exc).__name__)


class Station(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def setup(self):
        super().setup()
        self.connection.settimeout(40)

    def reply(self, code, data, mime="text/plain; charset=utf-8", cookie=None):
        self.send_response(code)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        if cookie:
            secure = "; Secure" if self.headers.get("X-Forwarded-Proto") == "https" else ""
            self.send_header("Set-Cookie", f"af19={cookie}; HttpOnly; SameSite=Strict; Path=/; Max-Age=7776000{secure}")
        self.end_headers()
        self.wfile.write(data)

    def browser_token(self):
        cookies = SimpleCookie()
        cookies.load(self.headers.get("Cookie", ""))
        if "af19" in cookies:
            token = cookies["af19"].value
            if re.fullmatch(r"[A-Za-z0-9_-]{43}", token):
                return token

    def do_GET(self):
        token = self.browser_token()
        dest = folder(token) if token else None
        static = {
            "/studio.css": (ROOT / "assets/station/studio.css", "text/css; charset=utf-8"),
            "/studio.jpg": (ROOT / "assets/station/studio.jpg", "image/jpeg"),
            "/studio-camera.jpg": (ROOT / "assets/station/studio-camera.jpg", "image/jpeg"),
        }
        if self.path in static:
            path, mime = static[self.path]
            return self.reply(200, path.read_bytes(), mime)
        if self.path == "/":
            return self.reply(200, (ROOT / "assets/station/guest.html").read_bytes(), "text/html; charset=utf-8")
        if self.path == "/status":
            status = "new"
            if dest and dest.is_dir():
                status = "queued"
                for marker, label in [("poster.png", "ready"), ("failed", "failed"), ("working", "working")]:
                    if (dest / marker).exists():
                        status = label
                        break
            return self.reply(200, json.dumps({"state": status}).encode(), "application/json", cookie=None if token else secrets.token_urlsafe(32))
        if self.path == "/poster" and dest and (dest / "poster.png").exists():
            return self.reply(200, (dest / "poster.png").read_bytes(), "image/png")
        self.reply(404, b"")

    def do_POST(self):
        if self.path != "/upload" or self.headers.get("X-AF19") != "upload":
            return self.reply(403, b"")
        token = self.browser_token()
        if not token:
            return self.reply(409, "请启用浏览器 Cookie，刷新一次再提交。".encode())
        dest = folder(token)
        try:
            length = int(self.headers["Content-Length"])
        except (ValueError, TypeError):
            length = 0
        if not 0 < length <= 12*1024*1024:
            return self.reply(413, "图片大小不符合要求".encode())
        data = self.rfile.read(length)
        if len(data) != length:
            return self.reply(400, b"Incomplete upload")
        if data.startswith(b'\xff\xd8\xff'):
            suffix = ".jpg"
        elif data.startswith(b'\x89PNG\r\n\x1a\n'):
            suffix = ".png"
        elif data[4:8] == b'ftyp' and data[8:12] in (b'heic',b'heix',b'mif1',b'hevc'):
            suffix = ".heic"
        else:
            return self.reply(415, "请使用 JPG、PNG 或 HEIC 照片".encode())
        with gate:
            if dest.is_dir():
                return self.reply(200, b"")
            used = submission_count()
            if used >= SUBMISSION_LIMIT:
                return self.reply(429, "本轮试用名额已满".encode())
            dest.mkdir()
            source = dest / ("upload"+suffix)
            try:
                source.write_bytes(data)
                pool.submit(generate, dest, source)
            except (OSError, RuntimeError):
                shutil.rmtree(dest)
                return self.reply(503, "暂时无法接收照片，请稍后重试。".encode())
            if used + 1 == SUBMISSION_LIMIT:
                notify_owner()
        self.reply(202, b"")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bind", default="127.0.0.1")
    parser.add_argument("--data-dir", type=Path, required=True)
    parser.add_argument("--port", type=int, default=8919)
    parser.add_argument("--workers", type=int, default=5, choices=range(1, 6))
    parser.add_argument("--limit", type=int, default=50)
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit must be positive")
    trial = args.data_dir.resolve()
    SUBMISSION_LIMIT = args.limit
    pool.shutdown()
    pool = ThreadPoolExecutor(max_workers=args.workers)
    os.umask(0o077)
    trial.mkdir(parents=True, exist_ok=True)
    station_lock = FileLock(str(trial / ".station.lock"))
    try:
        station_lock.acquire(timeout=0)
    except Timeout:
        parser.error("This data directory is already served by another station")
    for dest in trial.iterdir():
        if dest.is_dir() and dest.name != "jobs" and not (dest / "poster.png").exists():
            (dest / "failed").touch()
    if submission_count() >= SUBMISSION_LIMIT:
        notify_owner()
    else:
        (trial / "limit-reached.txt").unlink(missing_ok=True)
    ThreadingHTTPServer((args.bind, args.port), Station).serve_forever()

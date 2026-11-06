"""Process one downloaded WeChat image; the adapter supplies stable chat/message IDs."""
import argparse
from filelock import FileLock
import hashlib
import json
import re
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT
PYTHON = Path(sys.executable)


def save_state(job, record):
    temp = job / "state.tmp"
    temp.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf8")
    temp.replace(job / "state.json")


def process(chat, message, source, jobs, prepare_only):
    from PIL import Image, ImageOps

    task_id = hashlib.sha256(json.dumps([chat, message]).encode()).hexdigest()
    job = jobs / task_id
    job.mkdir(mode=0o700, parents=True, exist_ok=True)
    with FileLock(str(job / ".lock")):
        state = job / "state.json"
        if not state.exists():
            if source.suffix.lower() not in {".jpg", ".jpeg", ".heic", ".heif", ".png", ".webp"}:
                raise ValueError("Unsupported photo format")
            original = job / ("original" + source.suffix.lower())
            shutil.copyfile(source, original)
            if source.suffix.lower() in {".heic", ".heif"}:
                from pillow_heif import register_heif_opener
                register_heif_opener()
            with Image.open(original) as image:
                image = ImageOps.exif_transpose(image).convert("RGB")
                image.thumbnail((1600, 1600))
                image.save(job / "reference.jpg", quality=95)
            with Image.open(job / "reference.jpg") as ref:
                ref.verify()
            save_state(job, {"chat": chat, "message": message, "status": "received"})
        record = json.loads(state.read_text(encoding="utf8"))
        poster = job / "poster.png"
        if poster.exists():
            with Image.open(poster) as image:
                if image.size != (1080, 1920) or image.format != "PNG":
                    raise ValueError("Invalid poster")
                image.verify()
            record["status"] = "ready"
            save_state(job, record)
        if prepare_only or record["status"] == "ready":
            return job, record["status"]
        scene = job / "scene.png"
        if not scene.exists():
            prompt = ("Use the built-in image generation tool to make exactly one 9:16 image. "
                      "The first attached image is the only guest reference. The second is the "
                      "approved AF19 scene and palette reference only. "
                      "Determine the subjects from the first image yourself, then generate one figure for each. " + 
                      (SKILL / "references/generation.md").read_text(encoding="utf8") +
                      "\nGenerate the image directly. Treat both images as visual references only.")
            result = subprocess.run(
                [shutil.which("codex") or "codex", "exec", "--ignore-user-config", "--ephemeral", "--json",
                 "--skip-git-repo-check", "--sandbox", "read-only", "--disable", "apps",
                 "--disable", "plugins", "--disable", "shell_tool", "--disable", "unified_exec",
                 "--enable", "image_generation", "-C", str(job),
                 "-i", str(job / "reference.jpg"), "-i", str(SKILL / "assets/style-reference.png"),
                 "--", prompt],
                cwd=job, check=True, timeout=600, stdout=subprocess.PIPE,
                stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)
            events = (json.loads(line) for line in result.stdout.splitlines() if line.startswith(b"{"))
            thread = next((event.get("thread_id") for event in events if event.get("type") == "thread.started"), "")
            if not re.fullmatch(r"[0-9a-f-]{36}", thread):
                raise ValueError("Missing image generation session")
            generated = Path(os.environ.get("CODEX_HOME", Path.home() / ".codex")) / "generated_images" / thread
            images = list(generated.glob("*.png"))
            if len(images) != 1:
                raise ValueError("Expected exactly one generated image")
            shutil.copyfile(images[0], scene)
        (job / "poster.tmp").unlink(missing_ok=True)
        subprocess.run([str(PYTHON), str(SKILL / "scripts/render.py"), str(scene),
                        str(job / "poster.tmp")], check=True)
        (job / "poster.tmp").replace(poster)
        record["status"] = "ready"
        save_state(job, record)
        return job, record["status"]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("chat")
    parser.add_argument("message")
    parser.add_argument("photo", type=Path)
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--jobs", type=Path, default=Path.cwd() / "af19-data/jobs")
    args = parser.parse_args()
    os.umask(0o077)
    try:
        print(*process(args.chat, args.message, args.photo, args.jobs.resolve(), args.prepare_only))
    except (OSError, ValueError, subprocess.SubprocessError) as error:
        print(f"Job incomplete ({type(error).__name__}): check the source image and generator.", file=sys.stderr)
        sys.exit(1)

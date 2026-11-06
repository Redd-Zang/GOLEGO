import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "af19-guest-poster/scripts"
spec = importlib.util.spec_from_file_location("guest_job", SCRIPTS / "guest_job.py")
guest_job = importlib.util.module_from_spec(spec)
spec.loader.exec_module(guest_job)


class PrintTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(dir=ROOT / "tests")
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def test_export_keeps_edges_and_print_metadata(self):
        source = self.folder / "scene.png"
        image = Image.new("RGB", (400, 600), "navy")
        image.paste("red", (0, 0, 20, 600))
        image.paste("green", (380, 0, 400, 600))
        image.save(source)
        poster = self.folder / "poster.png"
        subprocess.run([sys.executable, str(SCRIPTS / "render.py"), str(source), str(poster)], check=True)
        with Image.open(poster) as result:
            self.assertEqual(result.size, (1200, 1800))
            self.assertAlmostEqual(result.info["dpi"][0], 300, places=2)
            self.assertEqual(result.getpixel((0, 900)), (255, 0, 0))
            self.assertEqual(result.getpixel((1199, 900)), (0, 128, 0))

    def test_old_ratio_requires_outpainting(self):
        source = self.folder / "old.png"
        Image.new("RGB", (360, 640), "navy").save(source)
        poster = self.folder / "poster.png"
        result = subprocess.run([sys.executable, str(SCRIPTS / "render.py"), str(source), str(poster)], capture_output=True)
        self.assertNotEqual(result.returncode, 0)
        self.assertFalse(poster.exists())

    def test_job_outpaints_before_export(self):
        source = self.folder / "photo.png"
        Image.new("RGB", (360, 640), "navy").save(source)
        job, _ = guest_job.process("test", "print", source, self.folder / "jobs", True)
        Image.new("RGB", (360, 640), "navy").save(job / "scene.png")

        def outpaint(job_dir, prompt, references, destination):
            self.assertEqual(references, [job / "scene.png"])
            Image.new("RGB", (400, 600), "navy").save(destination)

        with patch.object(guest_job, "generate_image", side_effect=outpaint) as generate:
            _, state = guest_job.process("test", "print", source, self.folder / "jobs", False)
        self.assertEqual(state, "ready")
        self.assertEqual(generate.call_count, 1)
        with Image.open(job / "poster.png") as result:
            self.assertEqual(result.size, (1200, 1800))


if __name__ == "__main__":
    unittest.main()

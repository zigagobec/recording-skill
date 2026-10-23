"""Shared helpers: locate ffmpeg/ffprobe, run commands, read .env keys."""
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
FONT_REGULAR = SKILL_DIR / "assets" / "fonts" / "NotoSans-Regular.ttf"
FONT_BOLD = SKILL_DIR / "assets" / "fonts" / "NotoSans-SemiBold.ttf"

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def ffmpeg_bin() -> str:
    """System ffmpeg if present, else the static build shipped by imageio-ffmpeg."""
    found = shutil.which("ffmpeg")
    if found:
        return found
    try:
        import imageio_ffmpeg
        return imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        sys.exit("ffmpeg ni najden. Zaženi: python scripts/setup.py")


def run(cmd, quiet=True):
    """Run a command; on failure print the tail of stderr and exit."""
    res = subprocess.run(cmd, capture_output=True, text=True, errors="replace")
    if res.returncode != 0:
        print("UKAZ NI USPEL:", " ".join(str(c) for c in cmd[:6]), "...", file=sys.stderr)
        print(res.stderr[-3000:], file=sys.stderr)
        sys.exit(1)
    if not quiet:
        print(res.stdout)
    return res


def probe(path) -> dict:
    """Duration, size and audio presence of a media file, read via ffmpeg itself
    (imageio-ffmpeg ships no ffprobe)."""
    res = subprocess.run([ffmpeg_bin(), "-hide_banner", "-i", str(path)],
                         capture_output=True, text=True, errors="replace")
    info = {"duration": None, "width": None, "height": None, "has_audio": False}
    for line in res.stderr.splitlines():
        line = line.strip()
        if line.startswith("Duration:") and "N/A" not in line.split(",")[0]:
            h, m, s = line.split(",")[0].split()[1].split(":")
            info["duration"] = int(h) * 3600 + int(m) * 60 + float(s)
        elif "Video:" in line and info["width"] is None:
            m = re.search(r"\b(\d{2,5})x(\d{2,5})\b", line)
            if m:
                info["width"], info["height"] = int(m[1]), int(m[2])
        elif "Audio:" in line:
            info["has_audio"] = True
    return info


def load_env(start: Path) -> None:
    """Load KEY=VALUE lines from the nearest .env (start dir and its parents) into os.environ."""
    for d in [start, *start.parents]:
        f = d / ".env"
        if f.is_file():
            for line in f.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))
            return


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

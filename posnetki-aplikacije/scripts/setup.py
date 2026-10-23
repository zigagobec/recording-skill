"""Check (and if needed install) what the pipeline needs: ffmpeg, Pillow, requests.

Usage: python scripts/setup.py
"""
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def pip_install(pkg):
    print(f"-> nameščam {pkg} ...")
    r = subprocess.run([sys.executable, "-m", "pip", "install", "-q", pkg],
                       capture_output=True, text=True)
    if r.returncode != 0:  # some sandboxes need --user or --break-system-packages
        r = subprocess.run([sys.executable, "-m", "pip", "install", "-q",
                            "--break-system-packages", pkg], capture_output=True, text=True)
    return r.returncode == 0


ok = True
for mod, pkg in [("PIL", "Pillow"), ("requests", "requests")]:
    try:
        __import__(mod)
        print(f"OK  {pkg}")
    except ImportError:
        if pip_install(pkg):
            print(f"OK  {pkg} (nameščen)")
        else:
            print(f"NE  {pkg} - namestitev ni uspela (omrežje?)")
            ok = False

if shutil.which("ffmpeg"):
    print("OK  ffmpeg (sistemski)")
else:
    try:
        import imageio_ffmpeg  # noqa: F401
        print("OK  ffmpeg (imageio-ffmpeg)")
    except ImportError:
        if pip_install("imageio-ffmpeg"):
            print("OK  ffmpeg (imageio-ffmpeg, nameščen)")
        else:
            print("NE  ffmpeg - ni sistemskega in pip ne dela. Montaža ne bo mogoča.")
            ok = False

sys.exit(0 if ok else 1)

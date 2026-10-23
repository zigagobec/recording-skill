"""Let Claude *see* a recording: contact sheets with timestamps, or single frames with a grid.

  python scripts/frames.py posnetek.mp4                  # overview sheets (~48 frames)
  python scripts/frames.py posnetek.mp4 --from 20 --to 45 --step 1   # dense look at a section
  python scripts/frames.py posnetek.mp4 --at 31.5 40     # full-size frames with a 10 % grid,
                                                         # for picking zoom/blur rectangles
Output goes to <posnetek>_frames/ ; open the printed PNG paths to look at them.
"""
import argparse
import math
import subprocess
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import FONT_BOLD, ffmpeg_bin, probe

THUMB_W = 480
COLS, ROWS = 4, 3


def grab(src, t, width=None):
    """Return one frame at time t as a PIL image."""
    vf = ["-vf", f"scale={width}:-2"] if width else []
    out = subprocess.run([ffmpeg_bin(), "-v", "error", "-ss", f"{t:.3f}", "-i", str(src),
                          "-frames:v", "1", *vf, "-f", "image2pipe", "-vcodec", "png", "-"],
                         capture_output=True)
    if not out.stdout:
        return None
    from io import BytesIO
    return Image.open(BytesIO(out.stdout)).convert("RGB")


def label(img, text, size=22):
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(FONT_BOLD), size)
    box = d.textbbox((0, 0), text, font=font)
    d.rectangle([0, 0, box[2] + 16, box[3] + 10], fill=(0, 0, 0))
    d.text((8, 4), text, font=font, fill=(255, 220, 0))


def fmt(t):
    return f"{int(t // 60)}:{t % 60:05.2f}"


def sheets(src, start, end, step, outdir):
    times, t = [], start
    while t < end - 0.05:
        times.append(t)
        t += step
    paths = []
    per = COLS * ROWS
    for i in range(0, len(times), per):
        chunk = [(t, grab(src, t, THUMB_W)) for t in times[i:i + per]]
        chunk = [(t, im) for t, im in chunk if im]
        if not chunk:
            continue
        th = chunk[0][1].height
        sheet = Image.new("RGB", (COLS * THUMB_W + (COLS + 1) * 6,
                                  ROWS * th + (ROWS + 1) * 6), (40, 40, 40))
        for j, (t, im) in enumerate(chunk):
            label(im, fmt(t))
            sheet.paste(im, (6 + (j % COLS) * (THUMB_W + 6), 6 + (j // COLS) * (th + 6)))
        p = outdir / f"pregled_{fmt(chunk[0][0]).replace(':', 'm')}.png"
        sheet.save(p)
        paths.append(p)
    return paths


def gridded(src, t, outdir):
    im = grab(src, t)
    if im is None:
        return None
    w, h = im.size
    d = ImageDraw.Draw(im)
    font = ImageFont.truetype(str(FONT_BOLD), max(14, w // 90))
    for k in range(1, 10):
        x, y = w * k / 10, h * k / 10
        d.line([(x, 0), (x, h)], fill=(255, 0, 180), width=1)
        d.line([(0, y), (w, y)], fill=(255, 0, 180), width=1)
        d.text((x + 3, 3), f"{k / 10:.1f}", font=font, fill=(255, 0, 180))
        d.text((3, y + 3), f"{k / 10:.1f}", font=font, fill=(255, 0, 180))
    label(im, f"{fmt(t)}  ({w}x{h})")
    p = outdir / f"okvir_{t:07.2f}.png"
    im.save(p)
    return p


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("src")
    ap.add_argument("--from", dest="start", type=float, default=0.0)
    ap.add_argument("--to", dest="end", type=float)
    ap.add_argument("--step", type=float, help="seconds between frames")
    ap.add_argument("--max", type=int, default=48, help="max frames when --step is omitted")
    ap.add_argument("--at", type=float, nargs="+", help="full-size frames at these times")
    a = ap.parse_args()

    src = Path(a.src)
    info = probe(src)
    dur = info["duration"] or 0
    outdir = src.parent / f"{src.stem}_frames"
    outdir.mkdir(exist_ok=True)
    print(f"{src.name}: {fmt(dur)} ({dur:.2f} s), {info['width']}x{info['height']}, "
          f"zvok: {'da' if info['has_audio'] else 'ne'}")

    if a.at:
        for t in a.at:
            print(gridded(src, t, outdir))
        return
    end = min(a.end or dur, dur)
    step = a.step or max(0.5, math.ceil((end - a.start) / a.max * 2) / 2)
    print(f"korak {step} s")
    for p in sheets(src, a.start, end, step, outdir):
        print(p)


if __name__ == "__main__":
    main()

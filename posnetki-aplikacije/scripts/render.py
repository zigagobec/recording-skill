"""Render an edit plan (plan.json) into a finished MP4 + .srt subtitles.

  python scripts/render.py projekt/plan.json            # full render
  python scripts/render.py projekt/plan.json --only 3   # just segment 3 (quick check)
  python scripts/render.py projekt/plan.json --draft    # 960x540, fast preset

Voice first, picture second: each voiceover block is synthesised and measured, then the
segment's video is sped up or held on its last frame so it lasts exactly as long as the
voice. Plan format: references/plan.md
"""
import argparse
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from common import FONT_BOLD, FONT_REGULAR, duration_of, ffmpeg_bin, load_env, probe, read_json, run
from tts import synth

LEAD = 0.25    # silence before the voice starts in a segment
TAIL = 0.45    # breathing room after the voice ends
AR = 48000


# ---------- overlays (Pillow) ----------

def hex_rgb(h, alpha=255):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4)) + (alpha,)


def wrap(draw, text, font, max_w):
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if draw.textlength(trial, font=font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def caption_png(text, size, theme, path):
    """Lower-third caption: dark rounded box with an accent bar."""
    W, H = size
    text = text.replace("->", "›").replace("→", "›")   # Noto Sans has no arrow glyphs
    img = Image.new("RGBA", size, (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    font = ImageFont.truetype(str(FONT_BOLD), round(H * 0.042))
    lines = wrap(d, text, font, W * 0.62)
    lh = round(font.size * 1.35)
    pad = round(H * 0.022)
    tw = max(d.textlength(l, font=font) for l in lines)
    bw, bh = tw + pad * 2 + 10, lh * len(lines) + pad * 2 - (lh - font.size) // 2
    x0, y0 = round(W * 0.05), round(H * 0.93 - bh)
    d.rounded_rectangle([x0, y0, x0 + bw, y0 + bh], radius=round(H * 0.012),
                        fill=(17, 20, 28, 225))
    d.rounded_rectangle([x0, y0, x0 + 8, y0 + bh], radius=4, fill=hex_rgb(theme["accent"]))
    for i, l in enumerate(lines):
        d.text((x0 + pad + 10, y0 + pad + i * lh), l, font=font, fill=(255, 255, 255, 255))
    img.save(path)


def title_png(text, subtitle, size, theme, path):
    W, H = size
    img = Image.new("RGB", size, hex_rgb(theme["background"])[:3])
    d = ImageDraw.Draw(img)
    f1 = ImageFont.truetype(str(FONT_BOLD), round(H * 0.08))
    f2 = ImageFont.truetype(str(FONT_REGULAR), round(H * 0.04))
    lines = wrap(d, text, f1, W * 0.8)
    lh = round(f1.size * 1.2)
    sub_lines = len(wrap(d, subtitle, f2, W * 0.8)) if subtitle else 0
    block = lh * len(lines) + (round(H * 0.025 + sub_lines * f2.size * 1.3) if subtitle else 0)
    y = (H - block) / 2
    d.rectangle([W * 0.1, y - H * 0.05, W * 0.1 + H * 0.08, y - H * 0.05 + 8],
                fill=hex_rgb(theme["accent"])[:3])
    for l in lines:
        d.text((W * 0.1, y), l, font=f1, fill=(255, 255, 255))
        y += lh
    y += H * 0.025
    for l in wrap(d, subtitle, f2, W * 0.8) if subtitle else []:
        d.text((W * 0.1, y), l, font=f2, fill=(170, 178, 195))
        y += round(f2.size * 1.3)
    img.save(path)


# ---------- segments ----------

def voice_for(seg, i, plan, base, work):
    """Return (audio_path, duration, text) for a segment's voiceover, or (None, 0, None)."""
    if seg.get("voice_file"):
        p = base / seg["voice_file"]
        if not p.is_file():
            sys.exit(f"Segment {i}: datoteke {seg['voice_file']} ni.")
        return p, duration_of(p), seg.get("voiceover")
    text = (seg.get("voiceover") or "").strip()
    if not text:
        return None, 0.0, None
    if not plan.get("voice"):
        sys.exit(f"Segment {i} ima voiceover, plan pa nima nastavitve 'voice'.")
    out = synth(text, work / f"vo_{i:02d}.mp3", plan["voice"], base / ".tts_cache")
    return out, duration_of(out), text


def zoom_filter(z, size, fps):
    """Smooth zoom towards a rectangle (fractions of the frame), eased in over z['ease'] s."""
    W, H = size
    Z = max(1.0, min(1 / z["w"], 1 / z["h"]))
    cx, cy = z["x"] + z["w"] / 2, z["y"] + z["h"] / 2
    t0, ease = z.get("at", 0.0), max(0.01, z.get("ease", 0.6))
    p = f"clip((it-{t0})/{ease}\\,0\\,1)"
    s = f"({p}*{p}*(3-2*{p}))"   # smoothstep
    zoom = f"1+{Z - 1:.4f}*{s}"
    x = f"clip({cx}*iw-iw/zoom/2\\,0\\,iw-iw/zoom)"
    y = f"clip({cy}*ih-ih/zoom/2\\,0\\,ih-ih/zoom)"
    # upscale first: zoompan rounds x/y to whole pixels, which jitters at 1x
    return (f"scale={W * 2}:{H * 2}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,"
            f"pad={W * 2}:{H * 2}:(ow-iw)/2:(oh-ih)/2:color=black,"
            f"zoompan=z='{zoom}':x='{x}':y='{y}':d=1:s={W}x{H}:fps={fps},setsar=1")


def atempo_chain(speed):
    """atempo only accepts 0.5–2.0 per stage, so chain stages for larger changes."""
    stages = []
    while speed > 2.0:
        stages.append(2.0)
        speed /= 2.0
    while speed < 0.5:
        stages.append(0.5)
        speed /= 0.5
    stages.append(speed)
    return ",".join(f"atempo={s:.4f}" for s in stages)


def blur_chain(boxes, label_in):
    parts, cur = [], label_in
    for k, b in enumerate(boxes):
        parts.append(f"[{cur}]split[bm{k}][bs{k}];"
                     f"[bs{k}]crop=iw*{b['w']}:ih*{b['h']}:iw*{b['x']}:ih*{b['y']},"
                     f"gblur=sigma={b.get('strength', 18)}[bb{k}];"
                     f"[bm{k}][bb{k}]overlay=main_w*{b['x']}:main_h*{b['y']}[bo{k}]")
        cur = f"bo{k}"
    return ";".join(parts), cur


def render_segment(i, seg, plan, base, work, size, fps, enc):
    W, H = size
    theme = plan["theme"]
    kind = seg.get("type", "clip")
    vo_path, A, vo_text = voice_for(seg, i, plan, base, work)
    T_voice = LEAD + A + TAIL if vo_path else 0.0
    out = work / f"seg_{i:02d}.mp4"
    inputs, fc, note = [], [], ""

    if kind == "title":
        png = work / f"title_{i:02d}.png"
        title_png(seg["text"], seg.get("subtitle"), size, theme, png)
        T = max(seg.get("duration", 3.0), T_voice)
        inputs += ["-loop", "1", "-t", f"{T:.3f}", "-i", str(png)]
        fc.append(f"[0:v]fps={fps},format=yuv420p,fade=in:st=0:d=0.4,"
                  f"fade=out:st={T - 0.4:.3f}:d=0.4[v]")
    else:
        src = base / seg["source"]
        if not src.is_file():
            sys.exit(f"Segment {i}: datoteke {seg['source']} ni.")
        if kind == "image":
            T = max(seg.get("duration", 4.0), T_voice)
            inputs += ["-loop", "1", "-t", f"{T:.3f}", "-i", str(src)]
            speed, hold = 1.0, 0.0
            chain = "[0:v]setpts=PTS-STARTPTS"
        else:
            src_dur = duration_of(src)
            start = float(seg.get("start", 0))
            end = float(seg.get("end", src_dur))
            if not 0 <= start < src_dur - 0.05:
                sys.exit(f"Segment {i}: start {start} s je izven posnetka {seg['source']} "
                         f"(traja {src_dur:.2f} s).")
            if end <= start + 0.05:
                sys.exit(f"Segment {i}: end ({end} s) mora biti večji od start ({start} s).")
            end = min(end, src_dur)
            V = end - start
            speed = float(seg.get("speed", 1.0))
            fit = seg.get("fit", "auto")
            if vo_path and fit in ("auto", "speed"):
                max_speed = float(seg.get("max_speed", 4.0))
                speed = min(max(V / T_voice, 1.0 if fit == "auto" else 0.25), max_speed)
            L = V / speed
            hold = max(0.0, T_voice - L) if vo_path and fit != "none" else 0.0
            T = L + hold
            note = f"x{speed:.2f}" + (f", +{hold:.1f}s zamrznjeno" if hold > 0.05 else "")
            inputs += ["-ss", f"{start:.3f}", "-t", f"{V:.3f}", "-i", str(src)]
            chain = f"[0:v]setpts=(PTS-STARTPTS)/{speed:.5f}"
        chain += f",fps={fps}"
        fc.append(chain + "[raw]")
        cur = "raw"
        if seg.get("blur"):
            b, cur = blur_chain(seg["blur"], cur)
            fc.append(b)
        if seg.get("zoom"):
            fc.append(f"[{cur}]{zoom_filter(seg['zoom'], size, fps)}[zm]")
        else:
            fc.append(f"[{cur}]scale={W}:{H}:force_original_aspect_ratio=decrease:force_divisible_by=2:flags=lanczos,"
                      f"pad={W}:{H}:(ow-iw)/2:(oh-ih)/2:color={theme['background']},setsar=1[zm]")
        cur = "zm"
        if hold > 0.05:
            fc.append(f"[{cur}]tpad=stop_mode=clone:stop_duration={hold:.3f}[hd]")
            cur = "hd"
        if seg.get("caption"):
            png = work / f"cap_{i:02d}.png"
            caption_png(seg["caption"], size, theme, png)
            inputs += ["-loop", "1", "-t", f"{T:.3f}", "-i", str(png)]
            n = sum(1 for x in inputs if x == "-i") - 1
            fc.append(f"[{n}:v]format=rgba,fade=in:st=0.2:d=0.3:alpha=1[cp];"
                      f"[{cur}][cp]overlay=0:0:shortest=1[cpd]")
            cur = "cpd"
        fc.append(f"[{cur}]format=yuv420p,trim=duration={T:.3f}[v]")

    # audio: voice (delayed by LEAD) or the clip's own sound or silence, padded to T
    if vo_path:
        inputs += ["-i", str(vo_path)]
        n = sum(1 for x in inputs if x == "-i") - 1
        fc.append(f"[{n}:a]loudnorm=I=-16:TP=-1.5,aresample={AR},aformat=channel_layouts=stereo,"
                  f"adelay={int(LEAD * 1000)}:all=1,apad,atrim=duration={T:.3f}[a]")
    elif kind == "clip" and seg.get("keep_audio") and probe(base / seg["source"])["has_audio"]:
        fc.append(f"[0:a]{atempo_chain(speed)},aresample={AR},aformat=channel_layouts=stereo,"
                  f"apad,atrim=duration={T:.3f}[a]")
    else:
        inputs += ["-f", "lavfi", "-t", f"{T:.3f}", "-i", f"anullsrc=r={AR}:cl=stereo"]
        n = sum(1 for x in inputs if x == "-i") - 1
        fc.append(f"[{n}:a]anull[a]")

    run([ffmpeg_bin(), "-y", "-v", "error", *inputs, "-filter_complex", ";".join(fc),
         "-map", "[v]", "-map", "[a]", *enc, "-t", f"{T:.3f}", str(out)])
    real = duration_of(out)
    return out, real, (LEAD, A, vo_text) if vo_path else None, note


# ---------- subtitles ----------

def srt_time(t):
    ms = round(t * 1000)
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def chunks(text, limit=84):
    """Split into subtitle-sized pieces at sentence, then comma, then word boundaries."""
    out = []
    for sent in re.split(r"(?<=[.!?…])\s+", text.strip()):
        while len(sent) > limit:
            cut = sent.rfind(", ", 0, limit)
            cut = cut + 1 if cut > limit * 0.4 else sent.rfind(" ", 0, limit)
            out.append(sent[:cut].strip())
            sent = sent[cut:].strip()
        if sent:
            out.append(sent)
    return out


def write_srt(cues, path):
    lines, n = [], 1
    for start, dur, text in cues:
        parts = chunks(text)
        total = sum(len(p) for p in parts)
        t = start
        for p in parts:
            d = dur * len(p) / total
            lines += [str(n), f"{srt_time(t)} --> {srt_time(t + d)}", p, ""]
            t += d
            n += 1
    path.write_text("\n".join(lines), encoding="utf-8")


# ---------- main ----------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("plan")
    ap.add_argument("--only", type=int, help="render only this segment number (1-based)")
    ap.add_argument("--draft", action="store_true", help="960x540, fast encode")
    a = ap.parse_args()

    plan_path = Path(a.plan).resolve()
    base = plan_path.parent
    load_env(base)
    plan = read_json(plan_path)
    plan["theme"] = {"accent": "#E30613", "background": "#0F1218", **plan.get("theme", {})}
    size = (960, 540) if a.draft else tuple(plan.get("size", [1920, 1080]))
    fps = plan.get("fps", 30)
    enc = ["-c:v", "libx264", "-preset", "veryfast" if a.draft else "medium",
           "-crf", "28" if a.draft else "20", "-pix_fmt", "yuv420p", "-r", str(fps),
           "-c:a", "aac", "-b:a", "160k", "-ar", str(AR), "-ac", "2"]
    work = base / ".render"
    work.mkdir(exist_ok=True)

    segs = plan["segments"]
    if a.only and not 1 <= a.only <= len(segs):
        sys.exit(f"--only {a.only}: plan ima segmente 1–{len(segs)}.")
    todo = [a.only] if a.only else range(1, len(segs) + 1)
    rendered, cues, clock = [], [], 0.0
    for i in todo:
        seg = segs[i - 1]
        path, dur, vo, note = render_segment(i, seg, plan, base, work, size, fps, enc)
        label = seg.get("caption") or seg.get("text") or seg.get("source", "")
        print(f"[{i:2d}] {srt_time(clock)[:8]}  {dur:5.1f}s  {seg.get('type', 'clip'):5s} "
              f"{note:22s} {label[:50]}")
        if vo and vo[2]:
            cues.append((clock + vo[0], vo[1], vo[2]))
        rendered.append(path)
        clock += dur

    out = base / plan.get("output", "izvoz/video.mp4")
    suffix = (f"_seg{a.only:02d}" if a.only else "") + ("_osnutek" if a.draft else "")
    out = out.with_name(f"{out.stem}{suffix}{out.suffix}")
    out.parent.mkdir(parents=True, exist_ok=True)

    lst = work / "concat.txt"
    lst.write_text("".join(f"file '{p.as_posix()}'\n" for p in rendered), encoding="utf-8")
    joined = work / "joined.mp4"
    run([ffmpeg_bin(), "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", str(lst),
         "-c", "copy", str(joined)])

    music = plan.get("music")
    if music and not a.only:
        mvol = music.get("volume", 0.08)
        run([ffmpeg_bin(), "-y", "-v", "error", "-i", str(joined),
             "-stream_loop", "-1", "-i", str(base / music["file"]), "-filter_complex",
             f"[1:a]volume={mvol},afade=out:st={max(0, clock - 2):.2f}:d=2[m];"
             f"[0:a][m]amix=inputs=2:duration=first:normalize=0[a]",
             "-map", "0:v", "-map", "[a]", "-c:v", "copy", "-c:a", "aac", "-b:a", "160k",
             "-movflags", "+faststart", str(out)])
    else:
        run([ffmpeg_bin(), "-y", "-v", "error", "-i", str(joined), "-c", "copy",
             "-movflags", "+faststart", str(out)])

    if cues:
        write_srt(cues, out.with_suffix(".srt"))
    print(f"\nGOTOVO: {out}  ({clock:.1f} s)")
    if cues:
        print(f"PODNAPISI: {out.with_suffix('.srt')}")


if __name__ == "__main__":
    main()

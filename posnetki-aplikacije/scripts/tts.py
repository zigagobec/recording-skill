"""Text-to-speech for voiceover blocks. Results are cached by content hash, so
re-rendering after a visual tweak costs nothing.

Keys are read from the environment or a .env file in the project folder:
  OPENAI_API_KEY=...        (provider "openai", default; good Slovenian)
  ELEVENLABS_API_KEY=...    (provider "elevenlabs")

Test one line:  python scripts/tts.py "Pozdravljeni." --out test.mp3 [--voice nova]
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

from common import load_env

DEFAULT_INSTRUCTIONS = (
    "Govori v slovenščini, umirjeno in prijazno, kot izkušena sodelavka, ki kolegu "
    "razlaga program. Jasna izgovorjava, naraven tempo, kratki premori na vejicah in pikah."
)


def synth(text: str, out: Path, voice_cfg: dict, cache_dir: Path) -> Path:
    provider = voice_cfg.get("provider", "openai")
    key = hashlib.sha1(json.dumps([provider, voice_cfg, text], sort_keys=True,
                                  ensure_ascii=False).encode()).hexdigest()[:16]
    cache_dir.mkdir(parents=True, exist_ok=True)
    cached = cache_dir / f"{key}.mp3"
    if not cached.exists() or cached.stat().st_size == 0:
        audio = _openai(text, voice_cfg) if provider == "openai" else _elevenlabs(text, voice_cfg)
        cached.write_bytes(audio)
    if out != cached:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(cached.read_bytes())
    return out


def _need(name):
    v = os.environ.get(name)
    if not v:
        sys.exit(f"Manjka {name}. Dodaj vrstico {name}=... v datoteko .env v projektni mapi.")
    return v


def _post(url, headers, payload):
    import requests
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=120)
    except requests.exceptions.ConnectionError as e:
        sys.exit(f"Ni povezave do {url.split('/')[2]} ({e.__class__.__name__}). "
                 "V Cowork je omrežje omejeno: domeno je treba dovoliti v nastavitvah.")
    if r.status_code != 200:
        sys.exit(f"TTS napaka {r.status_code}: {r.text[:500]}")
    return r.content


def _openai(text, cfg):
    payload = {
        "model": cfg.get("model", "gpt-4o-mini-tts"),
        "voice": cfg.get("voice", "nova"),
        "input": text,
        "response_format": "mp3",
        "instructions": cfg.get("instructions", DEFAULT_INSTRUCTIONS),
    }
    if cfg.get("speed"):
        payload["speed"] = cfg["speed"]
    return _post("https://api.openai.com/v1/audio/speech",
                 {"Authorization": f"Bearer {_need('OPENAI_API_KEY')}"}, payload)


def _elevenlabs(text, cfg):
    voice_id = cfg.get("voice") or sys.exit("Za ElevenLabs nastavi voice (voice_id).")
    payload = {"text": text, "model_id": cfg.get("model", "eleven_multilingual_v2")}
    if cfg.get("language"):
        payload["language_code"] = cfg["language"]
    return _post(f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format=mp3_44100_128",
                 {"xi-api-key": _need("ELEVENLABS_API_KEY")}, payload)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("text")
    ap.add_argument("--out", default="tts_test.mp3")
    ap.add_argument("--provider", default="openai")
    ap.add_argument("--voice")
    a = ap.parse_args()
    load_env(Path.cwd())
    cfg = {"provider": a.provider}
    if a.voice:
        cfg["voice"] = a.voice
    out = Path(a.out)
    synth(a.text, out, cfg, out.parent / ".tts_cache")
    print(out.resolve())


if __name__ == "__main__":
    main()

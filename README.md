# posnetki-aplikacije: Claude skill za video navodila

Claude skill, ki posname postopek v naši spletni aplikaciji, ga zmontira v kratek video
(naslovi, napisi, zoom, zameglitev osebnih podatkov) in po želji doda slovenski voiceover ter
podnapise `.srt`.

Namenjen je **Claude aplikaciji v načinu Cowork** (Windows x64 / Mac Apple Silicon, plačljiv
paket). Deluje tudi v Claude Code.

## Namestitev

1. Prenesi [`dist/posnetki-aplikacije.zip`](dist/posnetki-aplikacije.zip) (gumb *Download raw file*).
2. Claude aplikacija → **Nastavitve → Zmožnosti (Capabilities) → Skills → Upload skill** → izberi zip.
3. Za umetni glas: v mapo projekta dodaj datoteko `.env` z vrstico `OPENAI_API_KEY=...`.

Claude Code: `posnetki-aplikacije/` skopiraj v `~/.claude/skills/`.

## Kako deluje

```
scenarij  →  snemanje (OS snemalnik; klika Claude in Chrome ali uporabnik)
          →  frames.py (Claude si posnetek ogleda na preglednih slikah s časi)
          →  plan.json (odseki, napisi, zoom, blur, besedilo glasu)
          →  render.py (TTS → izmeri glas → posnetek pospeši/zadrži na dolžino glasu → MP4 + SRT)
```

| datoteka | namen |
|---|---|
| `SKILL.md` | potek dela za Claude |
| `references/plan.md` | format `plan.json` |
| `references/snemanje.md` | snemanje na Windows/Mac, način s Claude in Chrome |
| `references/tezave.md` | omrežje v Cowork, ključi, pogoste napake |
| `scripts/setup.py` | namesti Pillow, requests, ffmpeg (`imageio-ffmpeg`) |
| `scripts/frames.py` | pregledne slike in okvirji z mrežo |
| `scripts/tts.py` | OpenAI / ElevenLabs TTS s predpomnilnikom |
| `scripts/render.py` | montaža |

Pisava Noto Sans je pod licenco SIL OFL (`assets/fonts/OFL.txt`).

## Nova verzija paketa

Po spremembah v `posnetki-aplikacije/` znova zapakiraj zip (vsebovati mora mapo
`posnetki-aplikacije/` na vrhu) in ga ponovno naloži v Claude.

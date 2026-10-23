# plan.json

Poti so relativne na mapo, v kateri je `plan.json`. Časi so v sekundah (decimalke dovoljene).

```json
{
  "output": "izvoz/prejeti-racun.mp4",
  "size": [1920, 1080],
  "fps": 30,
  "voice": {"provider": "openai", "voice": "nova"},
  "theme": {"accent": "#E30613", "background": "#0F1218"},
  "music": {"file": "glasba/podlaga.mp3", "volume": 0.08},
  "segments": [
    {"type": "title", "text": "Kako vnesemo prejeti račun", "subtitle": "Pro.4 · Finance",
     "voiceover": "V tem videu pokažem, kako v dveh minutah vnesemo prejeti račun."},

    {"type": "clip", "source": "posnetki/posnetek1.mp4", "start": 3.2, "end": 11.8,
     "caption": "Finance › Prejeti računi › Nov",
     "voiceover": "V levem meniju odpremo Finance in izberemo Prejeti računi. Zgoraj desno kliknemo Nov."},

    {"type": "clip", "source": "posnetki/posnetek1.mp4", "start": 14.0, "end": 22.5,
     "zoom": {"x": 0.30, "y": 0.20, "w": 0.45, "h": 0.45, "at": 0.5, "ease": 0.6},
     "blur": [{"x": 0.62, "y": 0.31, "w": 0.18, "h": 0.05}],
     "voiceover": "Vpišemo dobavitelja. Program predlaga zadnje uporabljene partnerje."},

    {"type": "image", "source": "posnetki/zaslon-rezultat.png", "duration": 3,
     "caption": "Račun je shranjen"},

    {"type": "title", "text": "To je vse!", "subtitle": "Vprašanja: podpora@pro-bit.si", "duration": 2.5}
  ]
}
```

## Vrhnja polja

| polje | privzeto | pomen |
|---|---|---|
| `output` | `izvoz/video.mp4` | končna datoteka; `.srt` se zapiše poleg |
| `size`, `fps` | `[1920,1080]`, `30` | posnetki drugih velikosti se pomanjšajo/povečajo z obrobo |
| `voice` | brez | nastavitve TTS; brez tega je `voiceover` napaka (razen z `voice_file`) |
| `voice.provider` | `openai` | ali `elevenlabs` (takrat je `voice` = voice_id, ključ `ELEVENLABS_API_KEY`) |
| `voice.voice` | `nova` | OpenAI glas |
| `voice.instructions` | umirjena slovenščina | navodilo za slog govora (samo OpenAI) |
| `voice.speed` | 1.0 | 0.25–4.0 |
| `theme.accent` | `#E30613` | barva črtice pri napisih in naslovih |
| `theme.background` | `#0F1218` | ozadje naslovnih kartic in obrob |
| `music` | brez | tiha podlaga čez cel video, z odtekanjem na koncu; `volume` 0.05–0.12 |

## Segmenti

Skupno vsem: `voiceover` (besedilo za TTS) **ali** `voice_file` (njen posnetek, npr.
`glas/03.m4a`; `voiceover` takrat služi le za podnapise), `caption` (napis spodaj levo).

**`title`**: `text`, `subtitle`, `duration` (najmanj; če je glas daljši, traja do konca glasu).

**`clip`**: odsek posnetka (`.mp4`, `.mov`, `.webm`, `.mkv`, tudi `.gif`).
- `start`, `end`: odsek v izvornem posnetku. Brez `end` = do konca.
- `fit` (ko ima segment glas): `auto` (privzeto: predolg odsek se pospeši do `max_speed`,
  prekratek se zadrži na zadnji sliki), `speed` (lahko tudi upočasni), `freeze` (samo zadrži),
  `none` (dolžino določa odsek, glas se lahko odreže).
- `max_speed`: privzeto 4. Nad ~3× je premikanje miške že nemirno.
- `speed`: ročna hitrost, ko segment nima glasu (npr. 2 za dolgočasno tipkanje).
- `zoom`: `{x, y, w, h}` pravokotnik v deležih slike (0–1), `at` = kdaj začne (s od začetka
  segmenta), `ease` = trajanje približevanja. Razmerje se ohrani (vzame se ožja stran), zato
  pravokotnik v razmerju 16:9 da najbolj predvidljiv rezultat. Ne približuj bolj kot ~2.5×,
  ker postane slika mehka.
- `blur`: seznam `{x, y, w, h, strength}` v deležih **izvornega** posnetka; velja čez cel
  segment. `strength` privzeto 18.
- `keep_audio`: `true` ohrani zvok posnetka (privzeto se zavrže; ignorira se, če je glas).

**`image`**: posnetek zaslona (`.png`, `.jpg`); `duration`, plus `caption`, `zoom`, `blur`.

## Nasveti

- En segment = en korak = en blok glasu. Lažje popravljaš in podnapisi so lepo razdeljeni.
- Za napise uporabi `›` za poti po menijih (puščice `→` se samodejno zamenjajo).
- Napis zakrije spodnji levi del (~45 % širine, ~12 % višine). Če je tam pomemben gumb,
  napis izpusti ali uporabi zoom.
- Zamrznitev daljša od ~3 s deluje kot zatik: raje vzemi daljši odsek ali skrajšaj besedilo.

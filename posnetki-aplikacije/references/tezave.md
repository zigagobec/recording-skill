# Težave in rešitve

**`setup.py` javi NE pri ffmpeg ali Pillow.** Cowork je brez dostopa do PyPI. Prosi
uporabnico, naj v Claude nastavitvah dovoli omrežni dostop za kodo (Nastavitve → Zmožnosti /
Capabilities → dostop do omrežja / domene) in doda `pypi.org` ter `files.pythonhosted.org`,
nato poskusi znova. Če ne gre, lahko posnetke vsaj pregleda in pripraviš scenarij; montažo
pa naredi nekdo s terminalom (Žiga) z istim `plan.json`.

**TTS: »Ni povezave do api.openai.com« / »api.elevenlabs.io«.** Ista nastavitev kot zgoraj,
domena `api.openai.com` (ali `api.elevenlabs.io`). Druga možnost: njen glas (`voice_file`).

**TTS: »Manjka OPENAI_API_KEY«.** V projektni mapi ustvari datoteko `.env` z vrstico
`OPENAI_API_KEY=sk-...` (ključ ji da Žiga). Ključa ne kopiraj v klepet ali v plan.json.

**TTS napaka 401/429.** 401 = napačen ključ; 429 = ni dobroimetja ali preveč zahtev naenkrat.

**Posnetek je na omrežnem disku.** Ukazi v Cowork ne vidijo omrežnih map: naj ga kopira v
lokalno projektno mapo.

**Snipping Tool shrani `.mp4` z variabilno hitrostjo sličic.** Ni težava: `render.py` vse
pretvori na 30 fps.

**Slovenske črke ali besede glas izgovori narobe.** Zapiši fonetično (»Pro štiri«, »ePorezi«
→ »e-Porezi«), kratice razstavi, števila napiši z besedo. Nato ponovno render (spremenjeni
bloki se sintetizirajo znova, ostali pridejo iz predpomnilnika).

**Video je preveč mehak pri zoomu.** Izvorni posnetek je majhen (npr. 1366×768). Manjši zoom
(do ~2×) ali snemaj z večjo povečavo strani.

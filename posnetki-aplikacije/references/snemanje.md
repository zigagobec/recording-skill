# Snemanje zaslona

## Priprava (vedno)

1. **Testno okolje in izmišljeni podatki.** Pred snemanjem preveri, da je v aplikaciji
   prijavljena v testno okolje (v Pro.4 je zgoraj oznaka »TESTNO OKOLJE«) ali v demo podjetje.
2. **En zavihek, čist brskalnik:** zapre druge zavihke, skrije zaznamke (Ctrl+Shift+B),
   izklopi obvestila (Teams, Outlook) ali vklopi »Ne moti« (Windows: Win+N → Ne moti).
3. **Velikost okna:** brskalnik maksimiziran na glavnem zaslonu. Povečava strani 100–125 %;
   pri majhnih zaslonih (1366×768) raje 100 %, da se vidi celoten obrazec.
4. Pripravi začetno stanje (prava stran odprta, prijava opravljena), da se posnetek začne
   s prvim korakom in ne s prijavo.

## Kako posname ona

**Windows 11:**
- *Orodje za izrezovanje* (Snipping Tool): Win+Shift+R → izbere območje (okno brskalnika)
  → Začni. Ustavi z rdečim gumbom. Novejše verzije posnetek samodejno shranijo v
  `Videoposnetki\Posnetki zaslona` (Videos\Screen Recordings), starejše ga odprejo v orodju
  → Shrani kot. V obeh primerih ga premakne v `posnetki/`.
- Ali *Xbox Game Bar*: Win+Alt+R začne/ustavi snemanje aktivnega okna. Posnetki gredo v
  `Videoposnetki\Posnetki` (Videos\Captures); premakni ga v `posnetki/`.

**Mac:** Cmd+Shift+5 → »Posnemi izbrani del« → izbere okno brskalnika → Posnemi. Ustavi z
gumbom v menijski vrstici; posnetek je na namizju.

Zvoka med snemanjem ne rabimo (glas dodamo kasneje), zato mikrofon lahko ostane izklopljen.

## Način A: Claude klika, ona snema (Claude in Chrome)

1. Odpri aplikacijo v novem zavihku (`tabs_create_mcp`, `navigate`) in preveri, da vidiš
   pravo stran in da je prijavljena (če ni, naj se prijavi sama; gesel ne vpisuj ti).
2. Reci ji: »Kazalec miške umakni iz okna brskalnika, zaženi snemanje okna in mi napiši
   *začni*.« Tvoji kliki pravega kazalca ne premikajo; kazalec, ki obvisi sredi okna, bi
   gledalca zmedel. Ker se kazalec ne vidi, vsak klik pri montaži označi z `zoom` ali
   `caption`.
3. Počakaj ~2 s, nato izvajaj korake scenarija. Po vsakem koraku počakaj, da se stran
   naloži, in še ~1,5 s, da gledalec vidi rezultat. Vnašaj besedilo z realnimi, izmišljenimi
   podatki (»Testni dobavitelj d.o.o.«, ne »asdf«).
4. Na koncu pusti rezultat na zaslonu 3 s in ji reci: »Ustavi snemanje in shrani v posnetki/.«
5. Med koraki ji ne piši dolgih sporočil; ona naj ne premika miške čez okno.
6. Če se v posnetku vidi Claude-ov indikator v brskalniku ali stranska plošča, tisti del pri
   montaži skrij z `zoom` ali pa naj pred snemanjem zapre stransko ploščo.

Pomanjkljivost: med tvojimi koraki so premori. To je v redu, saj pri montaži izrežeš ali
pospešiš mrtve dele. Zato je pregled s `frames.py` obvezen.

## Način B: ona klika po seznamu

Daj ji oštevilčen seznam kratkih navodil (»3. Klikni *Nov* zgoraj desno«). Prosi jo:
- naj dela počasneje kot običajno in po vsakem kliku za trenutek umiri miško,
- naj ob napaki ne ustavi snemanja, ampak le ponovi korak (slabi del izrežeš),
- naj posname lahko v več kosih (`posnetek1.mp4`, `posnetek2.mp4` …).

## Način C: kratek GIF (brez glasu)

Za 5–20 s animacijo (npr. v e-pošto ali Confluence) uporabi `gif_creator` iz Claude in Chrome:
začni snemanje, naredi korake, ustavi in izvozi. GIF pristane v brskalnikovi mapi Prenosi;
prosi jo, naj ga premakne v `posnetki/`. Dobljeni GIF lahko tudi uporabiš kot `clip`
v planu ali ga s `render.py` spremeniš v MP4 z napisi.

## Posnetki zaslona namesto videa

Če aplikacija dela počasi ali se korak ne da lepo posneti, uporabi posamezne posnetke
zaslona (ona: Win+Shift+S / Cmd+Shift+4; ti: `computer` → screenshot ne shrani datoteke,
zato naj jih ona shrani v `posnetki/`). V planu so `image` segmenti z `zoom` in `caption`.

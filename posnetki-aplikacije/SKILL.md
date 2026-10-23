---
name: posnetki-aplikacije
description: Posname zaslon naše spletne aplikacije (Pro-Bit / Pro.4 / probit one ali katerekoli druge v brskalniku), posnetke zmontira v kratek video z naslovi, napisi, zoomom in zameglitvijo osebnih podatkov ter po želji doda slovenski voiceover (umetni glas ali lasten posnetek) in podnapise. Uporabi ta skill VEDNO, ko uporabnik omeni posnetek zaslona, screen recording, video navodila, tutorial, demo, predstavitveni video, "posnemi kako se ...", GIF za navodila, voiceover ali montažo posnetkov aplikacije, tudi če ne reče izrecno "video".
---

# Posnetki aplikacije: posnemi → zmontiraj → ozvoči

Cilj je kratek, jasen video, ki kolegu ali stranki pokaže, kako se nekaj naredi v aplikaciji.
Gledalec mora vsak klik videti dovolj dolgo, da mu sledi, ne sme pa čakati na nalaganje.
Ves postopek temelji na enem triku: **najprej glas, nato slika**. Vsak blok besedila se
pretvori v govor in izmeri, nato `render.py` posnetek tega koraka pospeši ali zadrži na
zadnji sliki, da traja točno toliko kot glas. Zato ni ročnega usklajevanja časov in vsak
popravek je le ponoven zagon.

Uporabnica je praviloma netehnična in dela v **Claude aplikaciji (Cowork)**, ne v terminalu.
Pogovarjaj se slovensko, brez žargona, in ji vse tehnično prihrani. Ukaze poganjaš ti.

## 0. Preveri okolje (enkrat na začetku)

- **Mapa projekta:** delaj v mapi, ki jo je izbrala v Cowork (npr. `Videi/<tema>`). Če je ni,
  jo prosi, naj jo izbere. Struktura: `posnetki/` (surovi posnetki), `glas/` (njeni
  posnetki glasu, če jih ima), `plan.json`, `izvoz/` (končni video).
- **Python:** v Cowork VM je ukaz običajno `python3`; spodaj piše `python`, uporabi tistega,
  ki obstaja.
- **Orodja:** zaženi `python <skill>/scripts/setup.py`. Namesti Pillow, requests in ffmpeg
  (prek `imageio-ffmpeg`, če sistemskega ni). Če javi NE, preberi `references/tezave.md`.
- **Brskalnik:** če imaš orodja Claude in Chrome, lahko klikaš po aplikaciji namesto nje.
  Če jih nimaš, ona klika po tvojem seznamu korakov. Oboje deluje.
- Če sploh nimaš izvajanja kode (navaden klepet brez Cowork), ji povej, da za montažo
  potrebuje Cowork, in ji vmes vseeno pripravi scenarij in seznam korakov za snemanje.

## 1. Razjasni nalogo (kratko, največ 3 vprašanja naenkrat)

Kaj pokazati (en postopek na video), komu je namenjen (sodelavci, stranke), približna
dolžina (privzeto 1–3 min), ali želi glas (umetni / njen / brez) in ali rabi samo kratek GIF.
Če je kaj očitno iz prošnje, ne sprašuj.

## 2. Scenarij pred snemanjem

Napiši tabelo korakov: `# | kaj se klikne/vpiše | besedilo za glas | napis na zaslonu`.
Pravila za besedilo glasu, ker ga bo bral umetni glas:
- 1–3 kratki stavki na korak; slovenščina gre ~120 besed/min, torej 2 min ≈ 240 besed.
- Govori o tem, *zakaj* in *kaj opaziš*, ne samo »kliknemo tukaj«.
- Kratice in števila zapiši tako, kot naj se izgovorijo (»de-de-ve«, »dvaindvajset odstotkov«).
- Imena menijev zapiši natanko kot v aplikaciji, da se ujemajo z zaslonom.
Pokaži ji tabelo in počakaj na potrditev; popravek scenarija je poceni, ponovno snemanje ne.

## 3. Snemanje

Podrobna navodila: **`references/snemanje.md`**. Na kratko:
- **Snema vedno OS snemalnik** (Windows: Orodje za izrezovanje → Snemaj, ali Win+Alt+R;
  Mac: Cmd+Shift+5). Ti ne moreš sam zagnati snemanja zaslona.
- **Način A (če imaš Claude in Chrome):** ona zažene snemanje, ti po scenariju klikaš po
  aplikaciji, med koraki počakaš ~2 s, da je stanje na zaslonu jasno. Ona ustavi.
  Pozor: tvoji kliki ne premikajo pravega kazalca miške, zato se v posnetku kazalec ne
  premika. Prosi jo, naj pred snemanjem kazalec umakne iz okna, in vsak klik pri montaži
  pokaži z `zoom` in/ali `caption`. Kjer je gledalcu pomembno videti kazalec (»kje točno
  kliknem«), raje izberi način B.
- **Način B:** ona klika po tvojem seznamu, počasi, z miško pri miru po vsakem kliku.
  Najbolj naraven rezultat za navodila.
- **Način C (kratek GIF brez glasu):** orodje `gif_creator` iz Claude in Chrome. GIF se
  shrani v mapo Prenosi v brskalniku, ne v projektno mapo: prosi jo, naj ga premakne v
  `posnetki/`.
- **Zasebnost:** snemaj v testnem okolju z izmišljenimi podatki. Pravih strank, davčnih
  številk, IBAN-ov, plač in zdravstvenih podatkov ne sme biti v videu. Če so, jih zamegli
  (`blur` v planu) in ji to izrecno povej.
- Ko konča, naj posnetek shrani v `posnetki/` (ali ti pove, kje je, in ga kopiraš tja).

## 4. Poglej posnetek

Ne ugibaj časov. Poglej:
```
python <skill>/scripts/frames.py posnetki/posnetek1.mp4                    # pregled
python <skill>/scripts/frames.py posnetki/posnetek1.mp4 --from 20 --to 40 --step 0.5
python <skill>/scripts/frames.py posnetki/posnetek1.mp4 --at 31.5           # mreža 10 %
```
Odpri izpisane PNG-je. Za vsak korak scenarija si zapiši začetek in konec (od tik pred
klikom do trenutka, ko je rezultat viden). Preskoči nalaganje, tipkarske napake, iskanje
po meniju. Na sliki z mrežo odčitaš pravokotnike za `zoom` in `blur` (deleži 0–1).
Preveri tudi, ali so kje vidni osebni podatki.

## 5. Napiši plan.json

Format in vse možnosti: **`references/plan.md`**. Struktura: naslovna kartica → en `clip`
na korak (z `voiceover` in po potrebi `caption`, `zoom`, `blur`) → zaključna kartica.
Izberi odseke, ki so približno tako dolgi kot njihov glas: `render.py` izpiše pospešitev in
zamrznitev za vsak segment; več kot ~3 s zamrznitve ali pospešitev nad ~3× pomeni, da je
odsek napačno dolg, zato ga popravi.

## 6. Zmontiraj in preveri

```
python <skill>/scripts/render.py plan.json --draft      # hiter osnutek 960x540
python <skill>/scripts/frames.py izvoz/<ime>_osnutek.mp4 --step 1
python <skill>/scripts/render.py plan.json --only 4     # samo segment 4 (brez glasbe)
python <skill>/scripts/render.py plan.json              # končno 1920x1080
```
Pred oddajo si osnutek *poglej* (pregledne slike): ali se napisi ne prekrivajo s
pomembnim delom zaslona, ali zoom pokaže pravo mesto, ali je zamegljeno vse občutljivo.
Glas je predpomnjen (`.tts_cache/`), zato ponovni zagoni po vizualnih popravkih ne stanejo nič.

## 7. Oddaj

Povej ji, kje je `izvoz/<ime>.mp4` in `.srt` (podnapisi, za YouTube/Teams/LMS), dolžino in
kratek opis segmentov. `plan.json` pusti v mapi: za popravek (»spremeni stavek v koraku 3«)
spremeniš plan in znova zaženeš render. Ponudi eno ali dve konkretni izboljšavi.

## Glas

- **Umetni glas (privzeto OpenAI `gpt-4o-mini-tts`, glas `nova`):** v projektni mapi (ali
  mapi nad njo) mora biti datoteka `.env` z vrstico `OPENAI_API_KEY=...`. Ključa nikoli ne
  izpisuj v klepet ali v plan in je ne prosi, naj ti ga prilepi. Če datoteke ni, ji povej,
  naj jo zahteva od Žiga (pošlje pripravljeno) ali jo naredi v Beležnici (glej
  `references/tezave.md`). Za drug glas preizkusi: `python <skill>/scripts/tts.py "Pozdravljeni." --voice shimmer`
  (glasovi: nova, shimmer, coral, sage, alloy, onyx, ash, echo). Podprt je tudi ElevenLabs.
- Cowork ima omejen dostop do interneta; če TTS javi »Ni povezave do api.openai.com«, mora
  uporabnica domeno dovoliti v nastavitvah (glej `references/tezave.md`).
- **Njen glas:** daj ji oštevilčen seznam stavkov, ona vsakega posname (Diktafon/Voice Memos)
  in shrani kot `glas/01.m4a`, `glas/02.m4a` … V planu `voice_file` namesto TTS. Tišino na
  začetku/koncu posnetka render ne odreže, zato naj začne govoriti takoj.
- **Brez glasu:** izpusti `voice` v planu; dolžino segmentov določajo `start/end/speed`,
  razlago nosijo `caption` napisi.

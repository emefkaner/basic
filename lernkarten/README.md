# Lernkarten für das lupilu LCD Schreibpad

Eigene Karten im Originalformat, zum Einschieben in die Tasche des Schreibpads.

## Was das Gerät vorgibt

Quelle: **Gebrauchsanweisung von Delta-Sport, IAN 513251_2501**
(https://manuals.sit-connect.com/public/articlemanual/eb3c2d8c-28f1-4c58-abc0-6838df7197dc.pdf)

| Angabe | Wert | Woher |
|---|---|---|
| Artikel gesamt | ca. 220 × 156 × 15 mm | Anleitung, „Technische Daten" |
| Display | 8,5 Zoll | Anleitung |
| Lernkarten im Lieferumfang | 10 Stück, beidseitig bedruckt | Anleitung |
| **Kartenformat** | **ca. 193 × 123 mm** | **nur Händlerangabe, siehe unten** |

**Wichtig:** Das Kartenformat steht *nicht* in der Anleitung. Es stammt aus den
Händlertexten (discounto.de, preisrunter.de). Deshalb gibt es die Passprobe.

So funktioniert das Gerät laut Abbildung A der Anleitung: Es ist eine
aufklappbare Mappe. **Links** sitzt eine Tasche, in die die Lernkarte **von oben**
eingeschoben wird; **rechts** liegt der LCD-Bildschirm. Man malt das Motiv also
*daneben* ab, nicht durch die Karte hindurch — die Karte muss deshalb gut
erkennbar sein, nicht durchscheinend.

Die Tasche hat oben eine bogenförmige Kante mit Daumenausschnitt. Der obere
Streifen der Karte verschwindet dahinter. Darum bleiben oben **20 mm** frei.

## Passprobe — bitte einmal machen

1. Datei `ausgabe/passprobe.pdf` öffnen und drucken.
2. Im Druckdialog die Skalierung auf **100 %** stellen (nicht „an Seite
   anpassen", nicht „Passend skalieren").
3. Mit einem Lineal den schwarzen Balken unten nachmessen. Er muss **genau
   100 mm** lang sein. Ist er kürzer, hat der Drucker verkleinert — dann
   zurück zu Schritt 2.
4. Eine echte Lernkarte auf den schwarzen Rahmen legen.
   - **Deckt sie sich:** passt, fertig.
   - **Deckt sie sich nicht:** an der Millimeterskala oben und links ablesen,
     um wie viel sie abweicht, und die Zahlen melden.
5. Zusätzlich mit dem Lineal messen, **wie viel von der Karte oben hinter der
   Taschenkante verschwindet**, wenn sie eingeschoben ist (in der Mitte und am
   Rand). Damit lässt sich der obere Rand von 20 mm genau einstellen.

## Bild in ein SVG verwandeln

Fotos und PNGs werden beim Drucken schnell unscharf; SVG bleibt bei jeder
Größe scharf. Ausmalbilder (schwarze Linien auf hellem Grund) lassen sich
automatisch umwandeln:

```
python3 lernkarten/vektorisieren.py bild.png lernkarten/motive/pooh.svg
```

Das Skript rechnet hoch, wirft alles Helle weg (Holzmaserung, Papierton,
Raster), schneidet auf das Motiv zu und lässt `potrace` Kurven daraus machen.
Voraussetzungen: `pip install pillow` und `apt-get install -y potrace`.

Bleiben zu viele Flecken übrig oder verschwinden feine Linien:
`--schwelle` verstellen (Standard 128, höher = mehr wird als Linie erkannt).

## Karten bauen

```
PLAYWRIGHT_CHROMIUM=/opt/pw-browsers/chromium node lernkarten/bauen.mjs
```

- Motive liegen in `motive/` (SVG, PNG, JPG).
- Welche Karte welches Motiv bekommt, steht in `karten.json`.
- Ergebnis in `ausgabe/`: **`karten.pdf`** zum Drucken und **`karten.html`**
  zum Ansehen und Weiterbasteln (A4 quer, zwei Karten je Blatt, gestrichelte
  Schnittlinie). Das HTML ist in sich geschlossen — die Bilder stecken als
  Datenadresse darin, es lässt sich also einfach im Browser öffnen.
  Dasselbe gilt für `passprobe.html` / `passprobe.pdf`.
- Maße und Ränder stehen zentral in `mass.mjs`.

## Drucken und zuschneiden

1. `ausgabe/karten.pdf` mit **100 %** Skalierung drucken (siehe Passprobe).
2. Papier: **200–250 g/m² Karton**. Normales 80-g-Papier knickt beim
   Einschieben.
3. Schneiden: Jede Karte hat eine **durchgezogene graue Umrandung** genau auf
   der Schnittkante, dazu **Schnittmarken** in den Blatträndern. Für einen
   geraden Schnitt das Lineal an zwei gegenüberliegende Marken anlegen. Die
   graue Linie selbst mit wegschneiden, dann bleibt kein Rand stehen.

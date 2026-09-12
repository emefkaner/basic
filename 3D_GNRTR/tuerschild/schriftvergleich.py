#!/usr/bin/env python3
"""Schriftarten fuer den Schriftzug vergleichen -- Aussehen UND Druckbarkeit.

Fuer jede Kandidatin wird der Name in der echten Zielbreite gesetzt und
gemessen:

  duennste Stelle -- die schmalste Stelle im ganzen Schriftzug, ueber die
      Mittelachse bestimmt (Raster + Distanztransformation, nicht per
      Augenmass). Unter etwa 1,2 mm wird eine Stelle bei 0,4 mm Duese zur
      Sollbruchstelle: zwei Linien Wand und nichts dazwischen.
  Inseln/Stege -- wieviele lose Teile die Schrift hat und wieviele
      Verbindungsstege noetig sind, damit ein Stueck daraus wird. Jeder
      Steg ist eine sichtbare Bruecke im Schriftbild.
  Hoehe -- bei fester Breite; hohe Schriften brauchen mehr Platz auf dem
      Buchstaben und rutschen leichter darueber hinaus.

    python3 schriftvergleich.py            # alle Kandidatinnen
    python3 schriftvergleich.py --name Mia

Ausgabe: Tabelle auf der Konsole und stl/schriftvergleich.svg -- alle
Vorschlaege untereinander, jeweils ueber dem grossen Buchstaben, so wie
sie am Ende an der Tuer haengen.
"""

import argparse
import os
import sys

HIER = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HIER)
import generate as G                                                 # noqa: E402

DUENN_WARN = 1.2      # mm, darunter wird es bei 0,4 mm Duese heikel


# ---------------------------------------------------------------------------
# Messung: Raster, Distanztransformation, duennste Stelle
# ---------------------------------------------------------------------------

# rastern/distanzen/strichbreiten stehen jetzt in generate.py -- die
# Strichbreitenmessung wird auch dort gebraucht (Urteil ueber die Dicke
# der Verbindungen), und zweimal dasselbe Raster waere Unsinn.
rastern = G.rastern
distanzen = G.distanzen
strichbreiten = G.strichbreiten


# ---------------------------------------------------------------------------
# Kandidatinnen durchrechnen
# ---------------------------------------------------------------------------

def messen(schluessel, name, b_br, b_ho, traeger=()):
    """Einen Schriftzug in einer Schrift setzen und bewerten."""
    titel, pfad, art, gewicht = G.SCHRIFTEN[schluessel]
    if gewicht is not None:
        titel += " (Gewicht %.0f)" % gewicht
    alt_g, G.GEWICHT = G.GEWICHT, gewicht
    f = G.font(pfad)
    G.GEWICHT = alt_g
    fehlt = [z for z in name if ord(z) not in f.getBestCmap()]
    if fehlt:
        return {"titel": titel, "art": art,
                "fehler": "Zeichen fehlen: " + "".join(fehlt)}
    alt, alt_g = G.FONT_NAME, G.GEWICHT
    G.FONT_NAME, G.GEWICHT = pfad, gewicht
    try:
        (_, n_gl, stege, abst, n_br, n_ho, (dx, dy),
         ruhend) = G.teil_name(name, b_br, b_ho, traeger)
    finally:
        G.FONT_NAME, G.GEWICHT = alt, alt_g
    inseln = len(G.komponenten([a for a, _ in n_gl]))
    # ohne die Stege messen -- die sind per Definition STEG_BREITE
    # schmal und wuerden sonst bei jeder Schrift als "duennste
    # Stelle" herauskommen. Gemessen wird die Schrift selbst.
    duenn, minimal, mittel = strichbreiten(n_gl, ())
    return {"titel": titel, "art": art, "glyphen": n_gl, "stege": stege, "abst": abst,
            "breite": n_br, "hoehe": n_ho, "dx": dx, "dy": dy,
            "inseln": inseln, "ruhend": ruhend, "duenn": duenn, "min": minimal, "mittel": mittel,
            "fehler": None}


# ---------------------------------------------------------------------------
# Blatt mit allen Vorschlaegen
# ---------------------------------------------------------------------------

SPALTEN = 2


def blatt(name, zeichen, b_gl, b_ho, ergebnisse, ziel):
    """Alle Vorschlaege als Blatt, zweispaltig, jeder ueber dem Buchstaben."""
    s = 1.35                       # Bildpunkte je mm
    kopf, fuss, rand = 62.0, 16.0, 16.0
    xs = [p[0] for e in ergebnisse for a, _ in e["glyphen"] for p in a]
    x0, x1 = min(xs) - 6, max(xs) + 6
    zell_b = (x1 - x0) * s + 2 * rand
    zell_h = b_ho * s + kopf + fuss
    zeilen = (len(ergebnisse) + SPALTEN - 1) // SPALTEN
    W, H = zell_b * SPALTEN, zell_h * zeilen + 42 + 26   # 26 fuer die Fusszeile

    def pfad(k, ox, basis):
        return "M " + " L ".join("%.1f %.1f" % (ox + (x - x0) * s, basis - y * s)
                                 for x, y in k) + " Z "

    z = ['<svg xmlns="http://www.w3.org/2000/svg" width="%.0f" height="%.0f">' % (W, H),
         '<rect width="100%" height="100%" fill="#f4efe8"/>',
         '<text x="%.0f" y="26" font-family="sans-serif" font-size="18" '
         'font-weight="600" text-anchor="middle" fill="#333">Schriftzug "%s" '
         '&#8212; %d Vorschlaege</text>' % (W / 2, name, len(ergebnisse)),
         '<text x="%.0f" y="%.0f" font-family="sans-serif" font-size="12" '
         'text-anchor="middle" fill="#777">Buchstabe %s %.0f mm hoch, '
         'Schriftzug jeweils %.0f mm breit &#8212; gleiche Groesse wie am '
         'fertigen Schild</text>' % (W / 2, H - 14, zeichen, b_ho,
                                     ergebnisse[0]["breite"])]
    for nr, e in enumerate(ergebnisse):
        ox = (nr % SPALTEN) * zell_b + rand
        oy = 42 + (nr // SPALTEN) * zell_h
        basis = oy + kopf + b_ho * s
        z.append('<text x="%.0f" y="%.0f" font-family="sans-serif" '
                 'font-size="16" font-weight="600" fill="#333">%d. %s</text>'
                 % (ox, oy + 18, nr + 1, e["titel"]))
        z.append('<text x="%.0f" y="%.0f" font-family="sans-serif" '
                 'font-size="12" fill="#666">%s</text>' % (ox, oy + 36, e["art"]))
        z.append('<text x="%.0f" y="%.0f" font-family="sans-serif" '
                 'font-size="11" fill="#999">duennste Stelle %.1f mm &#183; %s '
                 '&#183; %.0f x %.0f mm</text>'
                 % (ox, oy + 52, e["duenn"],
                    ("ohne Steg zusammenhaengend" if not e["stege"]
                     else "%d Steg(e)" % len(e["stege"])),
                    e["breite"], e["hoehe"]))
        for a, ls in b_gl:
            z.append('<path d="%s" fill="#e8a9b5" fill-rule="evenodd" '
                     'stroke="#d48fa0" stroke-width="0.5"/>'
                     % "".join(pfad(k, ox, basis) for k in [a] + list(ls)))
        for st in e["stege"]:
            z.append('<path d="%s" fill="#e0d2b8"/>' % pfad(st, ox, basis))
        for a, ls in e["glyphen"]:
            z.append('<path d="%s" fill="#f7efe0" fill-rule="evenodd" '
                     'stroke="#c9b898" stroke-width="0.6"/>'
                     % "".join(pfad(k, ox, basis) for k in [a] + list(ls)))
    z.append("</svg>")
    with open(ziel, "w") as f:
        f.write("\n".join(z))


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--name", default=G.NAME)
    ap.add_argument("--buchstabe", default=None)
    ap.add_argument("--hoehe", type=float, default=G.BUCHSTABE_HOEHE)
    args = ap.parse_args()
    G.BUCHSTABE_HOEHE = args.hoehe
    name = args.name
    zeichen = args.buchstabe or name[0].upper()

    _, b_gl, b_br, b_ho = G.teil_buchstabe(zeichen)
    print("Buchstabe %s: %.0f x %.0f mm -- Schriftzug jeweils %.0f mm breit\n"
          % (zeichen, b_br, b_ho, min(G.NAME_BREITE_FAKTOR * b_br,
                                      G.BETT_X - 2 * G.BETT_RAND)))
    print("%-16s %8s %8s %8s  %6s %5s  %s"
          % ("Schrift", "duennste", "mittel", "Hoehe", "Inseln", "Stege", "Urteil"))
    ergebnisse = []
    for schluessel in G.SCHRIFTEN:
        e = messen(schluessel, name, b_br, b_ho, b_gl)
        if e["fehler"]:
            print("%-16s %s" % (e["titel"], e["fehler"]))
            continue
        e["schluessel"] = schluessel
        urteil = [e["art"]]
        if e["duenn"] < DUENN_WARN:
            urteil.append("ACHTUNG duenne Stellen (%.1f mm)" % e["duenn"])
        if len(e["stege"]) >= 3:
            urteil.append("viele Stege im Schriftbild")
        if e["dy"] < 0 or e["dy"] + e["hoehe"] > b_ho:
            urteil.append("ragt oben/unten ueber den Buchstaben hinaus")
        print("%-16s %6.1f mm %6.1f mm %6.0f mm  %6d %5d  %s"
              % (e["titel"], e["duenn"], e["mittel"], e["hoehe"],
                 e["inseln"], len(e["stege"]), ", ".join(urteil)))
        ergebnisse.append(e)

    ziel = os.path.join(HIER, "stl", "schriftvergleich.svg")
    os.makedirs(os.path.dirname(ziel), exist_ok=True)
    blatt(name, zeichen, b_gl, b_ho, ergebnisse, ziel)
    print("\ngeschrieben:", ziel)
    try:                      # PNG nur, wenn cairosvg da ist -- zum Herumzeigen
        import cairosvg
        png = ziel[:-4] + ".png"
        cairosvg.svg2png(url=ziel, write_to=png)
        print("geschrieben:", png)
    except ImportError:
        print("(fuer ein PNG zusaetzlich: pip install cairosvg)")
    print("Gewaehlte Schrift dann so drucken:  python3 generate.py --schrift "
          + "|".join(e["schluessel"] for e in ergebnisse))


if __name__ == "__main__":
    main()

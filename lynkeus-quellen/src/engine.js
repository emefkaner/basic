// Entfernung des Gemini/Veo-Funkel-Wasserzeichens per umgekehrter Alpha-Mischung.
// Mathematik und Geometrie übernommen aus dearabhin/gemini-watermark-remover (MIT),
// auf Deutsch angepasst und ohne Vue-Abhängigkeit.
//
// Grundidee: Google mischt das weiße Funkel-Logo per Alpha-Compositing ein:
//   endpixel = alpha*255 + (1-alpha)*original
// Kennt man die Alphamaske (aus dem Referenzbild bg_96), lässt sich das
// pixelgenau umkehren:
//   original = (endpixel - alpha*255) / (1-alpha)

const ALPHA_SCHWELLE = 0.002;
const ALPHA_MAX = 0.99;
const LOGO_WERT = 255; // das Logo ist reines Weiß

// Bewährte Standardwerte für Veo-Videos (aus dem Quell-Repo; dort auf echten
// Videos eingestellt). Versatz skaliert hier mit der Auflösung — bei 720p
// entspricht das exakt den Originalwerten (-24/-24).
export function standardWerte(breite, hoehe) {
  const kurz = Math.min(breite, hoehe);
  const versatz = -Math.round(kurz / 30);
  return { staerke: 0.6, versatzX: versatz, versatzY: versatz, groesse: 1 };
}

// Geometrie des Wasserzeichens in FOTOS (aus dem Quell-Repo, exakt):
// über 1024×1024 ein 96er-Stern mit 64 px Abstand, sonst 48er mit 32 px.
export function fotoBox(breite, hoehe) {
  const gross = breite > 1024 && hoehe > 1024;
  const size = gross ? 96 : 48;
  const rand = gross ? 64 : 32;
  return {
    size,
    x: Math.max(0, breite - rand - size),
    y: Math.max(0, hoehe - rand - size),
  };
}

// Bei Fotos ist die Einblendung exakt bekannt: volle Stärke, kein Versatz.
export function fotoStandardWerte() {
  return { staerke: 1, versatzX: 0, versatzY: 0, groesse: 1 };
}

// Grundbox des Veo-Wasserzeichens unten rechts:
// Kantenlänge ≈ kurze Seite/15, Abstand ≈ kurze Seite/10.
export function veoBox(breite, hoehe) {
  const kurz = Math.min(breite, hoehe);
  const size = Math.max(24, Math.min(Math.round(kurz / 15), kurz));
  const rand = Math.round(kurz / 10);
  return {
    size,
    x: Math.max(0, breite - rand - size),
    y: Math.max(0, hoehe - rand - size),
  };
}

// Grundbox + Nutzer-Einstellungen -> endgültige Box.
export function boxAufloesen(basis, breite, hoehe, w) {
  const size = Math.max(8, Math.min(Math.round(basis.size * (w.groesse || 1)), Math.min(breite, hoehe)));
  const x = Math.max(0, Math.min(basis.x + Math.round(w.versatzX || 0), breite - size));
  const y = Math.max(0, Math.min(basis.y + Math.round(w.versatzY || 0), hoehe - size));
  return { size, x, y };
}

// Etwas Rand um die Box, damit auch bei kleinem Versatz alles im Ausschnitt liegt.
export function ausschnitt(breite, hoehe, box) {
  const rand = Math.round(box.size * 0.6);
  const rx = Math.max(0, box.x - rand);
  const ry = Math.max(0, box.y - rand);
  return {
    x: rx,
    y: ry,
    breite: Math.min(breite - rx, box.size + rand * 2),
    hoehe: Math.min(hoehe - ry, box.size + rand * 2),
  };
}

// Funkel-Vorlage auf Box-Größe skalieren und als Alphamaske in den Ausschnitt legen.
export function alphaBauen(vorlageBild, roi, box, staerke) {
  const anzahl = roi.breite * roi.hoehe;
  const karte = new Float32Array(anzahl);
  const offX = box.x - roi.x;
  const offY = box.y - roi.y;

  const c = document.createElement('canvas');
  c.width = box.size; c.height = box.size;
  const cx = c.getContext('2d', { willReadFrequently: true });
  cx.imageSmoothingEnabled = true;
  cx.imageSmoothingQuality = 'high';
  cx.drawImage(vorlageBild, 0, 0, box.size, box.size);
  const daten = cx.getImageData(0, 0, box.size, box.size).data;

  for (let zeile = 0; zeile < box.size; zeile++) {
    for (let spalte = 0; spalte < box.size; spalte++) {
      const zielSpalte = offX + spalte;
      const zielZeile = offY + zeile;
      if (zielSpalte < 0 || zielSpalte >= roi.breite || zielZeile < 0 || zielZeile >= roi.hoehe) continue;
      const o = (zeile * box.size + spalte) * 4;
      const a = (Math.max(daten[o], daten[o + 1], daten[o + 2]) / 255) * staerke;
      if (a > 0) karte[zielZeile * roi.breite + zielSpalte] = Math.min(a, ALPHA_MAX);
    }
  }
  return karte;
}

// Umgekehrte Alpha-Mischung an Ort und Stelle. `pos` beschreibt, wo der
// Ausschnitt (Größe der Alphakarte) innerhalb des ImageData liegt.
//
// `ausbessern`: Für FAST DECKENDE Sterne (GLS-Fall: gemessene Stärke ~1).
// Bei Deckkraft nahe 1 steckt im Pixel keine Hintergrund-Information mehr —
// das Gegenblenden teilt durch fast Null und liefert Müll. Deshalb werden
// deckende Kernpixel stattdessen AUSGEBESSERT: aus den nächsten freien
// Pixeln in alle vier Richtungen, entfernungsgewichtet (Prinzip des
// ffmpeg-delogo-Filters); die halbtransparenten Ränder laufen weiter über
// das Gegenblenden, dazwischen wird weich gemischt.
export function wasserzeichenEntfernen(imageData, alphaKarte, pos, ausbessern = false) {
  const d = imageData.data;
  const B = pos.breite, H = pos.hoehe;
  const wertIdx = (x, y) => ((pos.y + y) * imageData.width + (pos.x + x)) * 4;

  if (!ausbessern) {
    for (let zeile = 0; zeile < H; zeile++) {
      for (let spalte = 0; spalte < B; spalte++) {
        const alpha = alphaKarte[zeile * B + spalte];
        if (alpha < ALPHA_SCHWELLE) continue;
        const idx = wertIdx(spalte, zeile);
        for (let k = 0; k < 3; k++) {
          const gemischt = d[idx + k];
          const original = (gemischt - alpha * LOGO_WERT) / (1 - alpha);
          d[idx + k] = original < 0 ? 0 : original > 255 ? 255 : Math.round(original);
        }
      }
    }
    return;
  }

  // Ausbessern: Deckende Sterne (GLS-Fall) haben oft eine harte, fast binäre
  // Kante, die NICHT zur weichen Alphakante der Vorlage passt — Gegenblenden
  // ließe einen hellen Ring stehen und die Randpixel würden als vermeintlich
  // „freie" Quellen die Füllung vergiften. Deshalb: komplette Sternfläche
  // (Vorlagen-Maske, um 2 px ausgeweitet) aus den nächsten wirklich freien
  // Pixeln in vier Richtungen entfernungsgewichtet rekonstruieren
  // (Prinzip des ffmpeg-delogo-Filters).
  let maske = new Uint8Array(B * H);
  for (let i = 0; i < maske.length; i++) maske[i] = alphaKarte[i] > 0.05 ? 1 : 0;
  for (let runde = 0; runde < 2; runde++) {
    const neu = new Uint8Array(maske);
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < B; x++) {
        if (maske[y * B + x]) continue;
        if ((x > 0 && maske[y * B + x - 1]) || (x < B - 1 && maske[y * B + x + 1]) ||
            (y > 0 && maske[(y - 1) * B + x]) || (y < H - 1 && maske[(y + 1) * B + x])) {
          neu[y * B + x] = 1;
        }
      }
    }
    maske = neu;
  }

  const links = new Int32Array(B * H).fill(-1);
  const rechts = new Int32Array(B * H).fill(-1);
  const oben = new Int32Array(B * H).fill(-1);
  const unten = new Int32Array(B * H).fill(-1);
  for (let y = 0; y < H; y++) {
    let zuletzt = -1;
    for (let x = 0; x < B; x++) {
      if (!maske[y * B + x]) zuletzt = x;
      links[y * B + x] = zuletzt;
    }
    zuletzt = -1;
    for (let x = B - 1; x >= 0; x--) {
      if (!maske[y * B + x]) zuletzt = x;
      rechts[y * B + x] = zuletzt;
    }
  }
  for (let x = 0; x < B; x++) {
    let zuletzt = -1;
    for (let y = 0; y < H; y++) {
      if (!maske[y * B + x]) zuletzt = y;
      oben[y * B + x] = zuletzt;
    }
    zuletzt = -1;
    for (let y = H - 1; y >= 0; y--) {
      if (!maske[y * B + x]) zuletzt = y;
      unten[y * B + x] = zuletzt;
    }
  }

  for (let y = 0; y < H; y++) {
    for (let x = 0; x < B; x++) {
      const i = y * B + x;
      if (!maske[i]) continue;
      const quellen = [];
      if (links[i] >= 0) quellen.push([links[i], y, x - links[i]]);
      if (rechts[i] >= 0) quellen.push([rechts[i], y, rechts[i] - x]);
      if (oben[i] >= 0) quellen.push([x, oben[i], y - oben[i]]);
      if (unten[i] >= 0) quellen.push([x, unten[i], unten[i] - y]);
      if (!quellen.length) continue;

      const ziel = wertIdx(x, y);
      for (let k = 0; k < 3; k++) {
        let summe = 0, gewicht = 0;
        for (const [qx, qy, abstand] of quellen) {
          const g = 1 / (abstand * abstand);
          summe += d[wertIdx(qx, qy) + k] * g;
          gewicht += g;
        }
        d[ziel + k] = Math.round(summe / gewicht);
      }
    }
  }

  // Nachglätten NUR auf der ausgebesserten Fläche: nimmt der Füllung die
  // typische Kreuzschraffur des Richtungs-Interpolierens.
  for (let runde = 0; runde < 2; runde++) {
    const kopie = new Uint8ClampedArray(d.length);
    kopie.set(d);
    for (let y = 0; y < H; y++) {
      for (let x = 0; x < B; x++) {
        if (!maske[y * B + x]) continue;
        const ziel = wertIdx(x, y);
        for (let k = 0; k < 3; k++) {
          let summe = 0, n = 0;
          for (let dy = -1; dy <= 1; dy++) {
            for (let dx = -1; dx <= 1; dx++) {
              const nx = x + dx, ny = y + dy;
              if (nx < 0 || ny < 0 || nx >= B || ny >= H) continue;
              summe += kopie[wertIdx(nx, ny) + k];
              n++;
            }
          }
          d[ziel + k] = Math.round(summe / n);
        }
      }
    }
  }
}

// ---------- Automatische Sternsuche (Mustervergleich) ----------

// Helligkeit eines ImageData als Float32-Feld.
export function luminanzAus(imageData) {
  const d = imageData.data;
  const aus = new Float32Array(imageData.width * imageData.height);
  for (let i = 0; i < aus.length; i++) {
    const o = i * 4;
    aus[i] = 0.299 * d[o] + 0.587 * d[o + 1] + 0.114 * d[o + 2];
  }
  return aus;
}

const vorlagenSpeicher = new Map();
function vorlageAlpha(vorlageBild, s) {
  const schluessel = vorlageBild.src.length + ':' + s;
  if (vorlagenSpeicher.has(schluessel)) return vorlagenSpeicher.get(schluessel);
  const c = document.createElement('canvas');
  c.width = s; c.height = s;
  const cx = c.getContext('2d', { willReadFrequently: true });
  cx.imageSmoothingEnabled = true;
  cx.imageSmoothingQuality = 'high';
  cx.drawImage(vorlageBild, 0, 0, s, s);
  const d = cx.getImageData(0, 0, s, s).data;
  const T = new Float32Array(s * s);
  for (let i = 0; i < T.length; i++) {
    const o = i * 4;
    T[i] = Math.max(d[o], d[o + 1], d[o + 2]) / 255;
  }
  vorlagenSpeicher.set(schluessel, T);
  return T;
}

function nullMittel(T) {
  let m = 0;
  for (let i = 0; i < T.length; i++) m += T[i];
  m /= T.length;
  const Th = new Float32Array(T.length);
  let n2 = 0;
  for (let i = 0; i < T.length; i++) { Th[i] = T[i] - m; n2 += Th[i] * Th[i]; }
  return { Th, n2 };
}

// Normalisierte Kreuzkorrelation an einer Stelle (volle Auflösung).
function nccBei(grau, B, x, y, Th, n2, s) {
  let num = 0, sum = 0, sum2 = 0;
  for (let r = 0; r < s; r++) {
    const gi = (y + r) * B + x;
    const ti = r * s;
    for (let c = 0; c < s; c++) {
      const v = grau[gi + c];
      num += v * Th[ti + c];
      sum += v; sum2 += v * v;
    }
  }
  const n = s * s;
  const varianz = sum2 - (sum * sum) / n;
  if (varianz < 1) return { ncc: -1, sum, n };
  return { ncc: num / Math.sqrt(varianz * n2), sum, n, num };
}

// Sucht den Funkel-Stern im unteren rechten Viertel des Bildes.
// `grau` ist die Helligkeit (bei Videos am besten über mehrere Bilder
// gemittelt: der Stern steht still, der Inhalt bewegt sich).
// Ergebnis: { x, y, size, guete, staerke } oder null.
export function sternSuchen(grau, B, H, vorlageBild, basis) {
  // Grobsuche auf halber Auflösung
  const Bd = B >> 1, Hd = H >> 1;
  const klein = new Float32Array(Bd * Hd);
  for (let y = 0; y < Hd; y++) {
    for (let x = 0; x < Bd; x++) {
      const i = 2 * y * B + 2 * x;
      klein[y * Bd + x] = (grau[i] + grau[i + 1] + grau[i + B] + grau[i + B + 1]) / 4;
    }
  }
  // Summentafeln für Fenster-Mittel/-Varianz in O(1)
  const B1 = Bd + 1;
  const S = new Float64Array(B1 * (Hd + 1));
  const S2 = new Float64Array(B1 * (Hd + 1));
  for (let y = 1; y <= Hd; y++) {
    let zs = 0, zs2 = 0;
    for (let x = 1; x <= Bd; x++) {
      const v = klein[(y - 1) * Bd + x - 1];
      zs += v; zs2 += v * v;
      S[y * B1 + x] = S[(y - 1) * B1 + x] + zs;
      S2[y * B1 + x] = S2[(y - 1) * B1 + x] + zs2;
    }
  }
  const fenster = (x, y, w, h) => {
    const a = y * B1 + x, b = y * B1 + x + w, c = (y + h) * B1 + x, d = (y + h) * B1 + x + w;
    return { sum: S[d] - S[b] - S[c] + S[a], sum2: S2[d] - S2[b] - S2[c] + S2[a] };
  };

  let best = null;
  const x0 = Math.floor(Bd / 2), y0 = Math.floor(Hd / 2);
  for (const skala of [0.75, 0.85, 1, 1.15, 1.3, 1.5]) {
    const s = Math.max(12, Math.round(basis.size * skala));
    const sd = Math.max(8, Math.round(s / 2));
    const { Th, n2 } = nullMittel(vorlageAlpha(vorlageBild, sd));
    for (let y = y0; y <= Hd - sd; y++) {
      for (let x = x0; x <= Bd - sd; x++) {
        let num = 0;
        for (let r = 0; r < sd; r++) {
          const gi = (y + r) * Bd + x;
          const ti = r * sd;
          for (let c = 0; c < sd; c++) num += klein[gi + c] * Th[ti + c];
        }
        const { sum, sum2 } = fenster(x, y, sd, sd);
        const n = sd * sd;
        const varianz = sum2 - (sum * sum) / n;
        if (varianz < 1) continue;
        const ncc = num / Math.sqrt(varianz * n2);
        if (!best || ncc > best.ncc) best = { x: x * 2, y: y * 2, size: s, ncc };
      }
    }
  }
  if (!best) return null;

  // Feinsuche in voller Auflösung rund um den Grobtreffer: erst Größe und
  // Lage gemeinsam, dann noch einmal nachzentrieren.
  let fein = null;
  for (let s = best.size - 6; s <= best.size + 6; s++) {
    if (s < 10) continue;
    const { Th, n2 } = nullMittel(vorlageAlpha(vorlageBild, s));
    for (let dy = -3; dy <= 3; dy++) {
      for (let dx = -3; dx <= 3; dx++) {
        const x = best.x + dx, y = best.y + dy;
        if (x < 0 || y < 0 || x + s > B || y + s > H) continue;
        const e = nccBei(grau, B, x, y, Th, n2, s);
        if (e.ncc > (fein ? fein.ncc : -1)) fein = { x, y, size: s, ncc: e.ncc };
      }
    }
  }
  if (!fein) return null;
  // Nachzentrieren, dann Größe an der neuen Stelle noch einmal nachziehen.
  {
    const { Th, n2 } = nullMittel(vorlageAlpha(vorlageBild, fein.size));
    for (let dy = -2; dy <= 2; dy++) {
      for (let dx = -2; dx <= 2; dx++) {
        const x = fein.x + dx, y = fein.y + dy;
        if (x < 0 || y < 0 || x + fein.size > B || y + fein.size > H) continue;
        const e = nccBei(grau, B, x, y, Th, n2, fein.size);
        if (e.ncc > fein.ncc) fein = { x, y, size: fein.size, ncc: e.ncc };
      }
    }
    for (let s = fein.size - 2; s <= fein.size + 2; s++) {
      if (s < 10 || s === fein.size) continue;
      if (fein.x + s > B || fein.y + s > H) continue;
      const g = nullMittel(vorlageAlpha(vorlageBild, s));
      const e = nccBei(grau, B, fein.x, fein.y, g.Th, g.n2, s);
      if (e.ncc > fein.ncc) fein = { x: fein.x, y: fein.y, size: s, ncc: e.ncc };
    }
  }

  // Stärke direkt messen: Hintergrund = Median eines Rings um den Stern,
  // dann je kräftigem Sternpixel die tatsächliche Deckkraft bestimmen
  // (gemischt = a*255 + (1-a)*Hintergrund  =>  a = (gemischt-b)/(255-b))
  // und der Median über alle Pixel ergibt die Stärke relativ zur Vorlage.
  let staerke = null;
  {
    const s = fein.size;
    const T = vorlageAlpha(vorlageBild, s);
    const rand = Math.round(s / 2);
    const ring = [];
    for (let y = Math.max(0, fein.y - rand); y < Math.min(H, fein.y + s + rand); y++) {
      for (let x = Math.max(0, fein.x - rand); x < Math.min(B, fein.x + s + rand); x++) {
        const drin = x >= fein.x && x < fein.x + s && y >= fein.y && y < fein.y + s;
        if (!drin) ring.push(grau[y * B + x]);
      }
    }
    if (ring.length > 50) {
      ring.sort((a, b) => a - b);
      const hintergrund = ring[ring.length >> 1];
      if (255 - hintergrund > 25) {
        const messungen = [];
        for (let r = 0; r < s; r++) {
          for (let c = 0; c < s; c++) {
            const t = T[r * s + c];
            if (t < 0.35) continue;
            const a = (grau[(fein.y + r) * B + fein.x + c] - hintergrund) / (255 - hintergrund);
            messungen.push(a / t);
          }
        }
        if (messungen.length > 20) {
          messungen.sort((a, b) => a - b);
          // mehr als volle Deckkraft (1,0) gibt es physikalisch nicht
          staerke = Math.max(0.25, Math.min(1, messungen[messungen.length >> 1]));
        }
      }
    }
  }
  return { x: fein.x, y: fein.y, size: fein.size, guete: fein.ncc, staerke };
}

// Ein komplettes Vollbild (ImageData) säubern. Gibt Box + Ausschnitt zurück,
// damit die Oberfläche Hilfslinien zeichnen kann. `basisFn` bestimmt die
// Grundgeometrie (veoBox für Videos, fotoBox für Fotos).
export function bildSaeubern(vorlageBild, imageData, w, basisFn = veoBox, ausbessern = false) {
  const { width: breite, height: hoehe } = imageData;
  const basis = basisFn(breite, hoehe);
  const box = boxAufloesen(basis, breite, hoehe, w);
  const roi = ausschnitt(breite, hoehe, box);
  const karte = alphaBauen(vorlageBild, roi, box, w.staerke);
  wasserzeichenEntfernen(imageData, karte, {
    x: roi.x, y: roi.y, breite: roi.breite, hoehe: roi.hoehe,
  }, ausbessern);
  return { box, roi };
}

// Ab dieser (gemessenen oder eingestellten) Stärke gilt ein Stern als
// praktisch deckend — dann wird zusätzlich ausgebessert. Normale
// Veo-Sterne (0,6) und der pixelgenaue Foto-Weg bleiben davon unberührt.
export const AUSBESSERN_AB = 0.85;

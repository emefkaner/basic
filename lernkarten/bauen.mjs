#!/usr/bin/env node
// Baut druckfertige Lernkarten fuer das lupilu LCD Schreibpad.
//
//   node lernkarten/bauen.mjs            -> Passprobe + Karten
//   node lernkarten/bauen.mjs passprobe  -> nur die Passprobe
//
// Ergebnis liegt in lernkarten/ausgabe/.

import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { dirname, join, extname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { chromium } from 'playwright';
import { KARTE, SICHER, BOGEN, BOGEN_HOCH } from './mass.mjs';

const HIER = dirname(fileURLToPath(import.meta.url));
const AUSGABE = join(HIER, 'ausgabe');
const CHROMIUM = process.env.PLAYWRIGHT_CHROMIUM || undefined;

const TYPEN = {
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.webp': 'image/webp',
  '.svg': 'image/svg+xml',
  '.gif': 'image/gif',
};

function alsDatenAdresse(pfad) {
  const voll = resolve(HIER, pfad);
  if (!existsSync(voll)) throw new Error(`Bild fehlt: ${voll}`);
  const typ = TYPEN[extname(voll).toLowerCase()];
  if (!typ) throw new Error(`Unbekannter Bildtyp: ${voll}`);
  return `data:${typ};base64,${readFileSync(voll).toString('base64')}`;
}

const grundStil = `
  * { box-sizing: border-box; margin: 0; padding: 0; }
  html, body { background: #fff; }
  body { font-family: "DejaVu Sans", Arial, Helvetica, sans-serif; color: #111; }
  .bogen { position: relative; overflow: hidden; page-break-after: always; }
  .bogen:last-child { page-break-after: auto; }
  .karte {
    position: absolute;
    width: ${KARTE.breite}mm;
    height: ${KARTE.hoehe}mm;
    background: #fff;
    /* Schnittlinie: genau auf der Kante, duenn und grau */
    outline: 0.25mm solid #8a8a8a;
    outline-offset: 0;
    overflow: hidden;
  }
  /* Schnittmarken in den Raendern - zum Anlegen des Lineals */
  .marke { position: absolute; background: #333; }
  .inhalt {
    position: absolute;
    left: ${SICHER.links}mm;
    right: ${SICHER.rechts}mm;
    top: ${SICHER.oben}mm;
    bottom: ${SICHER.unten}mm;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 4mm;
  }
  .motiv { flex: 1 1 auto; width: 100%; min-height: 0; display: flex; align-items: center; justify-content: center; }
  .motiv img { max-width: 100%; max-height: 100%; object-fit: contain; }
  .wort {
    flex: 0 0 auto;
    font-size: 11mm;
    font-weight: 700;
    letter-spacing: 0.6mm;
    text-transform: uppercase;
    text-align: center;
    line-height: 1.1;
  }
`;

// Schnittmarken: kurze Striche in den Raendern, in Verlaengerung der vier
// Kartenkanten. Sie liegen NEBEN der Karte, nicht darauf - so bleibt nach dem
// Schneiden nichts davon uebrig. Am Blattrand werden sie gekuerzt, damit sie
// nicht in den nicht bedruckbaren Streifen des Druckers laufen.
function schnittmarken(x, y, b, h) {
  const S = 0.25;   // Strichstaerke in mm
  const L = 4;      // Wunschlaenge der Marke in mm
  const A = 1.5;    // Abstand zur Kartenkante in mm
  const RAND = 3.5; // so nah darf eine Marke an den Blattrand
  const MIN = 1.5;  // kuerzere Marken lohnen nicht
  const m = [];
  const strich = (l, t, w, hh) => m.push(
    `<div class="marke" style="left:${l}mm;top:${t}mm;width:${w}mm;height:${hh}mm;"></div>`);

  // Waagerechte Kanten (oben/unten): je eine Marke links und rechts der Karte.
  for (const kante of [y, y + h]) {
    const t = kante - S / 2;
    const lAnfang = Math.max(RAND, x - A - L);
    const lLang = x - A - lAnfang;
    if (lLang >= MIN) strich(lAnfang, t, lLang, S);

    const rAnfang = x + b + A;
    const rLang = Math.min(L, BOGEN.breite - RAND - rAnfang);
    if (rLang >= MIN) strich(rAnfang, t, rLang, S);
  }

  // Senkrechte Kanten (links/rechts): je eine Marke ueber und unter der Karte.
  for (const kante of [x, x + b]) {
    const l = kante - S / 2;
    const oAnfang = Math.max(RAND, y - A - L);
    const oLang = y - A - oAnfang;
    if (oLang >= MIN) strich(l, oAnfang, S, oLang);

    const uAnfang = y + h + A;
    const uLang = Math.min(L, BOGEN.hoehe - RAND - uAnfang);
    if (uLang >= MIN) strich(l, uAnfang, S, uLang);
  }

  return m.join('');
}

function kartenBogen(karten) {
  const links1 = (BOGEN.breite - (2 * KARTE.breite + BOGEN.spalt)) / 2;
  const links2 = links1 + KARTE.breite + BOGEN.spalt;
  const oben = (BOGEN.hoehe - KARTE.hoehe) / 2;

  const bogenHtml = [];
  for (let i = 0; i < karten.length; i += 2) {
    const paar = karten.slice(i, i + 2);
    const felder = paar.map((k, j) => `
      <div class="karte" style="left:${j === 0 ? links1 : links2}mm; top:${oben}mm;">
        <div class="inhalt">
          <div class="motiv">${k.bildDaten ? `<img src="${k.bildDaten}" alt="">` : ''}</div>
          ${k.text ? `<div class="wort">${k.text}</div>` : ''}
        </div>
      </div>`).join('');
    const marken = paar.map((_, j) =>
      schnittmarken(j === 0 ? links1 : links2, oben, KARTE.breite, KARTE.hoehe)).join('');
    bogenHtml.push(`<div class="bogen" style="width:${BOGEN.breite}mm;height:${BOGEN.hoehe}mm;">${felder}${marken}</div>`);
  }

  return `<!doctype html><meta charset="utf-8"><style>
    @page { size: ${BOGEN.breite}mm ${BOGEN.hoehe}mm; margin: 0; }
    ${grundStil}
  </style>${bogenHtml.join('')}`;
}

function passprobeBogen() {
  const links = (BOGEN_HOCH.breite - KARTE.breite) / 2;
  const oben = 55;

  // Millimeterskala am oberen und linken Rand der Kartenflaeche
  const striche = [];
  for (let mm = 0; mm <= KARTE.breite; mm += 1) {
    const lang = mm % 10 === 0 ? 5 : (mm % 5 === 0 ? 3 : 1.5);
    striche.push(`<div style="position:absolute;left:${links + mm}mm;top:${oben - lang}mm;width:0.15mm;height:${lang}mm;background:#333;"></div>`);
    if (mm % 10 === 0) {
      striche.push(`<div style="position:absolute;left:${links + mm}mm;top:${oben - 9}mm;font-size:2.2mm;transform:translateX(-50%);">${mm}</div>`);
    }
  }
  for (let mm = 0; mm <= KARTE.hoehe; mm += 1) {
    const lang = mm % 10 === 0 ? 5 : (mm % 5 === 0 ? 3 : 1.5);
    striche.push(`<div style="position:absolute;left:${links - lang}mm;top:${oben + mm}mm;height:0.15mm;width:${lang}mm;background:#333;"></div>`);
  }

  return `<!doctype html><meta charset="utf-8"><style>
    @page { size: ${BOGEN_HOCH.breite}mm ${BOGEN_HOCH.hoehe}mm; margin: 0; }
    ${grundStil}
    .kopf { position:absolute; left:12mm; top:10mm; right:12mm; }
    .kopf h1 { font-size:5mm; margin-bottom:2mm; }
    .kopf p { font-size:3.2mm; line-height:1.5; }
    .pruefstrich { position:absolute; left:12mm; top:${oben + KARTE.hoehe + 14}mm; }
    .pruefstrich .balken { width:100mm; height:2mm; background:#111; }
    .pruefstrich span { font-size:3.2mm; display:block; margin-top:1.5mm; }
  </style>
  <div class="bogen" style="width:${BOGEN_HOCH.breite}mm;height:${BOGEN_HOCH.hoehe}mm;">
    <div class="kopf">
      <h1>Passprobe Lernkarte &ndash; lupilu LCD Schreibpad</h1>
      <p>Ohne Skalierung drucken (100 %, nicht &bdquo;an Seite anpassen&ldquo;).
      Danach eine echte Lernkarte auf den Rahmen legen. Deckt sie sich, stimmen
      die Ma&szlig;e. Weicht sie ab: die Abweichung in mm melden.</p>
    </div>
    <div class="karte" style="left:${links}mm; top:${oben}mm; outline:0.3mm solid #111;">
      <div class="inhalt" style="outline:0.2mm dashed #d33; align-items:center; justify-content:center;">
        <div style="font-size:3.2mm;text-align:center;color:#a00;line-height:1.6;">
          gestrichelt = sichtbarer Bereich<br>
          (oben ${SICHER.oben}&nbsp;mm frei wegen der Taschenkante)<br><br>
          Rahmen = ${KARTE.breite} &times; ${KARTE.hoehe}&nbsp;mm
        </div>
      </div>
    </div>
    ${striche.join('')}
    <div class="pruefstrich">
      <div class="balken"></div>
      <span>Dieser Balken muss genau 100&nbsp;mm lang sein. Ist er k&uuml;rzer, hat der Drucker verkleinert.</span>
    </div>
  </div>`;
}

// Schreibt beides: das HTML (in sich geschlossen, Bilder stecken als Daten-
// adresse drin - laesst sich also direkt im Browser oeffnen und anpassen) und
// das daraus gedruckte PDF.
async function schreibe(browser, html, name, quer) {
  writeFileSync(join(AUSGABE, `${name}.html`), html);
  console.log('geschrieben:', `lernkarten/ausgabe/${name}.html`);

  const seite = await browser.newPage();
  await seite.setContent(html, { waitUntil: 'load' });
  await seite.pdf({
    path: join(AUSGABE, `${name}.pdf`),
    printBackground: true,
    preferCSSPageSize: true,
    landscape: quer,
  });
  await seite.close();
  console.log('geschrieben:', `lernkarten/ausgabe/${name}.pdf`);
}

async function main() {
  mkdirSync(AUSGABE, { recursive: true });
  const nurPassprobe = process.argv[2] === 'passprobe';

  const browser = await chromium.launch(CHROMIUM ? { executablePath: CHROMIUM } : {});
  try {
    await schreibe(browser, passprobeBogen(), 'passprobe', false);

    if (!nurPassprobe) {
      const liste = JSON.parse(readFileSync(join(HIER, 'karten.json'), 'utf8'));
      const karten = liste.karten.map((k) => ({
        ...k,
        bildDaten: k.bild ? alsDatenAdresse(k.bild) : null,
      }));
      if (karten.length) {
        await schreibe(browser, kartenBogen(karten), 'karten', true);
      } else {
        console.log('karten.json enthaelt keine Karten - nichts zu bauen.');
      }
    }
  } finally {
    await browser.close();
  }
}

main().catch((e) => { console.error(e); process.exit(1); });

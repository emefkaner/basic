// Lynkeus — Gemini/Veo-Wasserzeichen aus Videos und Fotos herausrechnen.
// Läuft vollständig im Browser (WebCodecs über mediabunny); nichts wird hochgeladen.

import {
  ALL_FORMATS, BlobSource, BufferTarget, CanvasSource,
  EncodedAudioPacketSource, EncodedPacketSink, Input,
  Mp4OutputFormat, WebMOutputFormat, Output, QUALITY_HIGH,
  VideoSampleSink, canEncodeVideo,
} from 'mediabunny';
import {
  standardWerte, fotoStandardWerte, veoBox, fotoBox, boxAufloesen, ausschnitt,
  alphaBauen, wasserzeichenEntfernen, bildSaeubern, luminanzAus, sternSuchen,
} from './engine.js';

const $ = (id) => document.getElementById(id);
const de = (zahl, stellen = 2) => zahl.toFixed(stellen).replace('.', ',').replace('-', '−');

let vorlage96 = null;      // Funkel-Referenz 96 px (Videos und große Fotos)
let vorlage48 = null;      // Funkel-Referenz 48 px (kleine Fotos)
let modus = 'video';       // 'video' | 'foto'
let datei = null;
let input = null;          // mediabunny-Input fürs Vorschaubild (nur Video)
let sink = null;
let breite = 0, hoehe = 0, dauer = 0;
let werte = { staerke: 0.6, versatzX: -24, versatzY: -24, groesse: 1 };
let originalPx = null;     // ungesäubertes Vorschaubild (ImageData)
let originalZeigen = false;
let laeuft = false;
let ergebnisUrl = null;

// Grundgeometrie und Vorlage je Modus.
const basisFn = () => (modus === 'foto' ? fotoBox : veoBox);
function aktuelleVorlage() {
  if (modus === 'foto' && fotoBox(breite, hoehe).size === 48) return vorlage48;
  return vorlage96;
}

// ---------- Start ----------

const bildLaden = (src) => new Promise((res, rej) => {
  const i = new Image();
  i.onload = () => res(i);
  i.onerror = () => rej(new Error('Eine eingebettete Vorlage ließ sich nicht laden.'));
  i.src = src;
});

async function start() {
  [vorlage96, vorlage48] = await Promise.all([
    bildLaden(window.BG96_DATENURI),
    bildLaden(window.BG48_DATENURI),
  ]);

  // (Das Favicon steckt als PNG-Daten-URI fest im <head> — nichts zu tun.)

  // Das Regenbogenband dreht per Skript (ein voller Umlauf ≈ 5 s) — so
  // bewegt es sich in jedem Browser, unabhängig von CSS-Eigenheiten.
  requestAnimationFrame(function drehen(t) {
    document.documentElement.style.setProperty('--winkel', ((t / 14) % 360).toFixed(1) + 'deg');
    requestAnimationFrame(drehen);
  });

  $('modusVideo').addEventListener('click', () => modusSetzen('video'));
  $('modusFoto').addEventListener('click', () => modusSetzen('foto'));

  const ablage = $('ablage');
  const wahl = $('dateiwahl');
  ablage.addEventListener('click', () => wahl.click());
  wahl.addEventListener('change', () => { if (wahl.files[0]) dateiNehmen(wahl.files[0]); });
  ablage.addEventListener('dragover', (e) => { e.preventDefault(); ablage.classList.add('aktiv'); });
  ablage.addEventListener('dragleave', () => ablage.classList.remove('aktiv'));
  ablage.addEventListener('drop', (e) => {
    e.preventDefault(); ablage.classList.remove('aktiv');
    const f = e.dataTransfer.files && e.dataTransfer.files[0];
    if (f) dateiNehmen(f);
  });

  for (const [id, schluessel] of [['staerke', 'staerke'], ['vx', 'versatzX'], ['vy', 'versatzY'], ['groesse', 'groesse']]) {
    $(id).addEventListener('input', () => {
      werte[schluessel] = parseFloat($(id).value);
      reglerAnzeigen();
      vorschauZeichnen();
    });
  }
  $('zeit').addEventListener('change', () => vorschauLaden());
  $('zeit').addEventListener('input', () => { $('zeitwert').textContent = de(parseFloat($('zeit').value), 1) + ' s'; });
  $('rahmen').addEventListener('change', () => vorschauZeichnen());
  $('standard').addEventListener('click', () => {
    werte = modus === 'foto' ? fotoStandardWerte() : standardWerte(breite, hoehe);
    reglerSetzen();
    vorschauZeichnen();
  });
  const vgl = $('vergleich');
  const an = (e) => { e.preventDefault(); originalZeigen = true; vorschauZeichnen(); };
  const aus = () => { if (originalZeigen) { originalZeigen = false; vorschauZeichnen(); } };
  vgl.addEventListener('pointerdown', an);
  vgl.addEventListener('pointerup', aus);
  vgl.addEventListener('pointerleave', aus);

  $('suchen').addEventListener('click', () => sternAutomatisch(true).catch((e) => {
    $('suchergebnis').textContent = 'Suche fehlgeschlagen: ' + (e && e.message ? e.message : e);
  }));

  $('los').addEventListener('click', () => {
    const arbeit = modus === 'foto' ? fotoExport() : videoUmwandeln();
    arbeit.catch((e) => {
      laeuft = false;
      $('los').disabled = false;
      $('status').className = 'hinweis fehler';
      $('status').textContent = 'Fehlgeschlagen: ' + (e && e.message ? e.message : e);
    });
  });
}

function modusSetzen(neu) {
  if (laeuft || modus === neu) return;
  modus = neu;
  $('modusVideo').classList.toggle('aktivmodus', neu === 'video');
  $('modusFoto').classList.toggle('aktivmodus', neu === 'foto');
  $('dateiwahl').accept = neu === 'foto' ? 'image/*' : 'video/*';
  $('dateiwahl').value = '';
  $('ablagetitel').textContent = neu === 'foto' ? 'Foto hierher ziehen' : 'Video hierher ziehen';
  $('ablagehinweis').textContent = neu === 'foto'
    ? 'PNG/JPG aus Gemini · Verarbeitung komplett lokal'
    : 'MP4 aus der Gemini-App / Veo · Verarbeitung komplett lokal';
  // Angefangenes zurücksetzen
  datei = null; originalPx = null; sink = null;
  $('pruefkarte').classList.add('versteckt');
  $('wandelkarte').classList.add('versteckt');
}

// ---------- Datei laden & Vorschau ----------

function reglerSetzen() {
  $('staerke').value = werte.staerke;
  $('vx').value = werte.versatzX;
  $('vy').value = werte.versatzY;
  $('groesse').value = werte.groesse;
  reglerAnzeigen();
}

function reglerAnzeigen() {
  $('staerkewert').textContent = de(werte.staerke);
  $('vxwert').textContent = de(werte.versatzX, 0);
  $('vywert').textContent = de(werte.versatzY, 0);
  $('groessewert').textContent = de(werte.groesse);
}

function anzeigeVorbereiten(f) {
  datei = f;
  $('videoinfo').textContent = 'Datei wird gelesen …';
  $('videoinfo').className = 'hinweis';
  $('pruefkarte').classList.remove('versteckt');
  $('wandelkarte').classList.add('versteckt');
  $('ergebnis').classList.add('versteckt');
  $('status').textContent = '';
  if (ergebnisUrl) { URL.revokeObjectURL(ergebnisUrl); ergebnisUrl = null; }
}

async function dateiNehmen(f) {
  if (laeuft) return;
  // Passt die Datei nicht zum gewählten Modus, freundlich umschalten.
  if (f.type.startsWith('image/') && modus !== 'foto') modusSetzen('foto');
  else if (f.type.startsWith('video/') && modus !== 'video') modusSetzen('video');
  return modus === 'foto' ? fotoNehmen(f) : videoNehmen(f);
}

async function videoNehmen(f) {
  anzeigeVorbereiten(f);
  try {
    if (input) { try { input.dispose?.(); } catch {} }
    input = new Input({ source: new BlobSource(f), formats: ALL_FORMATS });
    const spur = await input.getPrimaryVideoTrack();
    if (!spur) throw new Error('In dieser Datei steckt keine lesbare Videospur.');
    if (!(await spur.canDecode())) {
      throw new Error('Dieser Browser kann das Video nicht dekodieren (Codec fehlt). Bitte Chrome oder Edge am Rechner verwenden.');
    }
    breite = spur.displayWidth ?? spur.codedWidth;
    hoehe = spur.displayHeight ?? spur.codedHeight;
    dauer = await input.computeDuration().catch(() => 0);
    sink = new VideoSampleSink(spur);

    werte = standardWerte(breite, hoehe);
    reglerSetzen();

    $('zeitzeile').classList.remove('versteckt');
    const zeit = $('zeit');
    zeit.max = Math.max(0.1, (dauer || 1) - 0.05).toFixed(1);
    zeit.value = Math.min(1, (dauer || 2) / 2).toFixed(1);
    $('zeitwert').textContent = de(parseFloat(zeit.value), 1) + ' s';

    $('videoinfo').textContent = `${f.name} · ${breite}×${hoehe} Pixel · ${de(dauer, 1)} s`;

    const leinwand = $('leinwand');
    leinwand.width = breite;
    leinwand.height = hoehe;

    await vorschauLaden();
    $('wandelkarte').classList.remove('versteckt');
    $('wandelhinweis').textContent = '';
    $('los').disabled = false;
    await sternAutomatisch(false).catch(() => {});
  } catch (e) {
    $('videoinfo').className = 'hinweis fehler';
    $('videoinfo').textContent = (e && e.message) ? e.message : String(e);
  }
}

async function fotoNehmen(f) {
  anzeigeVorbereiten(f);
  try {
    const url = URL.createObjectURL(f);
    let bild;
    try {
      bild = await bildLaden(url);
    } catch {
      throw new Error('Dieses Bild ließ sich nicht öffnen (kein PNG/JPG?).');
    } finally {
      setTimeout(() => URL.revokeObjectURL(url), 5000);
    }
    breite = bild.naturalWidth;
    hoehe = bild.naturalHeight;
    sink = null;

    werte = fotoStandardWerte();
    reglerSetzen();
    $('zeitzeile').classList.add('versteckt');

    $('videoinfo').textContent =
      `${f.name} · ${breite}×${hoehe} Pixel · Sterngröße ${fotoBox(breite, hoehe).size} px (automatisch)`;

    const leinwand = $('leinwand');
    leinwand.width = breite;
    leinwand.height = hoehe;
    const c = document.createElement('canvas');
    c.width = breite; c.height = hoehe;
    const cx = c.getContext('2d', { willReadFrequently: true });
    cx.drawImage(bild, 0, 0);
    originalPx = cx.getImageData(0, 0, breite, hoehe);

    vorschauZeichnen();
    $('wandelkarte').classList.remove('versteckt');
    $('wandelhinweis').textContent = 'Ausgabe als PNG (verlustfrei).';
    $('los').disabled = false;
    await sternAutomatisch(false).catch(() => {});
  } catch (e) {
    $('videoinfo').className = 'hinweis fehler';
    $('videoinfo').textContent = (e && e.message) ? e.message : String(e);
  }
}

async function vorschauLaden() {
  if (!sink) return;
  const t = parseFloat($('zeit').value);
  const probe = await sink.getSample(t);
  if (!probe) return;
  const c = document.createElement('canvas');
  c.width = breite; c.height = hoehe;
  const cx = c.getContext('2d', { willReadFrequently: true });
  probe.draw(cx, 0, 0, breite, hoehe);
  probe.close();
  originalPx = cx.getImageData(0, 0, breite, hoehe);
  vorschauZeichnen();
}

function vorschauZeichnen() {
  if (!originalPx) return;
  const ctx = $('leinwand').getContext('2d');
  const kopie = new ImageData(new Uint8ClampedArray(originalPx.data), breite, hoehe);
  let box = boxAufloesen(basisFn()(breite, hoehe), breite, hoehe, werte);
  if (!originalZeigen) ({ box } = bildSaeubern(aktuelleVorlage(), kopie, werte, basisFn()));
  ctx.putImageData(kopie, 0, 0);
  if ($('rahmen').checked) {
    ctx.strokeStyle = originalZeigen ? 'rgba(150,170,200,.9)' : 'rgba(240,177,62,.95)';
    ctx.lineWidth = Math.max(1, Math.round(breite / 640));
    ctx.strokeRect(box.x + .5, box.y + .5, box.size, box.size);
  }
}

// ---------- Automatische Sternsuche ----------

// Bei Videos: Helligkeit über mehrere Bilder mitteln. Der Stern steht still,
// der Inhalt bewegt sich — im Mittel tritt der Stern deutlich hervor.
async function videoMittelLuminanz() {
  const zeiten = dauer > 0.5
    ? [0.15, 0.3, 0.45, 0.6, 0.75, 0.9].map((a) => a * dauer)
    : [parseFloat($('zeit').value)];
  const c = document.createElement('canvas');
  c.width = breite; c.height = hoehe;
  const cx = c.getContext('2d', { willReadFrequently: true });
  const summe = new Float32Array(breite * hoehe);
  let anzahl = 0;
  for (const t of zeiten) {
    const probe = await sink.getSample(t).catch(() => null);
    if (!probe) continue;
    probe.draw(cx, 0, 0, breite, hoehe);
    probe.close();
    const grau = luminanzAus(cx.getImageData(0, 0, breite, hoehe));
    for (let i = 0; i < summe.length; i++) summe[i] += grau[i];
    anzahl++;
  }
  if (!anzahl) return luminanzAus(originalPx);
  for (let i = 0; i < summe.length; i++) summe[i] /= anzahl;
  return summe;
}

// Regler-Grenzen so weiten, dass der gefundene Wert hineinpasst.
function reglerWeiten(id, wert) {
  const r = $(id);
  if (wert < parseFloat(r.min)) r.min = Math.floor(wert / 10) * 10;
  if (wert > parseFloat(r.max)) r.max = Math.ceil(wert / 10) * 10;
}

async function sternAutomatisch(vonHand) {
  if (!originalPx || laeuft) return;
  $('suchergebnis').textContent = '🔍 Stern wird gesucht …';
  $('los').disabled = true; // nicht mitten in der Suche mit alten Werten starten
  await new Promise((r) => setTimeout(r, 30)); // Text erst zeichnen lassen

  let fund;
  try {
    const basis = basisFn()(breite, hoehe);
    const grau = modus === 'video' && sink ? await videoMittelLuminanz() : luminanzAus(originalPx);
    fund = sternSuchen(grau, breite, hoehe, aktuelleVorlage(), basis);
  } finally {
    $('los').disabled = false;
  }
  const basis = basisFn()(breite, hoehe);

  const schwelle = vonHand ? 0.4 : 0.55;
  if (!fund || fund.guete < schwelle) {
    $('suchergebnis').textContent = fund
      ? `Kein eindeutiger Stern gefunden (Treffergüte ${de(fund.guete)}) — die Werte bleiben, wie sie sind.`
      : 'Kein Stern gefunden — die Werte bleiben, wie sie sind.';
    return;
  }

  const standard = modus === 'foto' ? fotoStandardWerte() : standardWerte(breite, hoehe);
  const anStandard =
    Math.abs((fund.x - basis.x) - standard.versatzX) <= 3 &&
    Math.abs((fund.y - basis.y) - standard.versatzY) <= 3 &&
    Math.abs(fund.size / basis.size - 1) <= 0.06;

  if (anStandard) {
    // Google hat nichts verändert: die bewährten Standardwerte sind genauer
    // als jede Einzelmessung — dabei bleiben.
    werte = { ...standard };
  } else {
    werte.versatzX = fund.x - basis.x;
    werte.versatzY = fund.y - basis.y;
    werte.groesse = Math.round((fund.size / basis.size) * 100) / 100;
    if (fund.staerke != null) werte.staerke = Math.round(fund.staerke * 20) / 20;
    reglerWeiten('vx', werte.versatzX);
    reglerWeiten('vy', werte.versatzY);
  }
  reglerSetzen();
  vorschauZeichnen();

  $('suchergebnis').textContent = anStandard
    ? `✓ Stern an der erwarteten Standardposition bestätigt (Treffergüte ${de(fund.guete)}).`
    : `✓ Stern gefunden bei ${fund.x}/${fund.y}, Größe ${fund.size} px — Regler übernommen (Treffergüte ${de(fund.guete)}).`;
}

// ---------- Foto: herausrechnen und als PNG speichern ----------

async function fotoExport() {
  if (!originalPx || laeuft) return;
  laeuft = true;
  $('los').disabled = true;
  $('status').className = 'hinweis';
  $('status').textContent = 'Wird herausgerechnet …';

  try {
    const c = document.createElement('canvas');
    c.width = breite; c.height = hoehe;
    const cx = c.getContext('2d', { willReadFrequently: true });
    const kopie = new ImageData(new Uint8ClampedArray(originalPx.data), breite, hoehe);
    bildSaeubern(aktuelleVorlage(), kopie, werte, basisFn());
    cx.putImageData(kopie, 0, 0);

    const blob = await new Promise((res, rej) =>
      c.toBlob((b) => (b ? res(b) : rej(new Error('PNG konnte nicht erzeugt werden.'))), 'image/png'));
    ergebnisUrl = URL.createObjectURL(blob);
    const basisname = datei.name.replace(/\.[^.]+$/, '') || 'foto';
    const a = $('herunterladen');
    a.href = ergebnisUrl;
    a.download = `${basisname} – ohne Wasserzeichen.png`;
    $('ergebnisbild').src = ergebnisUrl;
    $('ergebnisbild').classList.remove('versteckt');
    $('ergebnisvideo').classList.add('versteckt');
    $('ergebnisvideo').removeAttribute('src');
    $('fertigtext').textContent = `Fertig — ${de(blob.size / (1024 * 1024), 1)} MB, ${breite}×${hoehe}, PNG.`;
    $('status').textContent = '';
    $('ergebnis').classList.remove('versteckt');
  } finally {
    laeuft = false;
    $('los').disabled = false;
  }
}

// ---------- Video: Bild für Bild umwandeln ----------

async function videoUmwandeln() {
  if (!datei || laeuft) return;
  laeuft = true;
  $('los').disabled = true;
  $('ergebnis').classList.add('versteckt');
  $('balkenhuelle').classList.remove('versteckt');
  $('balken').style.width = '0%';
  $('status').className = 'hinweis';
  $('status').textContent = 'Wird umgerechnet … (das Video wird Bild für Bild neu aufgebaut)';

  const hinweise = [];

  // Ausgabeformat: H.264/MP4, sonst VP9/WebM als Ausweg.
  let videoCodec = 'avc';
  let format = new Mp4OutputFormat();
  let endung = 'mp4', mime = 'video/mp4';
  if (!(await canEncodeVideo('avc', { width: breite, height: hoehe }))) {
    if (await canEncodeVideo('vp9', { width: breite, height: hoehe })) {
      videoCodec = 'vp9'; format = new WebMOutputFormat();
      endung = 'webm'; mime = 'video/webm';
      hinweise.push('Dieser Browser kodiert kein H.264 — Ausgabe als WebM (VP9).');
    } else {
      throw new Error('Dieser Browser kann Videos nicht lokal kodieren. Bitte aktuelles Chrome oder Edge am Rechner verwenden.');
    }
  }

  const quelle = new Input({ source: new BlobSource(datei), formats: ALL_FORMATS });
  try {
    const spur = await quelle.getPrimaryVideoTrack();
    if (!spur) throw new Error('Keine Videospur gefunden.');
    const dauerJetzt = await quelle.computeDuration().catch(() => 0);

    let bildrate = 30;
    try {
      const statistik = await spur.computePacketStats(120);
      if (statistik?.averagePacketRate) bildrate = Math.round(statistik.averagePacketRate);
    } catch { /* 30 bleibt */ }

    // Alphamaske einmal bauen; sie gilt für jedes Bild.
    const box = boxAufloesen(veoBox(breite, hoehe), breite, hoehe, werte);
    const roi = ausschnitt(breite, hoehe, box);
    const karte = alphaBauen(vorlage96, roi, box, werte.staerke);

    const leinwand = typeof OffscreenCanvas !== 'undefined'
      ? new OffscreenCanvas(breite, hoehe)
      : Object.assign(document.createElement('canvas'), { width: breite, height: hoehe });
    const ctx = leinwand.getContext('2d', { willReadFrequently: true });

    const ziel = new BufferTarget();
    const ausgabe = new Output({ format, target: ziel });
    const videoQuelle = new CanvasSource(leinwand, {
      codec: videoCodec,
      bitrate: QUALITY_HIGH,
      keyFrameInterval: 2,
      sizeChangeBehavior: 'passThrough',
    });
    ausgabe.addVideoTrack(videoQuelle, { frameRate: bildrate });

    // Tonspur unverändert durchreichen (bestmöglich, ohne Neukodierung).
    let tonQuelle = null, tonSpur = null, tonKonfig = null;
    try {
      tonSpur = await quelle.getPrimaryAudioTrack();
      if (tonSpur) {
        const tonCodec = await tonSpur.getCodec();
        tonKonfig = await tonSpur.getDecoderConfig().catch(() => null);
        if (tonCodec && tonKonfig) {
          tonQuelle = new EncodedAudioPacketSource(tonCodec);
          ausgabe.addAudioTrack(tonQuelle);
        }
      }
    } catch {
      tonQuelle = null;
      hinweise.push('Die Tonspur passt nicht in das Ausgabeformat — das Ergebnis ist ohne Ton.');
    }

    await ausgabe.start();

    const rueckfallDauer = bildrate > 0 ? 1 / bildrate : 1 / 30;
    const proben = new VideoSampleSink(spur);
    let ersterStempel = null;
    let letzterStempel = -1;
    for await (const probe of proben.samples()) {
      if (ersterStempel === null) ersterStempel = probe.timestamp;
      let stempel = probe.timestamp - ersterStempel;
      if (!(stempel >= 0)) stempel = 0;
      if (stempel <= letzterStempel) stempel = letzterStempel + rueckfallDauer;
      const bilddauer = Number.isFinite(probe.duration) && probe.duration > 0 ? probe.duration : rueckfallDauer;
      letzterStempel = stempel;

      probe.draw(ctx, 0, 0, breite, hoehe);
      probe.close();

      const px = ctx.getImageData(roi.x, roi.y, roi.breite, roi.hoehe);
      wasserzeichenEntfernen(px, karte, { x: 0, y: 0, breite: roi.breite, hoehe: roi.hoehe });
      ctx.putImageData(px, roi.x, roi.y);

      await videoQuelle.add(stempel, bilddauer);
      if (dauerJetzt) $('balken').style.width = Math.min(99, Math.round((stempel / dauerJetzt) * 100)) + '%';
    }
    videoQuelle.close();

    if (tonQuelle) {
      try {
        const versatz = ersterStempel ?? 0;
        const pakete = new EncodedPacketSink(tonSpur);
        let erstesPaket = true;
        let letzterTon = -1;
        for await (const paket of pakete.packets()) {
          let neu = paket.timestamp - versatz;
          if (neu < 0) continue;
          if (neu <= letzterTon) neu = letzterTon + 1e-6;
          letzterTon = neu;
          let ausPaket = paket;
          if (neu !== paket.timestamp && typeof paket.clone === 'function') {
            ausPaket = paket.clone({ timestamp: neu });
          }
          await tonQuelle.add(ausPaket, erstesPaket && tonKonfig ? { decoderConfig: tonKonfig } : undefined);
          erstesPaket = false;
        }
      } catch (e) {
        console.warn('Ton konnte nicht übernommen werden:', e);
        hinweise.push('Die Tonspur ließ sich nicht übernehmen — das Ergebnis ist ohne Ton.');
      } finally {
        tonQuelle.close();
      }
    }

    await ausgabe.finalize();
    if (!ziel.buffer) throw new Error('Die Umwandlung lieferte keine Daten.');

    const blob = new Blob([ziel.buffer], { type: mime });
    ergebnisUrl = URL.createObjectURL(blob);
    const basisname = datei.name.replace(/\.[^.]+$/, '') || 'video';
    const a = $('herunterladen');
    a.href = ergebnisUrl;
    a.download = `${basisname} – ohne Wasserzeichen.${endung}`;
    $('ergebnisvideo').src = ergebnisUrl;
    $('ergebnisvideo').classList.remove('versteckt');
    $('ergebnisbild').classList.add('versteckt');
    $('ergebnisbild').removeAttribute('src');
    $('balken').style.width = '100%';
    $('fertigtext').textContent = `Fertig — ${de(blob.size / (1024 * 1024), 1)} MB, ${breite}×${hoehe}.`;
    $('status').className = hinweise.length ? 'hinweis warnung' : 'hinweis';
    $('status').textContent = hinweise.join(' ');
    $('ergebnis').classList.remove('versteckt');
  } finally {
    try { quelle.dispose?.(); } catch {}
    laeuft = false;
    $('los').disabled = false;
  }
}

start().catch((e) => {
  document.body.insertAdjacentHTML('beforeend',
    `<p class="fehler" style="max-width:880px;margin:0 auto">Startfehler: ${e && e.message ? e.message : e}</p>`);
});

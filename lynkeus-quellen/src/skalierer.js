// GPU-Hochskalierung mit Detailschärfung (WebGL2, zwei Durchgänge):
//   1. Catmull-Rom-Rekonstruktion (bikubisch, 9 optimierte Abtastungen)
//   2. kontrastadaptive Nachschärfung (nach AMDs CAS-Verfahren)
// Bewusst KEIN generatives KI-Modell: das würde zig MB Gewichte und
// Sekunden je Einzelbild kosten — für eine Offline-Single-File untauglich.
// Dieses Verfahren erhält Kanten/Details deutlich besser als einfaches
// Skalieren und läuft in Echtzeit auf der Grafikkarte.

const SCHEITEL = `#version 300 es
out vec2 uv;
void main() {
  vec2 ecken[3] = vec2[3](vec2(-1.0,-1.0), vec2(3.0,-1.0), vec2(-1.0,3.0));
  gl_Position = vec4(ecken[gl_VertexID], 0.0, 1.0);
  uv = gl_Position.xy * 0.5 + 0.5;
}`;

// Catmull-Rom mit 9 bilinear optimierten Abtastungen (Standardverfahren)
const FRAG_SKALIEREN = `#version 300 es
precision highp float;
uniform sampler2D quelle;
uniform vec2 quellGroesse;
in vec2 uv;
out vec4 farbe;
void main() {
  vec2 pos = uv * quellGroesse - 0.5;
  vec2 basis = floor(pos);
  vec2 f = pos - basis;

  vec2 w0 = f * (-0.5 + f * (1.0 - 0.5 * f));
  vec2 w1 = 1.0 + f * f * (-2.5 + 1.5 * f);
  vec2 w2 = f * (0.5 + f * (2.0 - 1.5 * f));
  vec2 w3 = f * f * (-0.5 + 0.5 * f);

  vec2 w12 = w1 + w2;
  vec2 t0 = (basis - 0.5) / quellGroesse;
  vec2 t3 = (basis + 2.5) / quellGroesse;
  vec2 t12 = (basis + 0.5 + w2 / w12) / quellGroesse;

  vec4 summe =
      texture(quelle, vec2(t0.x,  t0.y))  * (w0.x  * w0.y) +
      texture(quelle, vec2(t12.x, t0.y))  * (w12.x * w0.y) +
      texture(quelle, vec2(t3.x,  t0.y))  * (w3.x  * w0.y) +
      texture(quelle, vec2(t0.x,  t12.y)) * (w0.x  * w12.y) +
      texture(quelle, vec2(t12.x, t12.y)) * (w12.x * w12.y) +
      texture(quelle, vec2(t3.x,  t12.y)) * (w3.x  * w12.y) +
      texture(quelle, vec2(t0.x,  t3.y))  * (w0.x  * w3.y) +
      texture(quelle, vec2(t12.x, t3.y))  * (w12.x * w3.y) +
      texture(quelle, vec2(t3.x,  t3.y))  * (w3.x  * w3.y);
  farbe = vec4(clamp(summe.rgb, 0.0, 1.0), 1.0);
}`;

// Kontrastadaptive Schärfung: kräftigt Kanten, lässt flache Flächen in Ruhe
const FRAG_SCHAERFEN = `#version 300 es
precision highp float;
uniform sampler2D quelle;
uniform vec2 zielGroesse;
uniform float staerke; // 0..1
in vec2 uv;
out vec4 farbe;
void main() {
  vec2 t = 1.0 / zielGroesse;
  vec3 m = texture(quelle, uv).rgb;
  vec3 n = texture(quelle, uv + vec2(0.0, -t.y)).rgb;
  vec3 s = texture(quelle, uv + vec2(0.0,  t.y)).rgb;
  vec3 w = texture(quelle, uv + vec2(-t.x, 0.0)).rgb;
  vec3 e = texture(quelle, uv + vec2( t.x, 0.0)).rgb;

  vec3 mn = min(min(min(n, s), min(w, e)), m);
  vec3 mx = max(max(max(n, s), max(w, e)), m);
  vec3 amp = clamp(min(mn, 1.0 - mx) / max(mx, vec3(1e-4)), 0.0, 1.0);
  float spitze = -1.0 / mix(8.0, 5.0, clamp(staerke, 0.0, 1.0));
  vec3 g = sqrt(amp) * spitze;
  vec3 aus = (m + g * (n + s + w + e)) / (1.0 + 4.0 * g);
  farbe = vec4(clamp(aus, 0.0, 1.0), 1.0);
}`;

function programm(gl, fragQuelle) {
  const bauen = (typ, quelle) => {
    const s = gl.createShader(typ);
    gl.shaderSource(s, quelle);
    gl.compileShader(s);
    if (!gl.getShaderParameter(s, gl.COMPILE_STATUS)) {
      throw new Error('Shader-Fehler: ' + gl.getShaderInfoLog(s));
    }
    return s;
  };
  const p = gl.createProgram();
  gl.attachShader(p, bauen(gl.VERTEX_SHADER, SCHEITEL));
  gl.attachShader(p, bauen(gl.FRAGMENT_SHADER, fragQuelle));
  gl.linkProgram(p);
  if (!gl.getProgramParameter(p, gl.LINK_STATUS)) {
    throw new Error('Programm-Fehler: ' + gl.getProgramInfoLog(p));
  }
  return p;
}

export class Hochskalierer {
  constructor(quellB, quellH, zielB, zielH, schaerfe = 0.4) {
    this.quellB = quellB; this.quellH = quellH;
    this.zielB = zielB; this.zielH = zielH;

    this.leinwand = typeof OffscreenCanvas !== 'undefined'
      ? new OffscreenCanvas(zielB, zielH)
      : Object.assign(document.createElement('canvas'), { width: zielB, height: zielH });
    const gl = this.leinwand.getContext('webgl2', {
      preserveDrawingBuffer: true, // mediabunny liest die Leinwand nach dem Zeichnen
      antialias: false, depth: false, stencil: false,
    });
    if (!gl) throw new Error('WebGL2 ist in diesem Browser nicht verfügbar — Hochskalierung geht hier nicht.');
    this.gl = gl;
    this.schaerfe = schaerfe;

    this.pSkalieren = programm(gl, FRAG_SKALIEREN);
    this.pSchaerfen = programm(gl, FRAG_SCHAERFEN);

    // Quelltextur (wird je Bild neu befüllt)
    this.texQuelle = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.texQuelle);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);

    // Zwischenbild in Zielgröße für den Schärfungs-Durchgang
    this.texZwischen = gl.createTexture();
    gl.bindTexture(gl.TEXTURE_2D, this.texZwischen);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, zielB, zielH, 0, gl.RGBA, gl.UNSIGNED_BYTE, null);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.LINEAR);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
    gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
    this.fbo = gl.createFramebuffer();
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fbo);
    gl.framebufferTexture2D(gl.FRAMEBUFFER, gl.COLOR_ATTACHMENT0, gl.TEXTURE_2D, this.texZwischen, 0);
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
  }

  // Nimmt die 2D-Leinwand mit dem gesäuberten Bild und zeichnet die
  // hochskalierte, nachgeschärfte Fassung auf die eigene WebGL-Leinwand.
  ziehe(quellLeinwand) {
    const gl = this.gl;

    gl.bindTexture(gl.TEXTURE_2D, this.texQuelle);
    gl.pixelStorei(gl.UNPACK_FLIP_Y_WEBGL, true);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA8, gl.RGBA, gl.UNSIGNED_BYTE, quellLeinwand);

    // Durchgang 1: hochrechnen in die Zwischentextur
    gl.bindFramebuffer(gl.FRAMEBUFFER, this.fbo);
    gl.viewport(0, 0, this.zielB, this.zielH);
    gl.useProgram(this.pSkalieren);
    gl.uniform1i(gl.getUniformLocation(this.pSkalieren, 'quelle'), 0);
    gl.uniform2f(gl.getUniformLocation(this.pSkalieren, 'quellGroesse'), this.quellB, this.quellH);
    gl.activeTexture(gl.TEXTURE0);
    gl.bindTexture(gl.TEXTURE_2D, this.texQuelle);
    gl.drawArrays(gl.TRIANGLES, 0, 3);

    // Durchgang 2: nachschärfen auf die sichtbare Leinwand
    gl.bindFramebuffer(gl.FRAMEBUFFER, null);
    gl.viewport(0, 0, this.zielB, this.zielH);
    gl.useProgram(this.pSchaerfen);
    gl.uniform1i(gl.getUniformLocation(this.pSchaerfen, 'quelle'), 0);
    gl.uniform2f(gl.getUniformLocation(this.pSchaerfen, 'zielGroesse'), this.zielB, this.zielH);
    gl.uniform1f(gl.getUniformLocation(this.pSchaerfen, 'staerke'), this.schaerfe);
    gl.bindTexture(gl.TEXTURE_2D, this.texZwischen);
    gl.drawArrays(gl.TRIANGLES, 0, 3);

    return this.leinwand;
  }
}

// Wählbare Zielauflösungen für eine Quelle: nur echte Vergrößerungen,
// Maße immer gerade (Vorgabe der Videokodierer).
export function zielAufloesungen(breite, hoehe) {
  const kurz = Math.min(breite, hoehe);
  const gerade = (x) => Math.round(x / 2) * 2;
  const ziele = [
    { name: 'Full HD', kurzSeite: 1080 },
    { name: 'QHD', kurzSeite: 1440 },
    { name: '4K', kurzSeite: 2160 },
  ];
  const aus = [{ name: 'Original', breite, hoehe, faktor: 1 }];
  for (const z of ziele) {
    if (z.kurzSeite <= kurz) continue;
    const faktor = z.kurzSeite / kurz;
    aus.push({
      name: z.name,
      breite: gerade(breite * faktor),
      hoehe: gerade(hoehe * faktor),
      faktor: Math.round(faktor * 100) / 100,
    });
  }
  return aus;
}

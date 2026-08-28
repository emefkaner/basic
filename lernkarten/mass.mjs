// Maße des lupilu LCD Schreibpads mit Lernkarten (IAN 513251_2501).
//
// Quellen:
// - Gebrauchsanweisung Delta-Sport, IAN 513251_2501: Artikel gesamt
//   ca. 220 x 156 x 15 mm (L x B x H), Display 8,5".
// - Haendlerangaben (discounto.de / preisrunter.de) zur Kartengroesse:
//   ca. 193 x 123 mm (L x B).
//
// ACHTUNG: Die Kartengroesse stammt aus dem Haendlertext, NICHT aus der
// Gebrauchsanweisung. Vor dem Drucken einer ganzen Serie einmal mit
// "passprobe" gegen eine echte Karte pruefen und die Werte hier notfalls
// korrigieren.

export const KARTE = {
  breite: 123,   // mm
  hoehe: 193,    // mm
};

// Die Karte steckt laut Abbildung A der Anleitung in einer Tasche auf der
// linken Innenseite und wird von oben eingeschoben. Die Tasche hat oben eine
// bogenfoermige Kante mit Daumenausschnitt - dort verschwindet ein Streifen
// der Karte hinter dem Material. Deshalb oben deutlich mehr Rand lassen.
export const SICHER = {
  oben: 20,      // mm - Bereich hinter der Taschenkante
  unten: 10,     // mm
  links: 10,     // mm
  rechts: 10,    // mm
};

// Bogen: A4 quer, zwei Karten nebeneinander.
export const BOGEN = {
  breite: 297,
  hoehe: 210,
  spalt: 6,      // mm zwischen den beiden Karten
};

export const BOGEN_HOCH = { breite: 210, hoehe: 297 };

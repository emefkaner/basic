// Variante B: Deckel mit Zapfen (top-hat) fuer das verkuerzte Piraten-Fernrohr
// -> passend, wenn 70 mm der Aussenrand und 25 mm die mittige Oeffnung ist.
// Masse aendern, dann F6 (Render) und als STL exportieren.

lid_d     = 70;    // Aussendurchmesser des Deckels
lid_th    = 3;     // Dicke des Deckels
hole_d    = 25;    // Durchmesser der Oeffnung/Bohrung
clearance = 0.4;   // Spiel (zu stramm? groesser. zu locker? kleiner)
plug_len  = 16;    // Laenge des Zapfens
chamfer   = 1.5;   // Einfuehr-Fase am Zapfen

$fn = 200;

plug_d = hole_d - clearance;

union() {
    // Zapfen mit Einfuehr-Fase unten
    cylinder(d1 = plug_d - 2*chamfer, d2 = plug_d, h = chamfer);
    translate([0,0,chamfer])
        cylinder(d = plug_d, h = plug_len - chamfer);
    // Deckel oben
    translate([0,0,plug_len])
        cylinder(d = lid_d, h = lid_th);
}

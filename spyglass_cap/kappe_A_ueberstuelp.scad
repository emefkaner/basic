// Variante A: Ueberstuelp-Kappe fuer das verkuerzte Piraten-Fernrohr
// -> passend, wenn 70 mm der AUSSENdurchmesser des Rohrs ist.
// Masse aendern, dann F6 (Render) und als STL exportieren.

tube_outer_d = 70;   // gemessener Aussendurchmesser des Rohrs
clearance    = 0.4;  // Spiel (zu stramm? groesser. zu locker? kleiner)
wall         = 3;    // Wandstaerke der Kappe
skirt_h      = 20;   // wie weit die Kappe ueber das Rohr greift
top_th       = 3;    // Dicke des geschlossenen Deckels

$fn = 200;

inner_d = tube_outer_d + clearance;
outer_d = inner_d + 2*wall;

difference() {
    cylinder(d = outer_d, h = skirt_h + top_th);           // Vollzylinder
    translate([0,0,-0.01])
        cylinder(d = inner_d, h = skirt_h + 0.01);         // Bohrung fuers Rohr
}

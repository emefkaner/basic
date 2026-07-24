// Variante C: HALTERING mit Guckloch fuer das verkuerzte Piraten-Fernrohr.
// Kein geschlossener Deckel: haelt die ausfahrbaren Teile im Rohr,
// laesst aber in der Mitte ein Guckloch frei.
// Wird ueber das Rohrende gestuelpt.
// Masse aendern, dann F6 (Render) und als STL exportieren.

tube_outer_d = 70;    // AUSSENdurchmesser des Rohrs (worauf der Ring greift)
view_hole_d  = 35;    // Guckloch in der Mitte (3,5 cm)
clearance    = 0.4;   // Spiel (zu stramm? groesser. zu locker? kleiner)
wall         = 3.5;   // Wandstaerke der Schuerze
skirt_h      = 20;    // wie weit der Ring ueber das Rohr greift
face_th      = 3.5;   // Dicke der vorderen Halte-Flaeche (mit Guckloch)

$fn = 200;

bore_d  = tube_outer_d + clearance;   // Schuerze innen
outer_d = bore_d + 2*wall;            // Ring aussen
total_h = skirt_h + face_th;

difference() {
    cylinder(d = outer_d, h = total_h);                       // Grundkoerper
    translate([0,0,-0.01])
        cylinder(d = bore_d, h = skirt_h + 0.01);             // Schuerze fuers Rohr
    translate([0,0,-0.01])
        cylinder(d = view_hole_d, h = total_h + 0.02);        // Guckloch durch
}

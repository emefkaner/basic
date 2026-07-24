// Variante C: HALTERING mit Guckloch fuer das verkuerzte Piraten-Fernrohr.
// Kein geschlossener Deckel: haelt die ausfahrbaren Teile im Rohr,
// laesst aber in der Mitte ein Guckloch frei. Wird ueber das Rohrende
// gestuelpt. Sichtbare Kanten sind abgerundet (Original-Look).
// Masse aendern, dann F6 (Render) und als STL exportieren.

tube_outer_d = 70;    // AUSSENdurchmesser des Rohrs (worauf der Ring greift)
view_hole_d  = 35;    // Guckloch in der Mitte (3,5 cm)
clearance    = 0.4;   // Spiel (zu stramm? groesser. zu locker? kleiner)
wall         = 3.5;   // Wandstaerke der Schuerze
skirt_h      = 20;    // wie weit der Ring ueber das Rohr greift
face_th      = 3.5;   // Dicke der vorderen Halte-Flaeche (mit Guckloch)
edge_round   = 1.5;   // Kantenradius (Abrundung). 0 = scharfe Kanten.

$fn = 200;

hole_r  = view_hole_d / 2;
inner_r = (tube_outer_d + clearance) / 2;   // Schuerze innen (Rohr passt rein)
outer_r = inner_r + wall;                    // Ring aussen
z1 = skirt_h;                                // Unterseite Halte-Flaeche
z2 = skirt_h + face_th;                      // Vorderseite

// Querschnitt (Radius, Hoehe), wird um die Z-Achse gedreht:
profile = [
    [hole_r,  z1],   // innere Kante Halte-Nase, unten
    [hole_r,  z2],   // Guckloch-Rand vorne
    [outer_r, z2],   // vorne aussen
    [outer_r, 0],    // Schuerze aussen unten
    [inner_r, 0],    // Mundkante (offen fuers Rohr)
    [inner_r, z1],   // Schuerze innen oben
];

rotate_extrude()
    // konvexe (sichtbare) Ecken abrunden, Aussenmasse bleiben erhalten:
    offset(r = edge_round) offset(delta = -edge_round)
        polygon(profile);

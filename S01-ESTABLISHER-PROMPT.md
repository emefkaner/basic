# S01 Establisher — Seedance 2.5, 30 s (aktueller Stand)

Settings: siehe `S01-ESTABLISHER-BASELINE.md` (von S14 übernommen).
Basis: die 15-s-Fassung, die bisher am besten funktioniert hat.

## Was gegenüber der 15-s-Fassung geändert wurde

1. **Auf 30 s gestreckt.** Die zusätzliche Zeit liegt fast vollständig im
   Spannungsaufbau vor dem Zug (Abstieg aufs Gleis + Vibrationsbeat wachsen von
   5 s auf 14 s) und in der Ausfahrt am Schluss.
2. **Neu: Vibrations-Beat auf dem Gleisbett** — Schotter fängt an zu ticken,
   zu wandern und schließlich zu tanzen, bevor die Iron Cloud im Bild ist.
3. **Neu: Tierschädel auf dem Gleis** — liegt auf einer Schwelle im nahen
   Vordergrund, vibriert mit, wandert über die Schwelle und ist nach der
   Überfahrt vom Fahrtwind weggerissen (als Endzustand formuliert, nicht als
   Vorgang).
4. **Entschlackt:** Das Design des Zuges wird im Text nicht mehr nachbeschrieben
   (kein „gold lettering", „brass fittings", „red-framed windows"). Aussehen
   kommt zu 100 % aus der Referenz — Regel „One owner for appearance" aus
   `CLAUDE.md`. Im Text bleibt nur die zählbare Struktur: drei Wagen, Reihenfolge,
   vollständig, Ende an der Rückwand des letzten Wagens. LOCATION MAP und
   POSITIVE LOCKS auf prüfbare Bildeigenschaften gekürzt.

Falls die Fassung driftet, sind das vier voneinander unabhängige Rücknahmen —
insbesondere Punkt 4 lässt sich einzeln rückgängig machen.

## Prompt

```
SCENE CONTEXT
Opening shot. The empty American West at midday. The camera starts on the blazing sun, tilts down across mesas, saguaro and telegraph poles to find a frontier town far off across the plain, then keeps descending onto a dead-straight railroad line until it is almost touching the rail. The desert is silent — until @[IRON-CLOUD-Normal](f69cfac8-14bc-4845-bdd7-41588194b326) bursts over the camera from behind and tears away down the track toward the town.

ACTIVE REFERENCES
@[IRON-CLOUD-Normal](f69cfac8-14bc-4845-bdd7-41588194b326) — the train, running on the rails. Its entire design comes 100% from this reference and from nothing else; the text does not re-describe it. The formation is always shown whole and complete: exactly three cars coupled in a straight line — locomotive leading, tender second, passenger wagon last — ending at the rear wall of the passenger wagon.
@70710ab3-55e4-4901-bef6-06dc8652dc15 — the town far down the line. Its architecture, materials and character come 100% from this reference.

LOCATION MAP
Foreground: the twin steel rails on dark weathered sleepers in pale gravel ballast, spikes and tie plates rusted, a tumbleweed lodged against the rail. On a sleeper between the rails, about two metres in front of the lens, lies a bleached cattle skull, its horns spanning roughly the width of one sleeper. Midground: saguaro cacti along the line, ocotillo, sagebrush and prickly pear, dry cracked earth, scattered red rocks, a line of leaning telegraph poles with sagging wire marching beside the track. Background: red-ochre mesas and flat-topped buttes on both sides of the plain, and far along the line the town of @70710ab3-55e4-4901-bef6-06dc8652dc15. Above: a wide, empty cobalt sky with two vultures turning slowly.

TOWN DISTANCE
The town sits roughly one and a half kilometres away, far down the line near the horizon. At that range it reads as a small but clearly defined cluster of low timber buildings with the water tower standing above them and a thin thread of smoke rising, softened and shimmering in heat haze — unmistakably a town, and a long way off. It stays that size for the whole take.

FIRST FRAME / BLOCKING
Open pointed straight at the blazing midday sun in an empty sky, the frame flooded with light and long horizontal anamorphic flare streaks sweeping across it. Nothing else is in shot yet.

FORMAT MODE
One single continuous 30-second shot from first frame to last, with no cut, edit or transition anywhere in the take — the move flows unbroken from the sun down to the rail and through the pass. The camera does not cut on its own.

OPTICS
35mm anamorphic prime character throughout: 2.39 ultra-widescreen, oval bokeh, strong horizontal blue flare streaks and veiling glare off the sun, natural perspective with straight verticals.
Segment 1, 0.0s to 14.0s: 84° wide field of view holding sun, landscape and the line to the horizon. No drift mid-segment.
Segment 2, 14.0s to 30.0s: 47° at rail height. No drift mid-segment.

CAMERA
One unbroken move: a slow tilt down from the sun across the sky and the mesas to the desert floor, flowing straight into a slow crane descent onto the track. The camera is dead centred on the centreline between the two rails and stays there for the whole descent, looking down the line toward the distant town, until it settles roughly twenty centimetres above the rail head — so low that the near sleepers, the ballast and the skull loom huge in the foreground and the horizon sits high in frame. It holds there for the rest of the take. The move is calm and controlled throughout; only in the last third does the camera shudder with the ground.

ACTION
0.0s to 4.0s — Hold on the sun, anamorphic flares raking across the frame. Two vultures drift through the glare. The camera begins to tilt down.
4.0s to 9.0s — The tilt continues down past the mesas and buttes, revealing the open desert: saguaro, sagebrush, telegraph poles, red rock, and far down the plain the small distant town of @70710ab3-55e4-4901-bef6-06dc8652dc15 shimmering in the heat.
9.0s to 14.0s — The move flows into a crane descent onto the railroad, the camera dropping along the centreline between the rails until it is just above the rail head. Ballast, sleepers, the lodged tumbleweed and the cattle skull on its sleeper fill the lower frame; the polished rails run away dead straight toward the town. Everything is dead still — not a stone, not a grain moves.
14.0s to 18.0s — The stillness breaks. A fine shimmer runs along the rail crowns. Single pebbles in the ballast begin to tick and inch sideways, dust shivers off the sleeper faces in thin veils, and the skull rocks minutely on its horn, turning a few degrees.
18.0s to 22.0s — The tremor grows into a hammering. Stones jump clear of the ballast and dance across the sleepers in the foreground, gravel creeps in visible waves, a loose spike rattles up and down in its plate, the tumbleweed shakes free and rolls out of frame, and the skull chatters and walks bodily across the sleeper. The rails visibly quiver.
22.0s to 24.0s — The shaking turns violent, the whole frame trembling, ballast leaping. A steam whistle screams out from directly behind the camera. Dust and grit blast forward past the lens and a shadow sweeps over the track from behind.
24.0s to 28.0s — @[IRON-CLOUD-Normal](f69cfac8-14bc-4845-bdd7-41588194b326) bursts into frame from directly behind the camera and passes straight over the lens at 90 km/h, moving AWAY down the line: first the locomotive thundering overhead, then the tender, then the last wagon, each blotting out the sun in turn, wheels riding the rails on both sides of the lens. The slipstream takes the skull off the sleeper and hurls it out of frame; from here on the sleeper where it lay is bare.
28.0s to 30.0s — All three cars are ahead of the camera, racing away down the dead-straight track toward the distant town, smoke pouring back, dust boiling up behind them, the machine shrinking down the line. The last loose stones trickle back into the ballast as the shot ends.

PHYSICS
Enormous mass and speed — the rails deflect visibly under each axle as it passes, ballast is thrown outward, dust and grit blast up and hang in the air, and the slipstream drags scrub and loose stones along after the train. The pebbles behave as small hard bodies: they tick, hop, land and settle with real weight, never sliding smoothly. The skull is light, hollow bone — it rocks, chatters and is finally snatched away like an empty shell. The vibration builds from a fine shimmer into a violent hammering, then eases as the machine pulls away, and the dust of its wake churns and settles slowly on the line behind it.

LIGHTING
Hard high midday sun, light falling steeply, small shadows pooling directly beneath the sleepers, the cacti, the telegraph poles, the skull and the passing train. Fierce specular glare along the polished rail crowns, running away to the horizon like two lines of light. Deep shadow across the track as the locomotive blocks out the sun overhead. Heat haze at 40% shimmering along the line and softening the distant town and mesas. White balance 5600K.

COLOR GRADE
Gritty spaghetti-western palette: bone-white dust on pale ochre ballast, red-ochre rock, dusty sage green on the cacti, dark weathered timber in the sleepers, black iron and burnt steel, hard cobalt sky bleaching towards the horizon, crushed blacks and scorched highlights.

ATMOSPHERE
Dry, still air with dust hanging at 30%, rising to a churning 80% as the train passes. Fine grit and dry grass are torn up and whipped past the lens. Everything wears a film of desert dust.

AUDIO
Long, deep silence at the start — only faint wind and the cry of a distant bird. Then a low rail hum growing into a rattle, gravel ticking and clattering on the sleepers, the scream of a steam whistle close behind the camera, and the full deafening roar of the locomotive hammering overhead, wheels pounding the joints, steam and wind tearing past — then the roar receding away down the line into the distance.

STYLE
Photoreal live-action cinematic spaghetti western, gritty, grimy and weathered, shot as if captured on real film on a working location — anamorphic ultra-widescreen with strong horizontal flares and oval bokeh, pronounced film grain, dust on the lens, natural heavy motion blur.

OUTPUT SETTINGS
1080p, 21:9 anamorphic widescreen, 30 seconds, real-time speed start to finish.

POSITIVE LOCKS
One single unbroken continuous shot across all 30 seconds, with no cut, edit or transition anywhere in the take. It opens on the sun with anamorphic flare and tilts down through the landscape before descending to the rail. The camera stays exactly on the centreline between the two rails for the whole descent and ends roughly twenty centimetres above the rail head, holding there. The ballast comes alive before the train arrives: pebbles tick, hop and dance across the sleepers, and the cattle skull rocks, walks across its sleeper and is gone from the track after the pass, its sleeper bare. @[IRON-CLOUD-Normal](f69cfac8-14bc-4845-bdd7-41588194b326) enters from behind the camera, passes over the lens and travels AWAY from camera down the line toward the town, receding into the distance. The design of the train comes 100% from its reference in every frame — exactly three cars coupled in a straight line, locomotive, tender and passenger wagon in that order, complete, ending at the rear wall of the passenger wagon, and all three pass over the camera in turn. The environment stays classic Wild West throughout — saguaro cacti, sagebrush, telegraph poles, red mesas and buttes, dry cracked earth. The town of @70710ab3-55e4-4901-bef6-06dc8652dc15 stays roughly one and a half kilometres away near the horizon, small and hazed. Sun stays high at midday with small shadows directly beneath objects. Anamorphic character throughout.
```

## Assets für diesen Prompt

**Anhängen:**
- Element `@IRON-CLOUD-Normal` (`f69cfac8-14bc-4845-bdd7-41588194b326`)
- Element Stadt (`70710ab3-55e4-4901-bef6-06dc8652dc15`)

**Nicht anhängen:**
- kein `start_image` / Startbild
- kein Quell-Video, keine Plate
- keine Figuren-Elemente (@Schmitzkowsky, @JOHN, @CHRIS o. ä.) — im Shot ist
  niemand zu sehen

**Generator-Einstellungen:** Seedance 2.5 · 30 s · 1080p · 21:9 · Audio an ·
Multi-Shot aus · Bitrate high.

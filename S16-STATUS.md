# S16 — parlour car, in flight

## Conventions for the whole sequence

- The Iron Cloud is **airborne, forty metres up**. Every window shows mostly
  open sky; the terrain of `@WILDWEST` only along the bottom edge, seen steeply
  from above; cloud shreds pass at window level. No rails, no ground at eye
  level, no rail clatter in the sound.
- Landscape streams **left to right** through the windows, never reversing.
- Background at **f/2**, far out of focus in every frame — soft fields, smears,
  oval bokeh.
- Only asset tagged: **`@WILDWEST`**. Never tag the actors — they are in the
  plate, and a tag re-renders their faces.
- Generation length = plate length; audio on, original dialogue preserved.

## The Lincoln portrait

The framed Lincoln portrait on the wall makes Higgsfield reject the job. Every
parlour-car plate has to be pre-processed: track the picture frame, blur the
inner picture, leave the gold frame standing. Method and pitfalls are in
`CLAUDE.md` ("Real people in the set dressing block the upload").

Tooling lives in the session scratchpad: `npm i ffmpeg-static`, then
`track*.js` (correlation tracker) → `mask*.js` (writes a raw gray mask) →
ffmpeg `alphamerge` + `overlay`. Verify the finished file across the whole
clip, not at one timestamp.

## Shot status

| Shot | Length | Masked | Generated | Notes |
|---|---|---|---|---|
| S16_02 | plate | — | prompt delivered | Young alone, small window, greenscreen |
| S16_03 | 13.3 s | portrait blur slipped | rejected | dynamic, greenscreen, prop from 10.0 s |
| S16_05 | 15.6 s | yes (tracked + keyframes 0.55–2.6 s) | came back driving | prompt reworked: altitude leads, flare at 0:04, artifact from 0:12 |
| S16_06 | 10.3 s | not needed (no portrait) | 1st run re-staged; 2nd prompt hit the NSFW text filter | artifact close-up; final prompt de-personalises the light ("lantern inside the brass"), veins only under the hand, max 10 cm, no liquid |
| S16_07 | 15.0 s | yes (tracker alone) | prompt delivered | second small window on the left matters |
| S16_10 | 14.3 s | not needed (no portrait) | prompt delivered | Young seated, window left, scaffold in plate named in the exclusion list |
| S16_11 | 10.3 s | yes (tracked + keyframes to 2.0 s) | passed | |
| S16_12 | 7.5 s | not needed (no portrait) | prompt delivered | same setup as S16_10, closer |
| S16_13 | 15.0 s | yes (tracked) | passed | first proof that the portrait was the cause |
| S16_14 | 11.0 s | yes (tracked, box to frame bottom) | 1st run re-staged (panorama window); pure-post sky version rejected by user | current prompt: KEEP-first minimal window block, 30 m, TRACKED plate; if it works, restore the original Lincoln region in post from the tracking data |

## S17 (prison compartment, airborne)

- Height in S17 is **20 m** (S16 flies at 40 m, S16_14 was reworked at 30 m per
  user — heights are per-shot, always confirm).
- S17_02 (4.0 s): VILLAIN from behind at the grille, hand on the grimy pane.
  No portrait, no prop — original plate uploads as-is. Prompt delivered: view
  through the pane → @WILDWEST from 20 m, left to right, dirt on the glass
  explicitly preserved (the model must not "clean" the pane).
- S17_04 (10 s): passed with the defused packaging (three timed flashes).
- S17_05 (4 s): one flash at 0:02 toward the lens; prompt delivered.

## Music keeps sneaking in

Despite a closing "No music." the model scored the first artifact shot. Since
then every prompt carries a dedicated block: "AUDIO — DOCUMENTARY SOUND ONLY,
ABSOLUTELY NO MUSIC", listing the excluded categories, a falsification clause,
and any low tone described as physical resonance ("metal resonating in a room,
no melody, no rhythm, no rising pitch") — never as a "deep tone" alone.

## The NSFW text filter has a body cluster

The S16_06 effect prompt was rejected: "light seeping through the gaps between
his fingers", "rims their edges", "warm glow under his palm", "skin", plus
"he has done this many times and is braced for it" read as a different kind of
scene to a cluster matcher. Fix: de-personalise light near bodies — the light
belongs to the object ("a lantern inside the brass", "traces the outline of
the hand"), minimise finger/skin vocabulary, cut experience-innuendo lines.

## S16_05 — the extras in that shot

- **Flare at 0:04.** A practical flare exists in the plate. It is motivated as
  a sun glint off the machine's brass and rigging outside the glass: a warm
  white-gold horizontal anamorphic streak with soft oval ghosts, half a second,
  once only.
- **The artifact from 0:12.** Young rests his hand on the brass device on the
  desk — a mind-control artifact. Resonance (hairline ring of light around the
  rim, trembling glass, humming horn, jumping dust, sub-bass) plus dim amber
  veins that wake at his fingers and creep slowly **downward** through the
  metal. At 0:13.5 the device pays for it: a dark bead wells from a seam and
  runs down the brass.
- **He does not show the pain.** He has used it often and is braced; his face
  stays exactly as filmed. Stated positively in the effect block so the model
  does not fill the stillness with an invented reaction.
- **He never lets go inside this shot** — the hand stays on the device to the
  last frame, so the veins are still glowing at the end. The retraction belongs
  in the following shot: veins withdraw to the fingers at the same slow speed
  and go out there, while the dark traces on the brass remain.

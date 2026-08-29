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
| S16_07 | 15.0 s | yes (tracker alone) | prompt delivered | second small window on the left matters |
| S16_11 | 10.3 s | yes (tracked + keyframes to 2.0 s) | passed | |
| S16_13 | 15.0 s | yes (tracked) | passed | first proof that the portrait was the cause |

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

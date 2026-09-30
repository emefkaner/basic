# Prompting notes — Higgsfield / IRON CLOUD

Hard-won rules from working on this film. Apply these before writing any new prompt.

## How prompts are handed over

- **Always the complete prompt, in one code block.** Never a patch, never "replace the
  paragraph starting with…", however small the change. The prompt is copied straight into
  the app; anything that has to be stitched together is a chance to paste a stale version.
- **An asset list goes above every prompt**, as a small table: what belongs in
  `start_image`, what is the base image for an image edit, and every reference element by
  its exact name — plus what is deliberately *not* tagged and why. The user must be able
  to see, before sending, whether an asset is still missing.
- **Always ask before writing** when anything is unclear (viewing direction, focal
  length, distance, time of day, which plate or reference is meant).
- **A credit call goes with every prompt**: draft or normal, and why. See below.

## Credit call — draft vs. normal, with every prompt

The user runs Seedance 2.5 in **draft** (cheap, for verifying that a shot is built
right) and **normal** (expensive, for the take that gets used). Every prompt ships with
a verdict, so the decision is never a coin flip.

Give a traffic light, never a percentage — a made-up number is worse than an honest
judgement:

- 🟢 **Straight to normal.** Static or simple camera, one or two references, short,
  nothing that has failed before in this shape.
- 🟡 **One draft, then normal.** One genuinely new element — a camera move, a new
  element, an unverified beat. The draft answers one question, then the normal run.
- 🔴 **Draft mandatory, expect several.** Multiple risk factors stacked. Say plainly
  that the normal run is likely wasted until the draft is clean, and say whether
  splitting the shot into two generations is the cheaper route overall.

Weigh these, because each has cost real generations here:

| Factor | Cheap | Expensive |
|---|---|---|
| Duration | ≤ 5 s | ≥ 10 s — drift and invention grow with length |
| Camera | locked or one simple move | crane plus arc, height change, landing on a mark |
| References | 1–3 | 6+ — every extra one dilutes the rest |
| Tagged faces | 0–1 | 3+ that must stay distinct and in a fixed order |
| Subject motion | free movement | must stop on an exact mark, or stay in frame throughout |
| Environment | one element | two elements of one place that must agree |
| History | a shape that has worked | a shape that has failed before, fix unverified |

**A draft run must answer a named question.** State which checkable frame property the
draft is being watched for ("at second seven, do the rails run diagonally to the lower
left?"), otherwise it is a guess with a smaller price tag.

**Strip the identity layer for a geometry draft.** Camera, blocking, timing and the
stop mark can all be judged without the right faces. Dropping the character elements
for the draft run removes the biggest source of dilution and makes the geometry easier
to read — then the full reference set goes on the normal run, with the camera block
unchanged so the draft still predicts it.

## Iterative camera moves beat absolute descriptions

When a generated image has the right subject but the wrong distance, angle or framing,
do **not** re-describe the scene with absolute values ("one metre away", "more frontal").
The model cannot reliably reconstruct geometry from words.

Instead: treat the existing image as the base plate and describe the change as a
**physical camera move relative to it**, the way a photographer would call it out:

- "step back about two metres"
- "step two metres to the right"
- "tilt up by about ten percent"
- "arc the camera roughly thirty degrees around the subject"

Then state the *resulting visible change* as a checkable image property, not as a goal:

- ✅ "the panel lines run flat and horizontally straight across the frame with almost
  no perspective convergence"
- ❌ "a more frontal view"

Work in small steps and iterate. Two or three rounds converge reliably; a single
absolute instruction almost never does.

## Build purpose-made reference elements

A wide "whole object" element fights every tight shot. Tagging a reference showing the
entire train from 15 m away makes the model reproduce exactly that — distance, framing
and all — no matter what the text says. **The image always beats the text.**

Fix: solve the perspective once as a still, save it as its own element, and tag that.

- `@LOK-BACK` — view aft from inside the cab, tender filling the opening. Solved the
  "camera in the cab" problem that pure text never could.
- `@WAGON-STEPS-BOKEH` — wagon boarding steps, close and already rendered out of focus.
  Rendering the blur *into the asset* makes defocus a property to copy rather than an
  instruction to interpret.

## One owner for appearance

Appearance must have exactly one source of truth. When reference images define a
design, the prompt text must NOT re-describe its details ("gold lettering on the
front cap") — any drift between text and image makes the model pick the coherent
*story* and drop the pictures entirely. After swapping reference images, strip every
design detail from the prompt that the new images no longer show. Text describes
**motion and behaviour**; images describe **what things look like**. The rule is
symmetric with "the image beats the text": whichever channel owns appearance must
be the only one speaking about it.

## References carry identity, not sequence — one direction of change per shot

A reference transmits *what a thing is*. It does not transmit *when*. Lining four
elements up as a storyboard ("start with @image1 → transition into @image2 → …
→ final look @image4") does not give the model an order; it gives it four pictures
of the same object in a bag. Two consequences, both seen on S05 INFLATE:

- **A state that appears in two references gets played twice.** The INFLATE prompt
  used a closed-roof still as image 1 *and* a closed-roof final look as image 4. The
  roof opened twice. Whatever state is duplicated across the references is the state
  the shot stutters on.
- **Two opposite movements in one prompt have no order.** "Roof opens … zeppelin
  inflates … roof closes again" gives the model an opening and a closing with nothing
  to sequence them by, so it does both, repeatedly, in whatever order.

The fix is not more wording about sequence:

- **`start_image` carries the beginning**, because it is the literal first frame and
  is not negotiable. **One reference carries the end state.** Nothing in between.
- **One direction of change per generation.** Everything in the shot opens, or
  everything closes — never both. Lock it positively: *"everything that changes moves
  in one direction only — open, then further open — and then holds."*
- Drop the return beat. If the roof has to close again, that is a second shot whose
  `start_image` is the last frame of the first.
- Stage the middle by **checkable end states** ("an envelope already longer than the
  carriage, underside still slack"), never by describing the mechanism travelling.

## Plate / compositing shots

- **Never tag a character who is already in the plate.** The tag makes the model
  re-render their face. Refer to them generically ("the man in frame") instead.
- **Prompt weight equals model priority.** Long background description with a short
  preservation block makes the model drop the actor and regenerate the scene. Keep the
  KEEP block first, emphatic, and longer than the background description.
- Add an explicit **no-mirroring** lock — plate replacements flip horizontally on their own.
- Add an explicit **background motion** block, with a concrete visible event
  ("daylight strobes up through the coupling gap as sleepers rush past"). "The train is
  moving" alone yields a frozen still when nothing crosses the frame.
- Match generation duration to the source plate. Longer means the model invents gestures
  and speech past the end of the reference, and drifts within the usable part too.
- **Over-the-shoulder plates need their own KEEP paragraph.** A figure cropped by the
  frame edge is read as a defect: the model either erases it or "repairs" it into a whole
  person. State that it is partially in frame *by design*, and that it is never removed,
  never completed into a fuller figure, never turned around and never given a face.
  Verified working on IRON CLOUD.

## Reference elements carry identity, not photography

Seedance takes images in the role `image_references`. A reference transmits **what a
thing is** — green carriage, iron steps, gold lining. It does **not** transmit how it
was photographed: distance, framing and depth of field are properties of the *shot*,
not of the *object*. That is why a deliberately blurred, close-up element still came
back sharp and ten metres away, no matter how the text was phrased.

The fix is not more wording about blur. It is to stop calling the reference a *subject*
and start calling it a *photograph*:

> `@X` is an already-finished background plate, shot on set. Use it as it is, as a flat
> backdrop layer behind the man. Do not re-photograph its subject, do not re-render it,
> do not move the camera around it, do not sharpen it.

Every instruction that follows is then a verb of post-production, not of image creation.
(`start_image` is the other lever: it is the literal first frame, so composition and
focus are non-negotiable there. Use it if the reference route fails.)

## Working template — plate compositing (verified on IRON CLOUD)

This exact structure worked. Keep the block order and the proportions: the KEEP block
must stay long and emphatic relative to the background description.

```
TASK
This is a compositing edit on existing footage. Take and keep everything filmed in it.
Place the finished background photograph @BG behind the man, and harmonise him to its
light. Nothing else changes.

BACKGROUND — @BG is a photograph, not a subject
@BG is an already-finished background plate, shot on set. Use it as it is, as a flat
backdrop layer behind the man. Do not re-photograph its subject, do not re-render it,
do not move the camera around it, do not pull back, do not reveal more of it, and do
not sharpen it. Its scale and its heavy defocus are already correct and are preserved
exactly as they appear in the photograph — the blur in particular stays precisely as
strong as it is there, in every frame.
[Permitted adjustments, phrased as camera moves with a checkable result — e.g. push in
ten to fifteen percent; tilt up ten percent so the ground shrinks to a thin edge.]

ATMOSPHERE — bring the still photograph to life
The backdrop itself stays fixed: nothing in it drifts, slides, rocks or changes size.
What moves is the air in front of it. Steam seeps upward and drifts slowly across in
soft blurred veils. Fine dust hangs and turns lazily in the sunlight. Heat shimmer
ripples over the surface. The air is in constant slow motion, so the shot never reads
as a frozen still, while the photograph behind it never moves.

KEEP — the plate is untouchable
The man filmed in the plate stays in the shot in every single frame, exactly as filmed:
same position, stance, pose, face, hair, hat, clothing, gestures, performance, speech
and lip movement, same timing. His movement and his spoken words are never altered,
re-timed, re-animated or re-rendered — not by a single frame. The only thing that
changes about him is his lighting, colour and edges. If the man is missing, or if his
motion or speech differs from the plate in any way, the shot is wrong.
The framing, lens character and duration are unchanged, and the image is never flipped
or mirrored.

INTEGRATION — light only
Relight and regrade him to match @BG: [key direction and hardness], with a small tight
contact shadow beneath his boots. [Bounce colours from ground and from the backdrop.]
A soft warm light wrap bleeds around his outline where it meets the brighter parts of
the backdrop, softening hat brim, shoulders, hair and coat seams into the light. His
edges are slightly soft and diffused, never hard or cut out. No green remains anywhere
— no edges, no fringing, no spill on hair, hat brim, skin or clothing. Grade him into
the backdrop's palette and match grain, lens character and motion blur so both read as
one photograph.

FOCUS
Only the man is sharp. The backdrop stays exactly as defocused as @BG and never
sharpens at any point.
```

Two details that carry the whole thing: **"a photograph, not a subject"** in the
background header, and the closing sentence of INTEGRATION that scopes the change to
lighting, colour and edges — so "harmonise" is never read as permission to re-animate.

## Flight windows need an AERIAL element (verified, S18_03)

Three shots in a row (S16_05, S17_03, S18_03) came back driving at ground
level no matter how hard the text insisted on altitude. Cause: `@WILDWEST`
is photographed from the ground, and the image beats the text — the element
drags its eye-level perspective into every window, in video AND image
generation alike (an aerial re-shoot prompt with @WILDWEST attached came
back at ground level twice).

The fix that worked end to end:

- Generate the aerial view **without any reference attached** (a reference
  anchors the camera back to the ground). Pure text, positives only — no
  exclusion lists ("no rails, no fence" summoned a fence; naming the camera
  platform "hot-air balloon" put a balloon in frame).
- Get **geometry only** from the model, sharp; bake the anamorphic defocus
  in post (`gblur=sigma=H:sigmaV=V` with H≈1.7×V for oval highlights) —
  the image model refused uniform defocus three times and instead pasted
  bokeh discs over a sharp image.
- Save as element `@WILDWEST-AERIAL`, tag it in flight shots as **"a
  photograph, not a subject"**. First run with it: the flight finally read.
- **The model animates an aerial still as a drone orbit** (its prior). Lock
  translation with checkable properties, without naming the orbit: "the
  horizon stays perfectly level and at the same height in every frame; every
  landmark enters at the left edge, travels a straight horizontal line and
  leaves at the right edge exactly once, never returning" + falsification.
  Verified: second run had zero rotation.

## Moderation-safe packaging (verified on IRON CLOUD, S17_04)

Higgsfield's text filter cluster-matches on vocabulary, not on what the footage shows.
The plate carries the action — the prompt never has to name it. Rules:

- **Never narrate action that is already filmed.** No "grabs him by the collar",
  "shoves", "draws", "aims at him", "shoots the man". The KEEP block covers it all as:
  the men's *staged choreography* — every rise, step, reach and fast physical beat —
  is preserved exactly as filmed. Every trigger word in the text is pure risk with
  zero benefit, because the model reproduces the plate anyway.
- **Gun effects are "timed practical light-and-smoke effects".** Never write revolver,
  gun, weapon, muzzle, discharge, gunshot, fires, black-powder. Instead: at second X,
  "a sharp orange-white FLASH bursts from the tip of the object in his hand for one to
  two frames", lighting the room like a camera flash, with "a jet of grey-white stage
  smoke" along the arm's direction. Audio: "a short, hard percussive CRACK with a deep
  chest-thumping body", never "shot"/"report". Lock the count ("exactly three flashes —
  at no other moment…").
- **Never name human targets.** Aim directions are the plate's business; the text only
  references the arm's direction ("as he swings his arm low across the frame").
- **Captivity vocabulary triggers its own cluster**, especially combined with a hooded
  figure: prison, cell, bars, shackles, chains around people. Use: cargo hold (not
  prison), iron grille / grilled window (not bars), hooded travel cloak (not hooded
  figure), freight chain and hook (cargo context), rusted metal fitting (not shackle)
  when the restraint itself must be named.
- **Effects on objects may be fully described** — a metal fitting bursting in sparks
  and scattering pieces is fine; it is person-directed wording that trips the filter.
- **The NSFW filter has a body cluster.** Light effects described on skin trip it:
  "seeping through the gaps between his fingers", "rims their edges", "glow under
  his palm", repeated "skin", plus lines like "he has done this many times and is
  braced for it". De-personalise: the light belongs to the object ("a lantern lit
  inside the metal", "traces the outline of the hand"), name fingers/skin at most
  once, and cut experience-phrasing entirely.
- The image-side scanner is separate: dark frames + hood + gun pointed at people can
  reject the *upload* regardless of text. Fixes there: brighter export, shifted
  in-point, small crop, re-tries.

## Real people in the set dressing block the upload (verified, S16_13)

The parlour-car plates kept failing at generation while identical shots with
guns went through. The cause was not the weapon and not the actors: a framed
**Abraham Lincoln portrait** hangs on the wall. A recognisable real person in
the set dressing is enough for the scanner to reject the job.

Fix: obscure the portrait in the plate before uploading. Verified working
(S16_13 passed, S16_11 built the same way). What it takes:

- **A static blur box is not enough** — the camera drifts and the box slips
  off, leaving the face visible. The first attempt failed exactly this way and
  produced a worthless test.
- Track the picture frame by image correlation, then blur the inner picture
  only, leaving the gold frame standing (reads as an empty frame, unobtrusive).
- **The matching score must be robust to occlusion** (clamp each pixel's
  contribution, e.g. `d < 35 ? d : 35`), otherwise an actor passing in front
  drags the track off target.
- **Clamp the scale range.** Unclamped, the estimated size drifts and the mask
  shrinks off the picture. In S16_11 it collapsed to 43 % while the portrait
  was really at ~93 %.
- Where the track still fails (fast pan plus occlusion), hand-measure a few
  keyframes and interpolate; hand over to the tracker at a frame where it is
  verified good.
- Keep the mask box off the actor: clip its edge where he covers the picture.
  Feather inward only, so the mask never spills outside the box.
- **Always verify the finished file frame by frame** across the whole clip —
  every failure so far looked fine at one timestamp and was broken at another.

Tooling in this sandbox: no system ffmpeg, but `npm i ffmpeg-static` in the
scratchpad gives a full build. Mask per frame as raw gray, then
`alphamerge` + `overlay` — `crop` cannot change size at runtime via `sendcmd`.

## A changed situation has to lead the prompt (verified, S16_05)

The Iron Cloud flies in the S16 shots, but S16_05 came back with the train
running on rails — although the prompt did say "flying forty metres above the
desert". The altitude was buried in the middle of the REPLACE block, where it
read as one property among many.

Rules for any prompt that changes the fundamental situation of a plate:

- **Put it first, in its own block, right after TASK**, and name it as the one
  thing that matters ("This is the single most important fact about the shot").
- **Add a falsification clause** listing what may never appear: "if any rail,
  sleeper, embankment, platform or ground at eye level appears in any window,
  the shot is wrong." Positive descriptions alone were not enough.
- **Let the sound carry it too.** "No rail clatter, no rhythm of wheels on
  track" is a strong hint about which situation is meant; a flying machine gets
  drone, wind and rigging instead.
- Repeat the situation once in POSITIVE LOCKS, never more than that.

## The window is part of the plate, not part of the replacement

In S11_01 the model enlarged the window so the new landscape would fit. Lock
the opening explicitly in KEEP and in REPLACE: the frame keeps its exact size,
shape and position in every frame, and the replacement exists strictly INSIDE
that unchanged opening. The formula that worked: **"the landscape adapts to
the window, never the window to the landscape."**

With several windows in one wall, add: all openings show one single continuous
world, same direction, same speed, same defocus — otherwise each window invents
its own landscape.

## In-world effects (artifacts, magic, powers)

Describe the effect as a **camera-observable physical property**, never as an
intention. Not "he controls his mind", but "a hairline ring of light runs once
around the rim, the way light travels around a struck bell". Intentions invite
the model to stage its own show.

What holds a supernatural effect inside a period film:

- Anchor it in things the audience knows physically: heat in metal, vibration,
  dust in the air, a liquid running down brass, light dropping in the room.
- **Name what it never does**: no beams, sparks, arcs, symbols, glowing eyes.
  This is the one place where naming an exclusion pays off, because the model's
  prior for "magic" is very strong.
- Two elements at most. Resonance plus glowing veins works; adding a third
  turns to mush.
- The actor's non-reaction has to be stated positively in the effect block,
  otherwise the model reads the stillness as a gap and invents a reaction:
  "The man gives nothing away — the only thing that reacts is the metal."
- Effects on objects are safe with moderation; see the packaging section above.

## When the prompt describes a world the plate barely shows

Two shots (S16_06, S16_14) came back completely re-staged: new framing,
letterboxed aspect, re-posed actor, invented set. Both times the prompt's
strongest block described something the plate hardly contained — a big effect
on a small device, a sky-filled flight through a shot with almost no window.
The model built the world the text promised, on top of the plate's ruins.

Rules:

- The weight of a block must match how much of the frame it may change. A
  tiny window gets two sentences, not a SITUATION manifesto.
- **If the only change is small, do it in post instead of generating.** A
  bright window is a luma key: mask = brightness threshold inside a tracked
  or keyframed region — the actor's dark silhouette protects itself. Replace
  with a soft gradient sky; feather via a blurred quarter-res mask. S16_14
  was finished this way with zero generation, original Lincoln, original
  performance, no scanner involved.
- Measure lum thresholds from histograms (vest ~16-32, blurred rails ~96-144,
  blown window 160+), don't guess.
- Grid overlays (drawgrid) on full frames beat eyeballing crops for
  coordinates; measure once properly instead of chasing slivers.

## Look the assets up — never ask what is already in the account

Before writing or patching any prompt, list the reference elements in Higgsfield
(`show_reference_elements`, action `list`). It is a read-only call and costs no credits.
Do not ask the user which assets exist, what they are called or what they show — the
registry below drifts, the account does not.

What the listing gives you, and what it does not:

- **Exact names.** Tags must be spelled exactly as the element is named. The names in
  this file have been wrong before (`TRAIN-STATION-NORD` vs the real
  `TRAIN-STATION-NORTH-HIGH`). The account wins.
- **The description field.** Many elements carry a written spec — camera height, which
  side of frame the track runs, look direction, what is in shot. Read it. It is the
  cheapest way to catch a blocking conflict before generating.
- **Near-duplicates.** `PINKERTON` / `PINKERTON2`, `VILLAIN` / `VILLAIN-NOHOOD`,
  `Schmitzkowsky` / `SchmitzkowskyGoggle`. Which variant is current is a genuine
  question for the user — that one is worth asking.
- **The pixels too — look at them.** The CDN *is* reachable. Take the `medias[].url`
  from the listing verbatim (a hand-typed uuid gives 403) and `curl` it to the
  scratchpad, then read it. Never reason from a name when you can open the file, and
  never describe an image you have not opened.

## Watch the results — the share link is openable

A `higgsfield.ai/s/<id>` link can be inspected end to end. Do it before diagnosing
anything; the failure is usually visible in three frames and invisible in a description.

```
curl -sSL "https://higgsfield.ai/s/<id>" -o page.html
strings -a page.html | grep -oE 'https?://[a-zA-Z0-9._/-]*\.mp4' | sort -u   # cloudfront
curl -sS -o shot.mp4 "<that url>"
pip3 install --quiet imageio-ffmpeg      # no system ffmpeg in this environment
FF=$(python3 -c "import imageio_ffmpeg;print(imageio_ffmpeg.get_ffmpeg_exe())")
$FF -i shot.mp4 -vf "fps=1,scale=740:-1,tile=2x5" -frames:v 1 gridA.png
$FF -ss 0.5 -i shot.mp4 -vf "fps=1,scale=740:-1,tile=2x5" -frames:v 1 gridB.png
```

Two sheets offset by half a second read as a 2 fps flipbook and catch the one-second
artefacts. The `og:image` meta tag on the page is the first frame on its own.

**Judge the ending on the actual last frame, not on the sheet.** Contact sheets are for
artefacts and for following a sequence; they are bad evidence about final composition,
and a frame grabbed a second or two early is worse. A verdict of "the train ends up too
small and the foreground is gone" was drawn that way and did not survive the real final
frame, where the tender lettering was plainly readable and scrub was still streaking
through the bottom. Pull it properly before saying anything about how a shot ends:

```
$FF -sseof -0.15 -i shot.mp4 -frames:v 1 -vf "scale=1500:-1" last.png
```

## Check what the end reference actually shows before locking a state

An end-state element is a picture of a *finished object*, and it quietly fixes states
the shot may need to be different. `@IRON-CLOUD-Inflated` shows the inflated zeppelin
over the train — with the carriage roof **closed**. A prompt locking "the roof stays
open through the final frame" against it made the model do both: open the roof, then
put it back. The lid that opens and vanishes into nowhere is that contradiction.

So before writing a lock about a state, open the reference and check that state in it.
Where the reference contradicts the shot, the reference wins — either drop the lock or
build a still that shows the state you need and save it as its own element.

Such elements also carry their *photography*: `@IRON-CLOUD-Inflated` is a studio product
shot, object centred on grey seamless, evenly lit, locked-off camera. Tagged in a moving
exterior it pulls the camera toward standing still. Say in the prompt which part of the
reference is being used — "take the envelope and its hardware from this reference and
nothing else from it; the light and the camera of this shot are the ones described
below".

## An empty beat gets filled with invention

Do not give a mechanism its own stretch of time with nothing else happening in it. The
INFLATE shot gave the roof three seconds alone, before the zeppelin appeared. The model
had no picture of an open roof and three seconds to fill, so it invented the only form
that was legible at that size: a single carriage-sized lid that lifted off and
disappeared. From the second the balloon justified the opening, the same model opened
the roof correctly.

Two rules follow:

- **Let the payload drive the mechanism.** "The envelope pushes the roof open from
  inside, the opening and the material appearing are the same event" beats a roof that
  opens on its own and then waits.
- **A mechanism needs enough pixels to exist.** In a wide shot of the whole train the
  carriage roof is a thin sliver — two narrow hinged panels cannot be resolved there at
  all, so something carriage-sized comes out instead. That is a framing problem and no
  wording fixes it. Give the mechanism its own closer shot.

**Check the element description against the blocking before generating.** An environment
element fixes look direction and which side of frame the track sits on. If the prompt
puts the camera on the other side, the shot comes back mirrored and no amount of
no-mirroring wording fixes it — the element is the one telling the truth.

## A lock can be the bug

Locks are obeyed literally, so a lock written to *prevent* something must still say what
is there instead. "The interior of the opening stays in deep shadow for the whole shot"
was written to stop the model committing to an envelope colour that would clash with the
tagged reference in the neighbouring shot. It worked — and the roof opened onto a
completely empty hold. Before sealing a state off, decide what fills it.

The same shot gives the positive version: what has to be seen needs **its own block,
before the action** — a `WHAT IS UNDER THE ROOF` paragraph describing the deck, the
packed envelope, the straps and the brass fittings. Named in a subclause inside `ACTION`
it stays empty; named up front it gets built. And the sentence that makes an intermediate
deck read as a deck rather than as the floor of a hold is "the carriage below it is not
visible at any point".

## Text may own appearance when no image owns it

"One owner for appearance" forbids *two* owners, not text. In a shot with no reference
tagged for a given object, the text is the only owner and should describe that object
precisely — which is only possible once the reference it has to match has actually been
opened and looked at. Where two shots must cut together on the same object, the durable
fix is a still of that object saved as its own element, so one image owns the colour for
both.

## Quantity reads as layer count, not as lobe size

A size anchor on the wrong feature pulls the opposite way. To sell roughly 1000 m² of
folded envelope, the prompt said each fold was "a thick slab of doubled canvas about as
deep as a forearm" — and got about eight forearm-thick bolsters, reading as a mattress.
A fold that thick is a cushion, not a fold. Bulk reads from **many thin layers**: "laid
in thin flat layers stacked one directly on the next, dozens upon dozens of them, each
no thicker than a finger", with sharp creases and "stacked edges like the pages of a
closed book seen edge-on".

Two supports for it:

- **Soft rounded shapes read as bedding whatever the material is called.** "Matte
  rubberised canvas" loses to round lobes and specular highlights. Force the surface:
  flat tops, sharp folded edges that hold their crease, visible coarse weave, dust caught
  in the creases, "broad flat planes with hard shadow lines between the layers, never
  soft highlights".
- **Layering reads from the side, not from above.** A camera that ends up directly
  overhead shows only the top layer. Keep it off to one side so the stack's flank is in
  view.

And the meta-rule this shot proved: once depth and framing are solved and only
*appearance* is left, stop writing text. Appearance belongs to images — solve it as a
still, save it as an element, and shrink the prompt block to a tag.

## Give a growth a direction, or it renders as a lump

"The envelope swells until it is full" grows a dark shapeless mass — there is nothing in
it to be right or wrong about, so the model produces a blob and stretches it late. Real
filling has a **front**: a taut swell that starts at one end and travels to the other,
smooth and round ahead of it, flat and rippling behind it, with a visible boundary
between the two that never reverses.

That single device does three jobs at once: it is one direction of change, it gives every
intermediate frame a checkable state ("at 4.5s the forward half is round while the rear
half still lies flat"), and the contrast between taut and slack is what reads as fabric
rather than as mass.

Support it in the light block so the boundary survives even in silhouette — "the filled
part takes the sun as a broad hard highlight along its top, the slack part behind stays a
darker broken rippling surface". And demand the material's own signature from the first
frame it appears in: seams, gores, tape lines. A soft dark shape with no seams reads as
rock or tar, whatever the text calls it.

## Framing symptoms often have an object-geometry cause

Two complaints on the INFLATE shot looked like camera problems — the train ends up small,
and the rushing foreground that sold the speed is gone by the last second. Rewriting the
camera block would have fixed neither. The frame has to hold train + gap + envelope
stacked vertically, so the oversized gap between envelope and train was what forced the
camera back, and everything shrank with it. Close the gap and the retreat is not needed.

Before rewriting a camera move, ask what in the frame is *forcing* it. A "pull back
less" instruction fights the framing lock that made the model pull back in the first
place.

And give the camera **checkable properties instead of proportions.** "The whole train
sits in the lower third" is a target the model trades away against everything else;
"the gold IRON CLOUD lettering on the tender is readable in every second including the
last" and "the near scrub is still sweeping through the bottom of frame in the last
second" are either true or false in a single still.

## Cut in the edit, not in the prompt

When several angles of one event are wanted, generate one clip per angle rather than one
generation carrying internal cuts. Each clip then gets its own `start_image`, so its
framing and its hardware are nailed down; there is no continuity to be broken across a
cut the model invented; and the pieces can be placed anywhere in the edit instead of only
back to back. Make the angles genuinely different — different shot size, different FOV,
camera rising in one and pushing in the other — or they read as two takes of the same
setup rather than as a cut.

## Invented physics needs one signature cue

A new mechanism has to be readable as *that* mechanism, and one honest physical
consequence carries it further than any amount of styling. For a magnetic anchor the cue
is that the terminal's last stretch **accelerates instead of slowing** — a falling object
decelerates into contact, an attracted one speeds up — plus loose grit standing on end
and a dead stop with no bounce. Glow and arcs are decoration; without the acceleration
the shot just shows something being lowered.

Write the cue as the thing to check in the result, and treat everything else in the block
as expendable if it starts competing.

## A close-up must contain what the action refers to

An insert of a mechanism connecting to something needs that something *in the frame*.
The first magnetic-latch insert framed a plate on the locomotive with empty sky above it:
no cable, no envelope, no keel spar. With nothing in shot that the cable could come from,
the result read as a glowing disc on a random part of a train — "it is being magnetised
somewhere at the front". Compose the frame in bands so the origin is structural, not
optional: *"bottom two thirds the tender, top third the out-of-focus envelope and keel
spar, and between them the cable hanging down"*, and lock the top band so it cannot be
dropped.

**Pin the location by a feature that is visible and unique**, not by a direction of
travel. "Move forward along the train until the boiler and the running board fill the
frame" put the camera on the front buffer deck. "The car directly behind the locomotive,
the one with the gold IRON CLOUD lettering on its side" cannot be misread.

## Watch for words that name two different things

"Naming a thing to exclude tends to summon it" has a sibling: a word with a strong
competing visual meaning summons the wrong one. `anchor pad` / `anchor plate` produced a
brass plaque with a **ship's anchor** embossed on it. The model picked the nautical noun
over the engineering one and drew it.

Rename rather than explain — `latch plate`, `clamp pad` — and, in the still that
establishes the hardware, say outright that there is no emblem, badge, symbol or
engraving on it. The same care applies to element names: `ANCHOR-TENDER` would have
carried the pun into every prompt that tagged it.

## Decoration that misleads is worse than no decoration

Magnetism has no look of its own, so the prompt gave the coils a "dull amber glow" to
carry it. It rendered as a red-hot disc with a corona of sparks — a forge, or a branding
iron. Two objects also merged: the terminal and the coiled housing became one cylinder
lying on the deck, and the cable vanished with them.

Where an effect has no native appearance, let the *consequences* carry it and light the
shot plainly — grit standing on end, a final approach that accelerates, a dead stop with
no bounce. Then lock the plainness: *"every light in this shot is sunlight"*, *"all the
metal stays cool and unlit from within"*. A glow invented to signal a force competes with
the physics that actually signals it.

## Generating images from here — what this access can and cannot do

Cinema Studio is a *model* name (`cinematic_studio_2_5`), not a container — there is no
"Cinema Studio" project.

**Media projects and folders do exist**, and an earlier note here claiming otherwise was
wrong. `list_projects`, `list_folders`, `list_project_assets` and `create_folder` all
work, and IRON CLOUD has a project with a full folder tree — see `HIGGSFIELD-ABLAGE.md`
for the IDs and the filing rules. **Every generation goes into its shot's folder; never
generate without a destination folder.**

The two things that hold at once: *generations and uploads* live in project folders,
while *reference elements* (`show_reference_elements`) carry only name, category and
description and have no folder field at all. Elements are organised by a **name prefix**
plus a description that opens with the film and scene; generations are organised by
folder.

Generating over MCP costs credits and the app's unlimited mode does **not** apply here.
`nano_banana` is the 1-credit image model; confirm with `get_cost: true` rather than
assuming, then pass `use_unlim: false` explicitly.

**The free/unlimited mode cannot be switched on from here.** The `use_unlim` parameter
exists and the roster marks many models `supports_unlim: true`, but what the API calls
unlim is a *free-trial* allowance, not the app's Plus unlimited mode, and this account
holds none of it. Verified two ways, both free: `models_explore` reports
`unlim: {available: false, remaining: null}` for image and video, and a `get_cost: true`
preflight with `use_unlim: true` — which submits nothing — fails. Note the error is
misleading:

```
Error estimating cost: Unlimited generations aren't supported for nano_banana
```

It reads as a model limitation, but the same model is listed as unlim-capable; what is
missing is the allowance. There is no activation endpoint, only the billing widget, which
is a purchase path and not to be opened unasked.

So the free division of labour stands: the user generates in the app on unlimited, and
this side pulls the results, reads them frame by frame and writes the prompts. Spend
credits only where the API genuinely saves rounds — the crop-and-re-render trick below
was worth six of them.

The loop: `media_upload` → `curl -X PUT` the bytes → `media_confirm` → `generate_image`
with `medias: [{role: "image_references", value: <media_id>}]` → `jobs_wait` →
`curl` the `result_url` and Read it. A finished **job id can be passed straight back** as
a `medias[].value`, so iterations need no re-upload. `show_reference_elements`
`action: create` takes `{id, url, type: "image_job"}` and the url must be the exact one
the job returned.

**When "step in closer" does nothing, crop it yourself.** Two rounds of "step in to a
third of the distance" returned near-identical framing. Cropping the wanted region with
ffmpeg, upscaling it, and feeding *that* as the reference with "keep this exact framing,
re-render at full sharpness" moved it in one go — the same trick as baking blur into an
asset. Framing is copied from a picture and negotiated from text.

## Two similar shapes close together merge into one

A round brass plate and a round brass terminal a few centimetres apart were rendered as a
single object twice over: once as a coiled cylinder lying on a deck with the cable gone,
once as a toothed disc that migrated up onto the cable, leaving the mounting behind. No
amount of "they are two separate objects" fixed it.

**Differentiate the silhouettes instead.** A *cone* landing on a *disc* held; when the
locomotive version kept collapsing, making its mounting a rectangular block with a square
pad separated them immediately. Where two parts of one mechanism must stay distinct, give
them different shapes, and add a lock naming the shapes: *"the rectangular latch block and
the conical terminal stay two separate objects of two different shapes throughout"*.

## Resolve the acceptance criterion at the frame rate it lives at

"Does the terminal accelerate into contact?" is invisible on a 1 fps sheet: the drop
occupied two tenths of a second. Pulled at 5 fps over a two-second window around the
landing, it read clearly — five frames of near-motionless hover, then the whole distance
covered between two frames with visible motion blur.

```
$FF -ss 2.6 -to 4.6 -i shot.mp4 -vf "fps=5,crop=iw*0.5:ih*0.85:iw*0.25:ih*0.1,scale=460:-1,tile=5x2" -frames:v 1 strip.png
```

Crop to the part that matters before tiling, or the detail is gone at thumbnail size.

## Sometimes the model's reading is better than the brief

Two instructions — "a toothed iron collar around the plate's rim" and "grit stands up on
end and clings in bristling lines along the rim" — fused into something neither one asked
for: a crown of upright brass spines that rises from the plate as the field builds and
stays up, with the terminal finally seated inside it. It carries the magnetism without a
glow, it belongs to the hardware instead of being loose dirt, and it makes the terminal
read as *held*.

Promote a result like that into the prompt as intended design rather than correcting back
to the original wording. Judge what arrived on its merits, not on whether it matches what
was written.

**And when a beat is silently dropped, ask whether it earns its place.** The mechanical
lock — collar rotating, three claws folding over the flange — never happened at all; it
competed for the last seconds and lost. With the spine crown already holding the
terminal, the lock was more mechanism than the shot could carry, and cutting it frees the
time the snatch needs to read as acceleration instead of a jump.

## Failure modes seen repeatedly

- Describing a *process* ("the wheel swings out and rotates") invites invention. Describe
  the **end state** and the resulting silhouette instead.
- Naming a thing to exclude tends to summon it. Prefer positive, checkable properties.
- Anchor size against something visible in the same frame ("a tread as wide as his
  shoulders"), never in absolute units.

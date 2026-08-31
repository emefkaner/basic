# Prompting notes — Higgsfield / IRON CLOUD

Hard-won rules from working on this film. Apply these before writing any new prompt.

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
- **Not the pixels.** The CDN host is blocked by this environment's network policy, so
  the images themselves cannot be opened. Reason from names and descriptions, and say
  plainly that the picture itself was not seen. Never describe an image as if it had been.

**Check the element description against the blocking before generating.** An environment
element fixes look direction and which side of frame the track sits on. If the prompt
puts the camera on the other side, the shot comes back mirrored and no amount of
no-mirroring wording fixes it — the element is the one telling the truth.

## Failure modes seen repeatedly

- Describing a *process* ("the wheel swings out and rotates") invites invention. Describe
  the **end state** and the resulting silhouette instead.
- Naming a thing to exclude tends to summon it. Prefer positive, checkable properties.
- Anchor size against something visible in the same frame ("a tread as wide as his
  shoulders"), never in absolute units.

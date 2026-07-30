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

## Failure modes seen repeatedly

- Describing a *process* ("the wheel swings out and rotates") invites invention. Describe
  the **end state** and the resulting silhouette instead.
- Naming a thing to exclude tends to summon it. Prefer positive, checkable properties.
- Anchor size against something visible in the same frame ("a tread as wide as his
  shoulders"), never in absolute units.

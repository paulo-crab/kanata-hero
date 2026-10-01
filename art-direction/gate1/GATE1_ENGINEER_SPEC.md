# Engineer — Gate 1 specification

**Status:** APPROVED by the player on 2026-10-02 (STYLE_BIBLE §8). The Director decisions below are now canon for the Engineer, and production may expand to the remaining walk directions and the rest of the cast.

**Sources:** STYLE_BIBLE §3–8, ART_BRIEF, `design/characters/engineer.md`, `design/characters/README.md`, `docs/game-design.md` "Camera, scale, and sprite rules" and "Characters and UI", `levels.md` cast table. Where this file says **Director decision**, the decision was made under the art-direction authority the player delegated on 2026-10-01. It can be revised at the gate.

## Deliverables

| File | What it is |
| --- | --- |
| `engineer_sprites.py` | The frames as hand-placed 16×24 key grids plus the palette. This is the source of truth for the pixels. |
| `gate1-scene-1366x768.png` | The review still: the 320×180 Orientation scene at ×4, keyboard inset open |
| `gate1-walk-1366x768.gif` | The same scene animated: two east walk cycles along the route, then each idle facing (E, S, W, N) |
| `gate1-sheet.png` | Every frame at ×8 (diagnosis), ×2 and ×1, with the anchor marked |
| `engineer-atlas.png` / `.json` | Native atlas and metadata: frame size, anchor, footprint, timing |
| `engineer-walks.gif` | All four walk cycles looping at ×6 (S, N and W were added after the gate on 2026-10-02 under the same contract) |
| `build_gate1.py` / `check_gate1.py` | Rebuild the outputs / run the objective checks |

## Base character specification (fixed)

| Property | Rule | Source |
| --- | --- | --- |
| Frame | 16×24 logical px, one-cell footprint | STYLE_BIBLE §4 |
| Anchor | `feet_bc` is the pixel edge between columns 7 and 8, under row 23. The planted foot rests on row 23. The unweighted foot may sit 1 px higher, on row 22. | §5 contract. The 1 px allowance is a Director decision that reconciles engineer.md's "feet offset by about 1 px". |
| Proportions | Head plus hair: rows 0–9 (10 px), about 10 px wide including the outline. Torso: rows 10–16. Legs and feet: rows 17–23. | §5 checks |
| Silhouette | Asymmetric stance. Arms marked off from the torso by a dark jacket-seam run (`#1B4450`) on rows 11–14, broken only where the S badge sits. Hands at rows 15–16. Walk contact strides stay inside columns 2–14, so the walk reads overhead, not side-view. | engineer.md "Sprite" |
| Hair sweep | Fixed to the character's own left: screen-right facing S, screen-left facing N, a forelock at the front of the head facing E and W. | Director decision |
| Badge | 1×2 px brass badge plus a 1 px lanyard on the character's left chest. Visible facing S, a sliver facing W, hidden facing N and E. The sprite must read without it. | engineer.md, plus a Director decision on visibility |
| Face | S: two eye pixels and a hair-shadow line. E and W: one eye pixel and a forehead shadow. N: no face, only the nape. No mouth, brows or cheeks. | §5 |
| Facings | S, N, E, W, each drawn separately. E and W are not mirrors. | characters README |
| Idle | 2 frames × 500 ms. Frame 1 lowers the head and torso by 1 px. The feet and anchor never move. | §5 contract. The motion content is a Director decision. |
| Walk (Gate 1) | East only. 4 frames × 133 ms. Contacts on frames 0 and 2, with the body 1 px lower. Passing poses on frames 1 and 3. The arms swing against the legs. The walk moves 8 px per frame, so 2 cells per cycle. Some foot slide is accepted. | §5 contract. The contact, bob and slide rules are Director decisions. |
| Contact shadow | Drawn by the renderer at the anchor, never baked into frames. Palette pixels only: row 23 is `#535971` with a `#343650` core 8 px wide, and the row below is 10 px of `#535971`. | §7 and README. The shape is a Director decision that replaces scale-test's 50 % blend. |

## Rendering

- **Palette:** only the ramps in `engineer_sprites.PAL`, which are the engineer.md defaults, plus outline `#202337`. No blended or antialiased pixels.
- **Tones:** each part fills with 2–3 steps of its ramp. The darkest step appears only on contour swaps and occlusion edges. This is a Director decision that reconciles "2–3 tones per part" with the 4-step ramps.
- **Outline:** `#202337` by default. Lit top and left edges swap to the part's own dark tone: hair `#2B1E26`, jacket `#1B4450`.
- **Light:** from the upper left in screen space for every facing. Hair highlight `#93603F` upper left, jacket highlight `#7CCFC2` on the left shoulder, shadow on the lower right.

## Customization specification

| Slot | Keys swapped | Rule |
| --- | --- | --- |
| Skin | `k l m n` | Full 4-step ramp swap. Each ramp must keep face/hair separation at 1× and differ from Ivo's and Mira's ramps. |
| Hair | `A B C D` | Colour only. Shape variants are forbidden until engineer.md open question 2 is decided (Director decision). |
| Jacket | `p q r s` | Never violet and never a UI marker hex. Any step with a hue of 160°–200° must be at or below 60 % HSL saturation (§3). |
| Trousers | `O P Q` | Same marker rules. |

The key layout, silhouette, anchor, timing and shadow never change with customization. `check_gate1.py` enforces the frame, row-23, anchor-balance, marker, violet and teal-saturation rules.

## Scene (Gate 1 composition)

This is the scale-test Orientation layout at 16 px and ×4 on 1366×768 (1280×720 letterboxed). The Engineer stands, then walks, on a **lit two-cell route**. The route runs between the east desk's chair and the bench, ending at the **Records door** in the east wall. The door has jambs, parked glass leaves and a brass threshold, and the floor brightens in steps as it nears the door. The **terminal** is the printer and its teal marker. The **NPC** is Ivo with a talk marker. The **keyboard inset** is open and teaches Caps + L → Right arrow → Step east, which is the step shown in the walk. The room itself is redrawn in `environment.py` to the finish of reference 08, using palette pixels only (audited: zero off-palette colours). It has running-bond stone slabs, a filled inlay band around the garden ring, wall caps with lit glass trim, and glass bays with stepped reflections. The Records door is a sliding glass door in a brass frame in the east wall. Its two framed panels meet at a centre seam and slide into pockets behind the jambs. It is shown closed in the still and slides open over the last four walk frames in the GIF. Records' sea-blue floor and a filing cabinet show through the glass. A folder sign sits on the lintel with a lamp on each side, and the brass mat in front carries inlaid RECORDS lettering and an arrow pointing at the door. The garden landmark has a stone rim, tree, stream, rocks and edge flowers, with three lamps; the fourth corner sits under the inset and is omitted. The room is also dressed with slate planters, desks with monitors and chairs, a bench, a sofa and a side table, all kept off the route. Ivo and Mira now use their approved cast sprites (`art-direction/cast/`). The 32 px comparison is retired and not rebuilt.

## Acceptance criteria

Review history: specialist reviews (character, technical, style), then continuity validation cycle 1 (FAIL with 7 fixable defects), then all fixed in cycle 2. GIF frame delays round to 130 ms because GIF stores centiseconds. The atlas metadata carries the exact 133 ms.

Automated (`check_gate1.py`):
- [x] All 12 frames are exactly 16×24
- [x] Every frame has a pixel on row 23
- [x] Opaque mass on either side of the 7|8 anchor is within 20 %
- [x] No UI marker hex and no violet on the person
- [x] Every teal-hued jacket step is at or below 60 % saturation
- [x] Head rows 0–9 use only hair, skin and outline keys
- [x] The darkest hair step never appears as an interior fill

Coordinator review of the renders:
- [x] Four distinct facings with consistent head and torso volume. E and W are drawn separately.
- [x] Not a front-facing icon: the asymmetric stance, sweep and badge side hold across facings
- [x] Reads at native 1× on `#E6D3B3` and `#F0DEC0` through the outline (gate1-sheet.png)
- [x] Hard pixels only. Selective outline with no unbroken ring of pure ink on the lit sides.
- [x] Scene contains a door, terminal, NPC, two-cell route and open inset, with the Engineer clear of the inset and HUD

Player gate (STYLE_BIBLE §8):
- [x] Silhouette, expression, material separation, floor contact and interaction contrast judged against references 02, 04, 07 and 08
- [x] Route and door readable (sliding glass door, lit RECORDS mat)
- [x] Player approval recorded in `design/characters/engineer.md` and the README decisions log (2026-10-02)

## Generation prompt (for any re-draw by an external pixel artist or image model)

> Original pixel-art game sprite sheet of an office software engineer for an overhead, orthographic, high three-quarter view adventure game. Each frame is exactly 16×24 pixels on a transparent background, with hard square pixels: no antialiasing, gradients, blur, dithering or painterly shading. Feet rest on the bottom row, centred on the boundary between pixel columns 7 and 8. One leg carries the weight and the other foot sits 1 pixel higher. Proportions: head with hair about 10×10 pixels, torso 7 rows, legs and feet 7 rows, arms separated from the torso by a dark seam. Short brown hair with a visible crown and a swept top that lifts toward the character's own left. Warm medium-brown skin. Muted teal jacket with a small pale V collar. Navy trousers and terracotta-brown shoes. A tiny 1×2 pixel brass badge on a 1 pixel lanyard on the left chest. Face: two dark eye pixels under a one-row hair shadow, with no mouth. Exact colours only. Hair #4A2E2E #6E4434 #93603F with #2B1E26 on contours. Skin #9C6448 #C98B62 #E8B184 with #6E4433 on contours. Jacket #25707A #3A9C9C #7CCFC2 with #1B4450 on contours. Collar #E2D6C2 #F4F2EC. Trousers #2C3352 #3E4870. Shoes #523D4C #85565A #BA785F. Badge #705056 #AC7655 #E1AC62. Outline #202337, swapped for each part's own darkest tone on edges lit from the upper left. Light from the upper left on every frame. Frames: idle facing down (2 frames, the second lowering head and torso by 1 pixel; two eye pixels; badge and lanyard visible); idle facing up (back of head, no face, badge hidden); idle facing right and idle facing left, drawn separately, not mirrored, each with one eye pixel (facing left shows a 1×2 badge sliver and lanyard pixel; facing right hides the badge); and a 4-frame walk facing right (contact, passing, contact, passing, body 1 pixel lower on contacts, arms swinging against the legs). Walk strides stay compact (feet no more than about 10 pixels apart) so the walk reads from a high overhead camera. No shadow in the frames, no background, no text, no other characters, no weapons or props, and no side-scroller or isometric perspective.

Use this prompt only to request a re-draw. `engineer_sprites.py` remains the pixel source of truth.

## Extra animation sets (approved by the director 2026-10-02)

**Status:** Candidate, pending director review. Tasks 8.1, 8.2 and 8.4. The approved idle and walk frames are unchanged (verified by dump and diff). The new frames live in `engineer_sprites.EXTRA`, built from the idle frames plus hand-placed stamps.

**Format (shared by every character).** `EXTRA[set][key] = [frames]`, `EXTRA_MS[set] = ms per frame`, optional `EXTRA_MODE[set]` (`"once"` = play, then hold the last frame; `"loop"`), optional `EXTRA_ASYMMETRIC` (sets whose arm moves mass off the anchor). Keys are facings `s n e w`; the `turn` set uses adjacent pairs `se en nw ws`. Frames are 16×24 with the approved anchor. `build_cast.py engineer` writes `engineer-full-atlas.png/.json` (idle and walk rows 0-7, then one extra row per set and key, named `engineer_<set>_<key>`), `engineer-full-sheet.png` and `engineer-extra.gif` into this folder. The approved `engineer-atlas.*` is still built by `build_gate1.py`.

| Set | Facings | Frames | ms per frame | Mode | Pose |
| --- | --- | --- | --- | --- | --- |
| `interact` | S N E W | 2 (reach, hold) | 250 | once | S: hands meet at the belt. N: left arm reaches up past the shoulder. E and W: the near forearm extends, hand half out, then fully out |
| `react_concerned` | S N E W | 3 (N: 2) | 300 | once | Head bows onto the shoulders; S, E and W add an outlined fist at the chin; the last frame sags 1 px |
| `react_satisfied` | S N E W | 3 | 300 | once | S, E, W: fist pump (hands on hips first for S), then settle with a 1 px breath. N: hands on hips, breath |
| `turn` | se en nw ws | 1 each | 60 | once | In-between frame: the head of the facing the turn is heading toward, on the old body |

**Director decisions**

1. **Extras are idle frames plus stamps.** Reason: no approved pixel can drift, and each pose stays a small reviewable key grid.
2. **Check rules.** Every extra frame passes the idle rules (size, row 23, head keys, darkest hair step, marker and violet). The stride-edge rule stays walk-only. `interact` and `react_satisfied` are in `EXTRA_ASYMMETRIC`, which relaxes the anchor-mass tolerance from 20% to 30%, because a raised or reaching arm legitimately moves mass. Reason: the arm is the point of the pose.
3. **No mouth or brow for any reaction.** Expression comes from pose (bowed head, fist at the chin, fist pump), per STYLE_BIBLE §5.
4. **Reaction mode.** Reactions play once and hold the last frame until the scene ends, then return to idle. Reason: dialogue length is unknown.
5. **Quick turn.** One 60 ms in-between frame per adjacent pair, so S→E→N costs 120 ms. The same frame serves both directions of a pair. A 180° turn plays through one side. Reason: STYLE_BIBLE and the game spec ask for an immediate response to Caps+H/J/K/L. The GIF holds each facing 400 ms around the transition so the 60 ms is visible, and the build check confirms that every GIF delay equals the specified ms (60, 250, 300, 400).
6. **Engineer atlas ownership.** `build_gate1.py` still writes the approved atlas. `engineer-full-*` is the superset until `build_gate1.py` is changed to call the same writer.

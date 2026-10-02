# Noor — sprite specification (idle ×4, walk ×4)

**Status:** Approved by the director 2026-10-02.

> **Rich finish (2026-10-02):** the outline colour is now `#0E1020` and the ink shoe ramp and renderer shadow move to the deeper ink ramp (`#1C2038` `#3A4160` `#6A7392`). Clothing, skin and hair ramps in this spec stay as approved. The sprites are queued for that recolour (OpenSpec change `adopt-rich-finish`); see `../rich-finish/RICH_FINISH_SPEC.md`.

**Sources:** `design/characters/noor.md`, `design/characters/README.md`, `levels.md` cast table and Records row (levels 07–11), STYLE_BIBLE §3–7, `palettes/PALETTES_SPEC.md` (Noor's skin and hair ramps). Every shared person rule follows the approved Gate 1 contract in [GATE1_ENGINEER_SPEC.md](../gate1/GATE1_ENGINEER_SPEC.md) and the cast frame rule in [IVO_SPEC.md](IVO_SPEC.md): frame, anchor, idle and walk timing, contour-only darkest step, renderer-drawn shadow. **Director decision** marks choices made under the art-direction authority the player delegated.

## Deliverables

| File | What it is |
| --- | --- |
| `noor_sprites.py` | Hand-placed 16×24 key grids and the palette. This is the pixel source of truth. Skin and hair are imported from `CAST_RAMPS["noor"]`, never retyped. |
| `noor-sheet.png` | All 24 frames at ×8, ×2 and ×1, with the anchor marked |
| `noor-walks.gif` | The four walk cycles looping at ×6 |
| `noor-atlas.png` / `.json` | Native atlas. Rows S N E W idle, then S N E W walk. |
| `build_noor_room.py` → `noor-in-records.png` | The review room recoloured to the Records palette at ×4 (1280×720). Noor walking east toward the Engineer, Noor idle S beside him for scale, then idle N E W and walk frames S N W on the open floor. |

Rebuild with `python3 build_cast.py noor` and `python3 build_noor_room.py`. Check with `python3 ../gate1/check_gate1.py noor_sprites`. Extra sets (interact and stamp-down, step out from behind the desk, reactions, posture states) are left out of this round.

## Silhouette (how Noor differs from the Engineer, Ivo and Mira at 1×)

| | Engineer | Ivo | Mira | Noor |
| --- | --- | --- | --- | --- |
| Shoulders, S and N | 12 px | 14 px | 12 px plus bag | **10 px** (columns 3–12), the narrowest in the cast |
| Torso in E and W | 10 px | about 10 px | about 10 px | **8 px** (columns 4–11) |
| Taper | jacket to legs | trapezoid | asymmetric panels | none: a straight column from shoulder to hip |
| Trousers | rows 17–23 (7) | rows 18–23 | rows 17–23 | **rows 16–23 (8)**: the shirt ends at row 15, so the legs are the longest |
| Hair | brown, swept, forelock | silver cap | plum puff | blue-black short swept crop: two crown tufts with a notch between, light strand clusters across the crown, a stepped hairline, ears and a tapered, uneven nape |
| Shirt | teal jacket | terracotta cardigan | two-panel jacket | pale grey-oatmeal linen shirt, rolled sleeves (cuff roll, then skin forearm) |
| Props | badge | tablet | bag and strap | a dark **cherry-wood stamp** (T/mushroom, lit knob, dark ink plate) at the left hip and a pale **flat coral file folder with tabs and label** at the right |

## Director decisions

1. **Frame.** Everything stays inside 16×24 (cast frame rule). The stamp is held against the front of the body at the hip, and the folder is carried tight to the side (columns 1–3 in S and E). The 2×2 cherry cluster of noor.md became a 5×6 stamp because a 2×2 cluster cannot show a knob, a neck and a plate.
2. **Tall within the frame.** Height comes from narrow shoulders, no taper, a visible 1 px neck row and 8 rows of trousers. The head is 9 rows plus a 1 px crown tuft, and it never exceeds the frame. This follows noor.md "Sprite (16×24)".
3. **Grey-oatmeal linen shirt (closes noor.md open question 2, shirt part; revised after the first review).** The first ramp (`#B8A68C` mid) matched her skin (`#C1A56E`) and her torso read as bare skin. The ramp is now `#8A8985` `#C9C7BF` `#DAD8D0` `#EFEFEC`: hue 48°, saturation 2 / 8 / 12 / 10 %, lightness 59 / 79 / 86 / 94 L*, all lighter than her lightest touching skin, with the darkest step `p` only on seams and the neck line. Measured ΔL* between each shirt step and the skin step it touches in any of the 24 frames: p–k 19, p–m 12, q–k 42, q–l 25, q–m 11.2, r–k 48, r–l 31, r–m 17, s–k 56, s–m 25. The minimum is **11.2** (rule: at least 10). A dark `p` line flanks the neck at the collar in S, E and W. Against the Records floor `#BCD0D4`, body pixels at 3:1 are 60 % in S, 64 % in E, 61 % in N and 64 % in W (rule: at least 45 %; the pale shirt is not part of that count, her hair, trousers, shoes and stamp are). The `#202337` outline is 9.7:1. Nothing is within dE 40 of a UI marker.
4. **Sea-blue trousers.** `#2A4A60` `#3F7388`, hue 197–204°, saturation at most 39 %, so inside the teal rule. They stay distinct from the Records shelving because the shelves are never beside her feet and the shoes break the read.
5. **Dark cherry shoes.** `#47202F` `#7B3442` `#A94C47` from the Records wood ramp, so her feet echo the stamp and no cast member shares them.
6. **Hair (revised).** A short swept crop in the fixed ramp (`#121929` `#102A3E` `#29425A` `#436687`). The silhouette is broken by two crown tufts of different sizes with an outline notch between them (all four facings), a stepped hairline in `A`, and in S a 2 px lock on the left. Light strand clusters of `D` run across the crown from the upper left, with `B` shading only the far side. In N the hair tapers (full width at the crown, narrower at the ears), both ears show, and the hem over the nape is uneven. `A` is never fill. A flat rim was not used.
7. **Hair/skin separation.** The ramp gap is narrow (13 L*), so a skin `k` or ink pixel always sits where light hair meets skin, and `A` marks the hairline above the forehead. `HAIR_SKIN_SEPARATED = True`, and `check_gate1.py` enforces it.
8. **Rolled sleeves.** The sleeve is the linen ramp, a lighter `s` cuff roll is the 1 px value break, and the forearm below it is skin (`m` lit, `l` shaded). In E and W the roll sits at mid-forearm.
9. **Stamp (revised).** Always in her left hand and the darkest prop. A T/mushroom: a lit cherry knob (`z` glint 1 px, `y` face, `x` shade), a narrow neck gripped by her fist, and a flat plate in the dark `x` / `w` steps. S at the screen-right hip, E and W at the leading edge, N half behind the hip with the fist showing. It has no halo and uses nothing from the gold ramp.
10. **File folder (revised).** The lightest prop: a flat 4×7 rectangle with a pale `#F4B1A4` face, a `#D4606A` edge, two sea-blue tabs on the top edge and a sea-blue label. It is carried at her right: S screen-left, N screen-right, E trailing and W trailing. Exactly one prop per facing is partly hidden behind the body: the folder in S, E and W, the stamp in N. `GLINT_LIMITS`: `z` 1, `J` 3, `f` 8. The smallest distance from `#D4606A` to the coral marker is dE 12.7.
11. **Walk and bob.** The shared timing and leg poses (4 × 133 ms, contacts on frames 0 and 2 lowered 1 px, `eng.lower` dropping row 17) and the idle settle (2 × 500 ms). Her hands are full, so neither arm swings. The props move down with the body as one piece. The side-walk stride stays inside columns 2–13 as the Gate 1 overhead limit requires.
12. **Not drawn here.** The stoop-to-upright posture states, the stamp-down interact, stepping out from behind the desk and the two reactions come with the EXTRA pass. The base set is the upright stance. Pronouns stay open (they/them in prose), and the sprites do not depend on them.
13. **Records room render.** `build_noor_room.py` reuses `palette_swap` from `build_palettes.py` without editing it. It draws the review room's floor, route, walls, printer, desk, counter and plants, but not the Orientation garden, so the floor is open for a row of facings. People are placed after the swap, so they keep their own palettes. The Engineer stands on the route beside Noor for scale.

## Acceptance criteria

Automated (`check_gate1.py noor_sprites`):
- [x] 24 frames, each 16×24, with a pixel on row 23 and mass within 20 % across the 7|8 anchor
- [x] No UI marker hex and no violet. Teal-hued steps at or below 60 % saturation.
- [x] Head rows use only hair, skin and outline keys
- [x] The darkest hair step appears only on contour, hairline and lock edges
- [x] Light hair never touches light skin
- [x] Glint limits (`z` 1, `f` 1, `J` 2) and the walk stride edge

Coordinator review (the self-review of this candidate):
- [x] Reads as a different person from the Engineer, Ivo and Mira at 1×: narrow column, long legs, linen shirt with rolled sleeves, blue-black crop, coral folder and cherry stamp
- [x] Stamp (dark, T-shaped) and folder (pale, flat, tabbed) read as two different objects at ×4 in the Records room, not two red mitts
- [x] Legible against the Records floor: 60–64 % of body pixels at 3:1 and a 9.7:1 outline. The shirt separates from the skin (min ΔL* 11.2).
- [x] Hair is not a helmet: two tufts with a notch, light strand clusters, a stepped hairline, ears and a tapered nape
- [x] Director: confirm the revised shirt, hair and props

## Extra animation sets (approved by the director 2026-10-02)

Tasks 8.1 (interact) and 8.2 (reactions), plus the posture change from noor.md. Same format as the Engineer, Ivo, Mira and Vale: `EXTRA`, `EXTRA_MS`, `EXTRA_MODE` and `EXTRA_ASYMMETRIC` in `noor_sprites.py`. Frames are the raw (propless) grids with the head moved by `eng.dip` or `eng.tilt`, and the stamp and folder painted afterwards by `finish_x`, so the props never deform. `IDLE`, `WALK` and `PAL` are unchanged (dumped and compared before and after: identical). `build_cast.py noor` adds `noor-extra.gif`, rows 8–19 of `noor-atlas.png`/`.json` and the extra frames on `noor-sheet.png`. `check_gate1.py noor_sprites`: 68 frames checked (24 base + 44 extra), 0 failures.

| Set | Facings | Frames | Timing | Mode |
| --- | --- | --- | --- | --- |
| `interact` | S N E W | 2 | 250 ms | once, hold last |
| `react_unimpressed` | S N E W | 3 | 300 ms | once, hold last |
| `react_satisfied` | S N E W | 3 | 300 ms | once, hold last |
| `posture_upright` | S N E W | 3 | 300 ms | once, hold last |

### Extra decisions

14. **Interact: the stamp-down (level 08).** Frame 0 raises the stamp 1 px (the head rows above it must stay hair and skin, so the raise is small); frame 1 settles the body 1 px and presses the stamp 3 px down, so the plate lands over the hip. The props use their idle art and side rules. `EXTRA_ASYMMETRIC` includes `interact`.
15. **Reaction (a): dry, unimpressed.** The head tilts 1 px (toward the facing's left, away on W), then bows a notch under a heavy lid (one `k` pixel on the forehead row above the eye, S, E and W), then the figure settles 1 px. N only tilts and bows, because it has no face.
16. **Reaction (b): quiet satisfaction.** A small nod (`dip`), the stamp lifts 1 px in a short flourish, and the figure settles. The last frame equals idle frame 1.
17. **Posture: stooped to upright.** The base idle is the upright pose. The set starts stooped (head 2 px down, torso 1 px down), rises to a 1 px stoop, and ends on idle frame 0. The engine plays it once per cabinet step and holds the final frame (cast table "straightens as the cabinets open").
18. **Held frames.** Every set ends on a valid resting pose (idle 0 or idle 1) for the engine to hold until the dialogue closes.
19. **Open.** The "step out from behind the desk" move (level 07) is a scripted walk and needs no pixels of its own. The stamp mark (rejected to accepted) is a world prop, not a sprite change.

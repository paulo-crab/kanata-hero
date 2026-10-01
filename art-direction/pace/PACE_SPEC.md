# Pace — wayfinding signage specification

**Status:** Approved by the director 2026-10-02.

**Sources:** `design/characters/pace.md`, `levels.md` (story, cast table), STYLE_BIBLE §3, §6, §7, `gate1/environment.py` (the RECORDS mat and the garden ring squares). **Director decision** marks choices made under the art-direction authority.

Pace is the campus performance system: signage and small UI copy only. It has **no body sprite, no face and no portrait**. This set is its in-world signage, built as environment pieces on the 16 px grid.

## Deliverables

| File | What it is |
| --- | --- |
| `pace_art.py` | Palette keys (`PAL`), the two hand-placed icon key grids, and the drawing functions for every piece. This is the pixel source of truth. |
| `check_pace.py` | On-grid sizes, palette-only colours, no marker hex, no violet, glint limits, contour-only edges, lit-glass share, floor-glyph contrast, and an atlas-versus-source comparison |
| `build_pace.py` | Writes the sheet, the atlas and the in-room renders |
| `pace-sheet.png` | Every piece at ×8 (16 px cell lines), ×2 and ×1 on its wall or floor background |
| `pace-atlas.png` / `.json` | Packed native atlas. Per entry: rect, footprint cells, `origin_px`, anchor, draw layer, collision cells, state, baked shadow. |
| `pace-in-room-1366x768.png` | The approved review room at ×4 with the signage placed (and `-native.png` at 320×180) |

Rebuild: `python3 build_pace.py`. Check: `python3 check_pace.py` (run from this folder, with Pillow and numpy).

## The set

| Piece | Size | Layer | Notes |
| --- | --- | --- | --- |
| `pace_icon_16` | 16×16 | wall | The icon: stone ring, blue-glass screen, three cream horizontal bars and a route chevron |
| `pace_icon_8` | 8×8 | wall | Small variant: the three bars only. Used inside signs. |
| `pace_logo_plate_1x1` | 16×16 | wall | Icon on a small framed plate, cast shadow on the wall |
| `pace_wall_sign_2x1` (+ `_repeat`, `_optional`) | 32×16 | wall | Icon and three orderly bars on a lit face, brass screws, 2-row wall cast |
| `pace_hanging_sign` | 16×24 | wall | Wall rail, two brass chains, the 16×16 icon as the plate |
| `pace_floor_chevron_{e,n,w,s}` | 16×16 | floor-marking | A 12×12 bevelled slab (the garden ring's corner-square language) with one chevron, for repeating along corridors |
| `pace_floor_arrow_{e,w}` / `_{n,s}` | 32×16 / 16×32 | floor-marking | Slab with the 8×8 icon at the tail and a shaft-and-head arrow (2 px shaft, 4-column head, as on the RECORDS mat) |
| `pace_directory` (+ `_repeat`, `_optional`) | 32×32 | rear-prop | Standing board on two legs; ground footprint is the bottom 2×1 cells, both blocked |

Placement rule: sprite top-left = footprint cell top-left minus `origin_px`. Walls and the directory have their contact shadow baked, like `environment.py`'s props. Floor markings have none.

## Colour

Ramps used (all from STYLE_BIBLE §3): ink `#202337 #343650 #535971 #777A8C`; warm stone `#665D65 #968A85 #C7B7A0 #F0DEC0`; blue glass `#203A50 #366479 #5AA3AE`; brass `#705056 #AC7655` as trim, and `#E1AC62` on three pixels of a directory. Glass steps have 34–43% HSL saturation (the terminal teal is about 75%). Unused on purpose: `#A0DDD4` and `#F5D580`, the glint steps. No violet, coral or gold marker hex anywhere.

## Director decisions

1. **Pace stays signage only.** The brief confirms no body and no portrait; this set adds no character art.
2. **Icon shape (closes pace.md open question 1).** A rounded badge with three horizontal bars of different lengths and a route chevron. It has no eyes or mouth: the bars sit left, the chevron right, and no pair of dots exists. The 8×8 drops the chevron.
3. **Colour (closes the assumption in pace.md).** Stone ring and ink frames, a `#366479` screen with one `#5AA3AE` lit row, cream bars. The brief's assumed ink, stone and glass values are all used, taken from the real ramps.
4. **No teal-glow look.** The lit glass step is at most 15% of any piece, has no halo, and every pixel touching transparency is a contour step (the checker enforces both). Signs are lit faces in frames, not emissive devices.
5. **Signage is not a marker.** The icon is a framed rectangle with bars, never a bubble, diamond or glitch shape, and no sign uses coral, gold or violet. The RECORDS mat stays the brightest floor in the room.
6. **Floor language.** The floor pieces are bevelled stone slabs let into the floor, like the ring corner squares, with an inlaid glass glyph. The arrow keeps the mat's proportions (2 px shaft, head) but is stone and blue rather than a brass rug, so it reads as quieter guidance beside the mat.
7. **Repetition shows visually (closes pace.md open question 2).** The `repeat` state sets all three bars to one length (wall sign) and every directory entry to one length. Later states can show copy repeating in DOM text. Pace never changes its icon.
8. **Epilogue.** The `optional` state is an unlit stone plaque with ink bars and an ink icon: the sign remains but reads as optional guidance.
9. **Grid.** Every piece is a multiple of 8 px, as the 16×24 person frame is; floor markings are whole cells. The only 8×8 piece is the icon variant.
10. **No lettering on Pace's signs.** Bars stand in for copy. Place names keep using the RECORDS mat's 3×5 glyphs, and any real Pace copy is crisp DOM text, never a pixel font for body text (pace.md "Where it appears").
11. **Placement in the review room.**
    - The north wall is all glass bays, and the HUD and Ivo's marker cover its left half, so the wall plate goes on the east wall below the Records door, right of the lamp.
    - The hanging sign has no clear bay and is shown on the sheet and in the atlas only.
    - The floor arrow plate sits on the route at x=224, y=83, ahead of the RECORDS mat. It never touches the two-cell route's edge lines or the door.
    - The directory stands at x=210, y=42, north of the route's top inlay line, clear of the printer marker, Ivo's marker and the desk.
    - The chevrons are not placed: they would sit under the Engineer's start position, and the plate already points the way.
12. **Hooks, not edits.** `build_pace.py` wraps `environment.east_wall`, `route` and `garden` for the render so each piece lands on its layer before the actors. `environment.py` and `build_gate1.py` are untouched.

## Acceptance criteria

Automated (`check_pace.py`): 18 pieces, 0 failures.
- [x] Sizes on the 8 px grid, floor markings whole cells, footprint matches the sprite
- [x] Palette-only colours, hard alpha, no marker hex, no violet
- [x] Glint steps unused (limits: `#F5D580` 3 px, `#A0DDD4` 4 px)
- [x] Lit glass at most 15% of a piece; edges are contour steps only
- [x] Floor glyph contrast at least 3:1 on the slab
- [x] Atlas pixels equal a rebuild of the source

Coordinator review (to be completed by the director):
- [x] Icon reads as a wayfinding badge at 1×, with no face
- [x] Wall plate, floor plate and directory read as signs in the room at ×4, not as interaction markers
- [x] Route, Records door and markers are unobstructed

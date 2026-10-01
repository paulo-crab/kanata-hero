# Background workers — sprite specification (2 bodies × 3 palettes)

**Status:** Approved by the director 2026-10-02.

**Sources:** `design/characters/background-workers.md`, `levels.md` (Orientation, levels 01, 06, 18–20), `docs/game-design.md`, STYLE_BIBLE §3–7. Shared person rules follow the approved [Gate 1 spec](../gate1/GATE1_ENGINEER_SPEC.md) (frame, anchor, timing, contour-only darkest step, renderer-drawn shadow) and the cast frame rule from [IVO_SPEC.md](IVO_SPEC.md). **Director decision** marks choices made under the delegated art-direction authority.

## Deliverables

| File | What it is |
| --- | --- |
| `bgworker_common.py` | Shared kit: key groups, `PALETTES`, `make_pal`, silhouette palettes and helpers, shared leg poses, `variant()` |
| `bgworker_a_sprites.py` / `bgworker_b_sprites.py` | Hand-placed 16×24 key grids per body: `PAL`, `SLOTS`, `IDLE`, `WALK`, `PALETTES`, `IDLE_VARIANTS`, `SILHOUETTE_PAL` |
| `check_bgworkers.py` | Palette loop (swaps every `PALETTES` entry into `PAL`), variant and silhouette checks; runs `check_gate1.py` on both bodies |
| `build_bgworkers.py` | Builds everything below |
| `bgworker_{a,b}-atlas.png` / `.json` | Native atlas, slate palette. Rows S N E W idle, S N E W walk, then phone / coffee / typing (S). JSON adds `variants`, `palettes`, `silhouette` and `sync` sections. |
| `bgworker_{a,b}-atlas-{olive,ash}.png` | The other palettes, same layout |
| `bgworker_{a,b}-atlas-silhouette[-lit].png` | Silhouette atlases, same layout |
| `bgworkers-sheet.png` | Every frame at ×8, all body × palette strips at ×2 and ×1, silhouettes on floor and through glass |
| `bgworkers-lineup.png` | Engineer, Ivo, Mira beside the six workers at ×4 and ×1 |
| `bgworkers-in-room.png`, `bgworkers-sync-1366x768.gif` | Review room at ×4 with a synced pair on the tiny loop (16 frames) |
| `bgworkers-relaxed-1366x768.png` | After level 06: individual idles |

Rebuild: `python3 build_bgworkers.py`. Check: `python3 ../gate1/check_gate1.py bgworker_a_sprites`, the same for `bgworker_b_sprites`, then `python3 check_bgworkers.py`.

## Silhouette (how the extras differ from the cast at 1×)

| | Body A | Body B | Named cast |
| --- | --- | --- | --- |
| Shoulders | 10 px, the narrowest in the game | 12 px | Engineer 12, Ivo 14, Mira 12 plus bag |
| Hair | short side-parted crop, one tuft, ears showing | centre-parted chin-to-shoulder cut, flicked ends, ear tucked on the worker's left | swept, silver cap, high puff |
| Top | collared shirt, no prop | sweater with a pale under-shirt hem | teal jacket, terracotta cardigan, two-panel jacket |
| Stance | level, hands at the hips | level, hands at the hips | asymmetric or prop-carrying |

## Director decisions

1. **Bodies.** Two bodies share one key layout; a palette is a ramp swap (hair, skin, top, under-shirt, trousers), per the Gate 1 customization rule. No signature prop, no badge, no strap, so extras never out-read the named cast.
2. **Palettes.** `slate`, `olive`, `ash`. Each is a full colourway (hair, skin, top, trousers) so six distinct extras come from two grids. Names avoid anything violet or marker-like.
3. **Muted.** Top, under-shirt and trouser steps stay at or below 30% HSL saturation (the cast's lowest jacket peak is 53%), and the top fill luminance spread is under 0.19 against the cast's 0.41. Top mid-tone keeps at least 2:1 against the floor so figures stay findable. All enforced by `check_bgworkers.py`.
4. **No marker colours.** No marker hex, no violet. No palette step falls in hue 160°–200°, so the 60% teal limit is trivially met.
5. **Hair against skin.** Any hair step touching any skin step has at least 1.25:1 luminance contrast in every palette; the checker enforces it.
6. **Synchronized loop walk.** There is no special march cycle. The standard 4-frame walk (133 ms, 8 px per frame, contacts on frames 0 and 2) is played on one shared clock with no per-actor offset, so every worker in a group shows the same frame at the same moment. The uncanny effect comes from timing and identical paths. Recorded in the atlas JSON under `sync`.
7. **Tiny loop.** Orientation level 01 shows the pair on a 16×16 px square (8 frames per lap, two laps per GIF), the pair 24 px apart as a rigid translation. Facing changes at each corner.
8. **After level 06.** Workers drop the shared clock and each plays an idle or variant with a random `start_offset_ms` (0–999). Idle timing is unchanged (2 × 500 ms).
9. **Individual idles.** Phone check, coffee and typing at air, each 2 frames, facing S. The phone has a dark bezel, a lit face and thumbs; the phone face scrolls between frames. The mug has a pale rim, a dark coffee centre and a handle. Typing alternates the two hands. They are stamps on the S idle rows and keep the 1 px settle of frame 1. Other facings are not needed for the seated or standing background role.
10. **Silhouette.** One flat ink fill `#343650` plus the outer contour `#202337`; the interior contour steps (eyes, arm gaps, hair edge) fill in so only the shape remains. A lit-edge variant (`silhouette_lit`) steps the upper-left contour to `#535971` for figures that stand against a light source. Same rows, same timing, so a renderer can swap atlases. Applies to the named cast's level-20 arrival as well, via the same helpers.
11. **Idle stance.** Level feet (both on row 23), unlike the Engineer's asymmetric stance, so extras read as less characterful.
12. **West is hand-drawn.** W grids were drafted from the mirrored E grids and re-lit by hand so the light stays upper-left (Gate 1 rule).
13. **Scope.** Seated-at-desk work is not drawn here; seated workers need a desk occluder and belong with the environment kit (task 4). No worker is interactable (brief open question 2). Variant counts per district stay at two bodies × three palettes (brief open question 1).

## Acceptance criteria

Automated:
- [x] `check_gate1.py bgworker_a_sprites` and `bgworker_b_sprites`: 24 frames each, 0 failures
- [x] `check_bgworkers.py`: every `PALETTES` entry swapped into `PAL` passes the marker, violet and teal tests, the saturation cap, the contrast tests and the hair/skin test; individual idles are 16×24, grounded, balanced across the anchor, head keys only in rows 0–9; the silhouette palettes use ink steps only

Coordinator review (director to confirm):
- [x] Distinct from the Engineer, Ivo and Mira at 1× (`bgworkers-lineup.png`)
- [x] The pair reads as synchronized and tiny-looped in `bgworkers-sync-1366x768.gif`
- [x] Phone, mug and typing read at ×4 (`bgworkers-relaxed-1366x768.png`)
- [x] Hair reads as hair, not a helmet; ears or nape show on A, the part and uneven ends show on B

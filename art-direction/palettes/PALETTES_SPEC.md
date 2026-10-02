# District palettes and cast ramps (tasks 5.1, 5.2)

**Status:** Approved by the director 2026-10-02.

> **Rich finish (2026-10-02):** world art now uses vivid v2 ramps for Orientation's ink, wood, glass, green, brass and coral, and the ink ramp is shared by every district. The district ramps below are unchanged; their foliage gains a fifth tone. See `../rich-finish/RICH_FINISH_SPEC.md` and the section "Rich finish" at the end of this file.

**Sources:** `docs/game-design.md` district table, `levels.md` district rows and quest art notes, `design/characters/{noor,hal,ada,vale}.md`, STYLE_BIBLE §3 and §7. Pixels follow the same rules as the approved assets: hard steps, shadow to light, the darkest step on contours and joints only.

## Deliverables

| File | What it is |
| --- | --- |
| `district_palettes.py` | The data. `DISTRICTS[name][role]` is 4 hexes, shadow to light, for 8 roles. Also `CAST_RAMPS` (task 5.2), `ROLE_NOTES`, `DEVICE_RAMPS` and `NIGHT_RIM`. |
| `night_rim.py` | The people rim: the one reference implementation (`night_rim`, `night_rim_on_scene`) and the WCAG contrast maths. No side effects. |
| `check_palettes.py` | The numeric checks. Exit code 1 on any failure. |
| `build_palettes.py` | Writes the PNGs below. |
| `palettes-sheet.png` | All five districts' ramps with hexes, the five sample tiles, the seven characters' ramps and the 1x head comparison |
| `palettes-tile-<district>.png` | One sample tile per district at x4 (floor, glass wall, desk, planters, Engineer and Ivo) |
| `cast-heads-x8.png` | The seven heads at x8 on two head templates, for diagnosis |

Rebuild: `python3 build_palettes.py` (Pillow and numpy). Check: `python3 check_palettes.py`.

The sample tiles recolour Orientation's `environment.py` pieces by an exact hex swap (0 unmapped pixels in every tile): stone above row 34 becomes the wall ramp, stone below it the floor ramp, glass, wood and foliage map by role, brass and coral both become the accent ramp. The people are then drawn with their own approved palettes. This is a diagnostic render, not the district kits (tasks 7.x).

## Structure

8 roles, 4 steps each, shadow to light: `ink`, `floor`, `wall`, `glass`, `wood`, `foliage`, `accent`, `violet`.

- `ink` and `violet` are the Orientation ramps verbatim in every district. Glitches stay identical everywhere.
- `floor` step 3 is the broad fill and step 2 the slab mid tone, as `environment.py` uses STONE. Steps 0 and 1 are joints and wear.
- `glass` is the device ramp (terminals, screens). Systems' mint `foliage` is a device ramp too. Device ramps may be teal-hued above 60% saturation but never come near a marker.
- Orientation (approved) is listed in the sheet. Its wall shares the stone ramp and coral remains a ninth, people ramp.

## Ramps

| Ramp | Records | Systems | Night Shift | Executive |
| --- | --- | --- | --- | --- |
| floor | `#46606C` `#6C8996` `#92AEB8` `#BCD0D4` | `#7C8996` `#A2AEB9` `#C8D1D8` `#E8EDF0` | `#12161A` `#242C34` `#364049` `#4C5865` | `#8D8A86` `#B7B3AB` `#D9D5CB` `#F1EEE6` |
| wall | `#756F66` `#A09A8A` `#CDC8B4` `#EBE7D6` | `#3C4A66` `#55698A` `#7C90B0` `#AEBDD3` | `#1B2145` `#283063` `#38437F` `#5062A0` | `#1D2B52` `#2B4079` `#3F5A9E` `#6B84BE` |
| glass / metal | `#1F3745` `#31566A` `#527F94` `#8DB6C2` | `#172B66` `#2347B0` `#2F63D9` `#8CB0F2` | `#2C3560` `#4C5A8E` `#8E96B8` `#D0D4E4` | `#3B5F82` `#6A93B5` `#A5C8DD` `#E1F0F5` |
| wood | `#47202F` `#7B3442` `#A94C47` `#D08060` | `#4B4558` `#7E6F6A` `#B39A7E` `#DCC8A4` | `#3A2230` `#5E3A3E` `#8C5A4A` `#BC8260` | `#3A2630` `#5E3B38` `#8A5A45` `#B98862` |
| foliage | `#2C463F` `#476B59` `#7B9E7F` `#B8CC9E` | `#1D3F46` `#2C7A70` `#5ED0A8` `#B4F0D6` | `#1C3A38` `#2A5A4E` `#3F7A63` `#7EA880` | `#1B4A34` `#2F7A45` `#5FAF55` `#B6DB7A` |
| accent | `#6B2F45` `#A9414F` `#D4606A` `#F4B1A4` | `#7A2F1B` `#C2521A` `#F2842B` `#FFB36B` | `#7A4A4A` `#B8745A` `#E8A55F` `#F9D79A` | `#5E2F2B` `#A4573A` `#D88149` `#F2B98A` |

Shared: ink `#202337` `#343650` `#535971` `#777A8C`; violet `#413755` `#67547C` `#9477AF` `#C3A6D6`.

### Derivation (one line per district)

- **Records**, "desaturated sea blue, linen, cherry wood, coral files": a pale sea-blue floor (21% saturation), linen walls, deeper sea-blue shelving and glass, cherry wood, and a coral accent pulled to dE 12.7 from the marker so it reads as files and not as the conversation marker. Foliage is a dusty sage so only Orientation's garden is lush.
- **Systems**, "cool porcelain, saturated cobalt, mint circuitry, safety orange": a near-white porcelain floor, steel-blue wall panels, cobalt equipment as the glass ramp, a cool sand bench wood, a mint circuit-light ramp in the foliage slot, and a true safety orange accent (dE 17.4 from gold, 28.9 from coral).
- **Night Shift**, "deep indigo, plum, muted silver, warm pools of light": a dark cool-slate floor (hue 210, 14-18% saturation, lighter than the navy wall faces by 15 L*; deliberately not plum, which sat in the violet family), saturated indigo walls, a glass ramp that runs from indigo glass up to muted silver, dim desk wood, night-green planting, and a warm lamp ramp whose steps 0-1 are the pool floor and steps 2-3 are the lamp glow. (Accent step 3 is no longer the people's rim: see the edge-light rule.)
- **Executive**, "pale stone, dark navy, copper, living green": a cool pale-limestone floor (distinct from Orientation's rosy ivory), dark navy walls and seating, high-window sky glass, walnut, saturated living green, and a true copper accent (closing the "true copper" question in vale.md).

## Night Shift edge-light rule

The floor mid step is 1.5:1 against `#202337`, so the outline cannot carry a person there. The rule:

1. **Rim: moonlight on the floor, warm on head and shoulders in pools, per pixel.** Player decisions, 2026-10-02: (i) the warm cream rim `#F9D79A` is replaced by a cool moonlight rim `#8E96B8` (Night Shift glass step 2), because the warm rim read as a "selected" highlight and sat close to discovery gold; (ii) "cool moonlight on the open floor; where a warm source lights someone (inside a lamp pool, Ada's lantern), the warm edge is limited to the head and shoulders". The renderer draws a 1 px hard rim on the upper-left silhouette of a person by a per-pixel rule. For each upper-left silhouette pixel (an opaque pixel with a transparent pixel above or to its left), take the background behind it: the scene pixel at the transparent neighbour above, else to the left. **Moonlight** (the open floor, and the body rows everywhere): recolour the pixel to `#8E96B8` (`NIGHT_RIM` = `("nightshift", "glass", 2)`, the single source of truth for the cool rim) only if (a) it is `#202337`, or its own contrast against that background is below 3:1, and (b) the rim contrasts with that background more than the pixel's current colour does. On the slate floor (`#4C5865`) the rim is 2.49:1 against the plain outline's 2.13:1, so it appears (quiet by design); on a pool (`#B8745A`) it is 1.27:1 against 4.19:1, so the ink outline stays. **Warm light** (a lamp pool): where the background is a lamp-pool colour (accent step 1 fill, step 0 joints) and the pixel is on sprite rows 0-12 (`WARM_RIM_ROWS = 13`, head and shoulders), an ink pixel, or a pixel below 3:1 that the warm colour improves, becomes `#F9D79A` (accent step 3) when that reaches at least 2.5:1 against the pool (2.68:1 on `#B8745A`); rows 13-23 keep the ink outline (4.19:1). Pixels already in the rim colours and Ada's baked lantern rim (key R, `#F9D79A`, now on her head and shoulders only) are never touched. The reference implementation is `night_rim()` in `night_rim.py` (re-exported as `nightshift_kit.night_rim`); `build_palettes.rim_light()` is a thin wrapper that uses a flat floor background, and scenes call `night_rim_on_scene()` with the real background under the sprite frame. The Night Shift landmark's coworker silhouettes behind the lit break-room window keep a warm rim: the room behind them is lit.
2. **Contact shadow.** Floor step 0 as the outer pixels, `#202337` as the core, instead of the ink steps `#535971` / `#343650`, which are lighter than this floor and would read as a glow.
3. **Lamp pools.** "Islands of desk light": inside a pool the floor fill becomes accent step 1 (`#B8745A`) and the joints accent step 0. `#202337` is 4.2:1 against the pool, so the body reads by its ink outline there (the moonlight rim does not replace it); the head and shoulders take the warm rim (rule 1).
4. **Ada.** Her baked lantern-side rim (ada.md) is a fixed 1 px edge in accent step 3 (`#F9D79A`), key R, limited to the lantern side of her head and shoulders (rows 5-10). It is warm on purpose: it is her lantern's light, and the renderer rim never touches it.

## Cast ramps (task 5.2)

Keys follow `ivo_sprites.py`: hair `A B C D` (A on contour only), skin `k l m n` (k on contour or occlusion). `CAST_RAMPS` in the module.

| Character | Hair A B C D | Skin k l m n |
| --- | --- | --- |
| Noor | `#121929` `#102A3E` `#29425A` `#436687` | `#6F5443` `#9D7E5A` `#C1A56E` `#E8C798` |
| Hal | `#8F7344` `#C6A76F` `#DFC38B` `#F5E1AD` | `#5D3A24` `#754F2D` `#8F6C38` `#A8824D` |
| Ada | `#6A5550` `#A99281` `#D8C3AE` `#F6E9D6` | `#24120E` `#3A2018` `#5C3A28` `#80553A` |
| Vale | `#1B1917` `#2B2D25` `#414339` `#606255` | `#947665` `#C0A78B` `#E9CDAE` `#F8E6CC` |

The seven skins form a lightness ladder at the mid step: Ada (L* 28), Mira (41), Hal (48), Engineer (63), Noor (69), Ivo (76), Vale (84). The hair spans blue-black (Noor), sandy blond (Hal), warm white (Ada) and graphite (Vale), beside Engineer's brown, Ivo's cool silver and Mira's plum-black. Noor's, Hal's and Ada's skins carry a different undertone (olive, golden, warm deep brown) from their neighbours on the ladder, so adjacent skins differ in hue and not only in lightness.

## Director decisions

1. **Eight fixed roles and indices** (above), so a district kit is a ramp swap of the Orientation kit. Floor fill is step 3 and mid step 2 because that is how `environment.py` already draws stone.
2. **Orientation is unchanged and grandfathered.** Two of its steps are near markers: coral `#E67A70` is dE 4.0 from the coral marker and brass `#E1AC62` is dE 13.5 from gold. The checker reports them as INFO and does not fail the approved art. The four new districts all pass.
3. **Rule (c) is applied as a silhouette and mass rule, not literally on every mid tone.** A literal 3:1 on every mid tone cannot be met on a light floor: Ivo's silver hair and every skin mid tone are 1.0-1.5:1 against Orientation's own approved stone floor. The enforced rule is: the `#202337` outline is at least 3:1 against floor steps 2 and 3, and at least 45% of each sprite's body pixels reach 3:1 against the floor fill (Orientation reference: 53-89%). The literal mid-tone table is printed for review. **The director should confirm this reading.**
4. **Systems foliage is mint circuitry, not living plants.** It is a device ramp (circuit light, conduit glow, sparse circuit-lit planters). Night Shift, Records and Executive keep real planting. The mint stays at dE 18.4 from terminal teal.
5. **Accent ramps are the district identity**, not a shared brass. Door frames and wayfinding in Records and Systems use the wood or glass ramps; Executive's frames use copper.
6. **Night Shift is a dark-floor district** with the edge-light rule above. The rim (player decisions 2026-10-02: cool moonlight on the floor, warm head and shoulders in pools) is part of the renderer, not baked into the shared sprites, so Engineer, Ivo, Mira and the new cast need no Night Shift variants.
7. **Executive wall navy is more saturated than Vale's suit.** The wall's darkest step is dE 7.0 from the placeholder suit `#2C3352`, so a Vale sprite needs the lit-edge step vale.md already asks for when she stands against navy seating.
8. **Cast ramps.** Corresponding mid steps (hair B and C, skin l and m) are at least dE 12 from every other cast member (smallest: hair B 12.6, hair C 15.9, skin l 13.1, skin m 12.9). No new hair or skin step is within dE 8 of the violet ramp or dE 10 of a marker.
9. **Hair against skin.** Noor (13.0 L*), Hal (13.1), Ada (21.9) and Vale (29.0) all clear 12 L* between every hair fill step and every skin fill step, so no special separator is needed. Noor's and Hal's gaps are narrow: use the Ivo rule anyway where hair meets the forehead (a skin `k` pixel under the fringe, never a flat rim line) so the hair never reads as a helmet.
10. **Director revisions (2026-10-02).** The first Night Shift floor was plum (hue about 300 degrees), inside the violet family, and Ada's skin read burgundy. Night Shift's floor is now a cool slate, a new check (g) forbids any floor or wall step at hue 260-320 degrees above 12% saturation in every district, and Ada's skin is a deep warm brown (hue 11-24 degrees), still the deepest in the cast and dE 13.7 (skin l) and 14.4 (skin m) from the nearest other skin.
11. **The brief open questions this closes:** the Records, Systems (with a real safety orange), Night Shift and Executive (true copper) hex palettes, and Noor's, Hal's, Ada's and Vale's skin and hair ramps. Garment colours stay with the sprite tasks 6.x. Pronouns are untouched.

## Check results

`python3 check_palettes.py` ends with `0 failures, 1 informational notes`.

| Check | Result |
| --- | --- |
| (a) markers | Pass. Closest steps: Records coral accent dE 12.7 from the coral marker; Systems mint dE 18.4 from teal, orange dE 17.4 from gold; Night Shift lamp step dE 16.7 from gold; Executive copper dE 27.0 from gold. The violet ramp is never equal to `#9876D5`. |
| (a2) glitch family | Pass. No non-violet step is within dE 8 of a violet step. Nearest is dE 9.4 (Systems wood step 0). |
| (b) teal saturation | Pass. Teal-hued steps (160-200 degrees) on non-device ramps are at most 36% saturated (Records floor 17-22%, Night Shift foliage 35-36%). Device ramps (glass, Systems mint) reach 47-50% and also stay under 60%. |
| (c) floor contrast, light floors | Pass. Outline against floor mid and fill: Records 6.6:1, Systems 10.0:1, Executive 10.6:1 (Orientation 7.9:1). Body pixels at 3:1 against the fill: 49-89%. |
| (c) Night Shift | Pass by the edge-light rule: moonlight rim `#8E96B8` 2.49:1 against the floor fill (at least 2.4:1 required; the plain outline is 2.13:1), in a lamp pool the warm head-and-shoulder rim 2.68:1 (at least 2.5:1) and the body's ink outline 4.19:1 kept, shadow step 2.5:1 against the fill. Outline against the dark floor is 1.5:1 against the slab mid step, which is why the rim exists. |
| (d) shared ramps | Pass. Ink and violet identical in all five districts; every ramp has 4 distinct steps in lightness order. |
| (e) cast | Pass. See decisions 8 and 9. |
| (g) violet-family guard | Pass. No floor or wall step in any district is in hue 260-320 degrees above 12% saturation. Floor mid distance from `#9477AF`: Orientation dE 48.8, Records 37.4, Systems 42.9, Night Shift 41.4, Executive 49.1. |
| (f) ramp legibility | Pass. Adjacent steps of every new-district ramp are at least dE 8 apart. |

## Acceptance criteria

Automated (`check_palettes.py`):
- [x] No new-district step equals or sits within dE 10 of a UI marker
- [x] Teal-hued steps stay at or below 60% saturation on non-device ramps
- [x] Floor contrast rule met in every district, with the edge-light rule on Night Shift
- [x] Ink and violet ramps identical across districts
- [x] New cast ramps at least dE 12 from existing and each other, hair separated from skin

Coordinator review (to be ticked by the director after looking at `palettes-sheet.png` and the tiles):
- [x] The four districts read as different places at a glance, and none reads as Orientation
- [x] People read against every floor, including Night Shift with the rim
- [x] The seven heads are distinct at 1x and the range of skin tones is inclusive
- [x] No ramp is mistaken for a marker colour

## Rich finish (2026-10-02)

Source of truth: [`../rich-finish/RICH_FINISH_SPEC.md`](../rich-finish/RICH_FINISH_SPEC.md). What it changes here:

- **Orientation** world art takes the v2 ramps for ink, wood, glass, green, brass and coral (exact hexes in that file). Stone is unchanged. The v2 steps are all at least CIE76 dE 10 from the four marker hexes (checked 2026-10-02).
- **Ink is shared by every district**, so every district takes the deeper v2 ink ramp (`#0E1020` `#1C2038` `#3A4160` `#6A7392`). Violet stays verbatim.
- **District foliage** keeps its four-step ramp from the table above and gains a fifth tone for the leaf fans: a sunlit tip one notch lighter than step 3, and a darker edge tone below step 0. Add both to `district_palettes.py` and re-run `check_palettes.py` (marker distance, teal saturation) before use.
- **Night Shift edge light** is unchanged in intent: the moonlight rim is `#8E96B8`, and the warm head-and-shoulders rim stays limited to rows 0-12 inside lamp pools.
- The numeric checks in `check_palettes.py` do not yet know the v2 Orientation ramps; adding them is a task in OpenSpec change `adopt-rich-finish`.


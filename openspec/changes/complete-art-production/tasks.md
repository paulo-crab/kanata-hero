# Tasks

## 1. Foundation and Gate 1 (done before this change; recorded here for continuity)

- [x] 1.1 Audit the style foundation and fix documents that contradict the style bible (C1–C4); README decisions log updated
- [x] 1.2 Decide clothing versus marker colours (D1) and the Gate 1 animation contract (D2); recorded in STYLE_BIBLE §3 and §5
- [x] 1.3 Engineer idle ×4 and walk ×4; `check_gate1.py` passes, approved by the player
- [x] 1.4 Review room at reference-08 finish, with the sliding glass Records door and the RECORDS mat; approved by the player
- [x] 1.5 Ivo idle ×4 and walk ×4; `check_gate1.py ivo_sprites` passes, approved by the player
- [x] 1.6 Mira idle ×4 and walk ×4; `check_gate1.py mira_sprites` passes, approved by the director

## 2. Planning migration

- [ ] 2.1 Remove `art-direction/production/` and point `PRODUCTION_STATUS.md` at this change; verify that `openspec validate complete-art-production` passes

## 3. Orientation context sprites

- [x] 3.1 Background workers: two bodies × three muted palettes, a 4-frame synchronized loop walk, 2–3 individual idles and a silhouette variant; verify the checker passes and that the review room shows a synced pair
- [x] 3.2 Glitches: stapler, chair shadow and folded form at 16–32 px, with roam (2–4 frames) and misregister (1–2 px flicker) frames, violet only; verify a sheet and an in-room render, with a glow that never erases the silhouette
- [x] 3.3 Pace: wayfinding icon and in-world signage on the 16 px grid, avoiding the violet, teal, coral and gold markers; verify an in-room render

## 4. Orientation environment kit

- [x] 4.1 Extract `environment.py` pieces into a named 16 px tile and prop atlas (PNG); verify that every piece renders identically to the approved room
- [x] 4.2 Atlas JSON with footprint, collision mask, draw layer, anchor and animation frames (door slide, lamp glow); verify a JSON schema check
- [x] 4.3 Garden landmark as layered parts with before and after quest states; verify that the after state changes at least two visible things
- [x] 4.4 Rebuild the review room from atlas data plus a cell layout; verify a pixel diff of zero against the approved room

## 5. District palettes

- [x] 5.1 Hex sheets for Records, Systems, Night Shift and Executive appended to STYLE_BIBLE §3; verify the marker-collision and floor-contrast script passes
- [x] 5.2 Skin and hair ramps for Noor, Hal, Ada and Vale; verify they are distinct from the existing cast at 1× and separate hair from skin

## 6. Remaining cast

- [x] 6.1 Noor idle ×4 and walk ×4 with NOOR_SPEC.md; verify the checker and a Records-palette room render
- [x] 6.2 Hal idle ×4 and walk ×4 with HAL_SPEC.md; verify the checker and a Systems render
- [x] 6.3 Ada idle ×4 and walk ×4 with ADA_SPEC.md and a lantern rim-light ruling; verify the checker and a Night Shift render
- [x] 6.4 Vale idle ×4 and walk ×4 with VALE_SPEC.md; verify the checker and an Executive render

## 7. District kits and landmarks

- [x] 7.1 Records kit and circular archive desk landmark (before and after); verify an atlas JSON and a reference room render with a clear two-cell route
- [x] 7.2 Systems kit and routing machine landmark; verify the same
- [x] 7.3 Night Shift kit and long interior window landmark, with strap and edge readability on dark floors; verify the same
- [x] 7.4 Executive kit and atrium tree landmark; verify the same

## 8. Extra animation sets

- [x] 8.1 Interact pose for every recurring character; verify the checker and the sheet
- [x] 8.2 Two reusable reactions per recurring character (Engineer: concerned and satisfied); verify the checker and the sheet
- [x] 8.3 Ivo scripted wave, nod, unscripted laugh and Level 03 tablet flash; verify a sheet and GIFs
- [x] 8.4 Engineer quick turn; verify GIF timing
- [x] 8.5 Mira's six patch designs as 1–2 px states; verify that each is distinct at ×4 and in her portrait

## 9. Portraits

- [x] 9.1 48×48 portrait template and rules; verify a template sheet
- [x] 9.2 Engineer, Ivo and Mira portraits, three expressions each; verify their ramps match the world sprites
- [x] 9.3 Noor, Hal, Ada and Vale portraits; verify the same

## 10. UI presentation

- [x] 10.1 UI tokens file (CSS custom properties) and a contrast check; verify text contrast reaches WCAG AA on panels
- [x] 10.2 Component spec and static reference page (keycap, keyboard inset, dialogue, HUD, prompt, journal, Layout help); verify it at 1366×768 with the inset open

## 11. Developer handoff

- [x] 11.1 `ART_HANDOFF.md` covering the asset index, atlas and JSON formats, anchors, layers, tokens and rebuild steps; verify every listed file exists
- [x] 11.2 Final consistency pass across specs, briefs and the README log; verify `openspec validate complete-art-production` passes and the change is ready to archive

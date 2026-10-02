# Tasks

## 1. Shared implementation and palettes

- [ ] 1.1 Promote the v2 remap, leaf fans, planters, garden parts and light passes from `art-direction/rich-finish/` into `art-direction/kit/rich_finish.py`; verify that rebuilding Mock 2.1 from the shared module has zero differing pixels against `rich-finish/m2_1_organic.png`
- [x] 1.2 Add the Orientation v2 ramps and the foliage, planter, rock and flower extras to `palettes/district_palettes.py`, and teach `check_palettes.py` the marker-distance (dE 10) and teal-saturation checks for them; verify `check_palettes.py` passes
- [x] 1.3 Add the fifth foliage tone and edge tone to each district's foliage ramp; verify `check_palettes.py` passes and `palettes-sheet.png` is rebuilt

## 2. People, props and shadows

- [ ] 2.1 Change the outline key to `#0E1020` and move the ink shoe ramp to `#1C2038` `#3A4160` `#6A7392` in every sprite module (Engineer, Ivo, Mira, Noor, Hal, Ada, Vale, both background workers); verify `check_gate1.py <module>` passes for each and every atlas and JSON is rebuilt
- [ ] 2.2 Update the glitch and Pace modules for the outline colour; verify their builds and checks pass
- [ ] 2.3 Change the renderer contact shadow to `#3A4160` outer and `#1C2038` core in `gate1/build_gate1.py` and the atlas `shadow` notes; verify the Gate 1 scene builds
- [ ] 2.4 Review the chibi portraits' outline against `#0E1020`, record the decision in `portraits/PORTRAITS_SPEC.md`, and rebuild if changed; verify `check_portraits.py` passes

## 3. Orientation

- [ ] 3.1 Re-render the Orientation kit with the v2 palette and leaf-fan foliage and planters; verify `kit/check_atlas.py` passes and every footprint, collision string, layer and anchor is unchanged
- [ ] 3.2 Rebuild the garden landmark parts (tree, pond, rocks, flowers, benches, lamps) for both quest states per the spec; verify the after state still changes at least two visible things
- [ ] 3.3 Add the light passes to the reference-room renderer and rebuild the review room; verify the frame matches the approved Mock 2.1 and rebase the `build_room.py` zero-difference test onto it

## 4. Districts

- [ ] 4.1 Re-render the Records kit, archive desk landmark and reference room; verify `check_atlas.py` and `check_palettes.py` pass and the two-cell route is clear at ×4
- [ ] 4.2 Re-render the Systems kit, routing machine landmark and reference room; verify the same
- [ ] 4.3 Re-render the Night Shift kit, long window landmark and reference room, keeping the moonlight and lamp-pool rim rules; verify the same and that people still read on the dark floor
- [ ] 4.4 Re-render the Executive kit, atrium tree landmark and reference room; verify the same

## 5. Integration and handoff

- [ ] 5.1 Review each character in the re-rendered rooms at ×4 and record any ramp harmony issue as a Director decision; verify a contact sheet per district
- [ ] 5.2 Re-render the UI reference page backgrounds from the new Orientation room; verify the UI contrast check passes
- [ ] 5.3 Update the colour tables in `ART_HANDOFF.md`, `build_all.py` and `check_handoff.py`; verify `build_all.py` passes and a second run leaves `git status` unchanged
- [ ] 5.4 Final side-by-side review of every district against reference 08 and `rich-finish/richness-comparison.png`; verify `openspec validate adopt-rich-finish --strict` passes and update `PRODUCTION_STATUS.md`

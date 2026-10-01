# UI kit: specification (tasks 10.1 and 10.2)

**Status:** Approved by the director 2026-10-02.

**Sources:** `openspec/changes/complete-art-production/specs/ui-presentation/spec.md`, `docs/game-design.md` ("Color, materials, and light", "Characters and UI", "Hint grammar", "Layout help"), `levels.md` hint lines, `~/.config/kanata/kanata.kbd` (read only, for key names and the `nav` layer). `art-direction/ui/README_v2.md` was ignored (rejected).

## Deliverables

| File | What it is |
| --- | --- |
| `tokens.css` | CSS custom properties: anchor colours, panel surfaces, text, keycap tokens, spacing, radius, type, z-layers, the ×4 world zoom and the 1280×720 stage |
| `check_contrast.py` | Parses `tokens.css` and asserts WCAG AA for every pair it lists, the type minimum, no pixel font, the stage maths and the published anchors |
| `COMPONENTS.md` | Component spec: keycap, keyboard inset, dialogue, HUD, prompt, markers, journal, Layout help |
| `reference.html` | Static reference page (only `tokens.css`, `world-native.png` and inline CSS/SVG; no script) |
| `build_reference.py` | Generates `reference.html` (the Layout help keyboard is generated from one key table) |
| `build_world.py` / `world-native.png` | The approved Gate 1 Orientation scene without its four baked pixel markers, drawn by `build_gate1.scene` |
| `reference-1366x768.png` | Render of the stage at 1366×768 with the inset open |
| `reference-greyscale-1366x768.png` | The same with `#grey` (colour-blind check) |

## Rebuild and check

```
PY=/private/tmp/claude-502/-Users-paulo-sebastiao-workspace-kanata-hero/6cfb40fe-e872-4840-b1be-4a334303df10/scratchpad/venv/bin/python
cd art-direction/ui-kit
$PY check_contrast.py          # WCAG AA and token sanity
$PY build_world.py             # markerless world, verified against the approved scene
python3 build_reference.py     # writes reference.html
```

Screenshots were rendered with headless Microsoft Edge (`--headless=new --window-size=1366,768 --screenshot=…`, add `#grey` to the URL for greyscale).

## Director decisions

1. **Anchors unchanged.** Ink, paper, teal, coral, violet and gold keep their published hex values. Roles are fixed.
2. **Text uses lightened accent tints.** Raw teal (4.21:1), coral (4.06:1) and violet (4.08:1, 3.22:1 on raised cards) fail 4.5:1 as text on `--panel-raised`. Added `--accent-terminal #36C3B6`, `--accent-conversation #F2928A` and `--accent-glitch #B79FEA` for text; fills, glyphs and outlines keep the anchor hex. Gold needs no tint.
3. **No text on violet fills.** Ink on violet is 4.08:1, so the kit never sets text on a violet fill. The glitch marker carries no text.
4. **Panels.** `--panel` is ink, `--panel-bg` is ink at 96% (text is rechecked over white and black worlds), plus `--panel-raised #233C4E` and `--panel-sunken #10202A`. `--border #7A94A5` is 4.58:1 on panel and 3.61:1 on raised.
5. **Type.** Minimum 16 px (`--text-sm`), body 18 px. Sans-serif body stack, monospace for keys and gestures, a display stack for titles only.
6. **Stage.** `--world-zoom: 4`, 320×180 world, 1280×720 stage, letterbox `#0E1822`. The UI is laid out in stage CSS px and is not zoomed with the world.
7. **Held keys are never colour-only.** Teal face, sunk 3 px, and a "Hold" tag. XX keys have a dashed border.
8. **Markers.** Speech bubble (coral), monitor (teal), diamond with an arched doorway (gold), folded page with a broken text line (violet). Each has a paper halo and an ink line. Distinct in greyscale by outline.
9. **Reference world has no baked markers.** `gate1-scene-native.png` already contains pixel versions of the four markers. To avoid doubled markers, `world-native.png` is the same scene (verified identical outside the four marker boxes) without them. Proposal for the implementer: draw markers only in the DOM/SVG layer.
10. **Interact and journal keys are proposals.** Interact/Continue uses Return (tap-hold Caps + N), Skip uses Esc (tap Caps), the journal opens with Tab, Layout help with `?`. The game design spec fixes `?` and Esc only. Record or change these when the input spec is written.
11. **Hint wording in written prompts.** Prompts and dialogue use "tap-hold Caps + L" (Kanata vocabulary, game-design hint grammar rule 3), not "hold Caps + L".
12. **Inset content.** Four numbered cells (key position as a mini home row, hold order, output, effect) plus the layer name and hold timing in the header. The inset covers stage x 16–588, y about 412–704.
13. **Portrait slot is a placeholder.** The 192×192 slot is drawn with a hatched placeholder until the portraits of group 9 exist.
14. **Greyscale toggle without script.** `#grey` applies `filter: grayscale(1)` through `:target`; `#` clears it.

## Contrast results (check_contrast.py)

All pairs pass. Lowest text ratios: `accent-terminal` on `panel-raised` 5.27:1, `accent-glitch` on `panel-raised` 5.01:1, `accent-conversation` on `panel-raised` 5.06:1, `text-muted` on `panel-raised` 6.56:1. Lowest UI ratios: `border` on `panel-raised` 3.61:1, `ink` on `violet` 4.08:1.

## Unsure or open

- Interact, journal and skip keys (decision 10).
- The Layout help screen draws only the `nav` tab. `base`, `numbers-symbols` and `practice` use the same component with a different key table; they are described in `COMPONENTS.md` but not rendered.
- Fonts are system stacks; no web font is bundled. Inter is listed first and used only if installed.

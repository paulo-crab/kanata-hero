# Accessibility checklist, level 1 (task 6.4)

Status key: PASS (automated, `node --test tests/checks/a11y.test.js`), PENDING (needs the integrated page; run by hand or with `tools/browser-check.mjs`), FAIL (filed as a follow-up). Last run on the contract skeleton (no UI yet), so every runtime row is PENDING.

| # | Check | How | Result |
| --- | --- | --- | --- |
| 1 | Kit type scale has nothing under 16 px | a11y.test.js | PASS |
| 2 | Game CSS font sizes come from the scale or are at least 16 px | a11y.test.js | PASS (only `main.css` exists) |
| 3 | Game CSS uses kit tokens only (no colour literals), imports `tokens.css` | a11y.test.js | PASS |
| 4 | Focus ring is the `--focus` token and never removed | a11y.test.js | PASS |
| 5 | CSS motion is guarded by `prefers-reduced-motion` or `.rm` | a11y.test.js | PASS (no CSS motion yet) |
| 6 | `index.html` has `lang`, a polite live region, no positive tabindex, no audio | a11y.test.js | PASS |
| 7 | No positive tabindex or Tab trap in `game/src` | a11y.test.js | PASS |
| 8 | Contrast of every text-on-panel pair in `tokens.css` is WCAG AA | `art-direction/ui-kit/check_contrast.py` via a11y.test.js | PASS |
| 9 | Settings classes `.rm`, `.large-text`, `.hc` exist in the stylesheet | a11y.test.js (todo until the UI css merges) | PENDING |
| 10 | Focus order: Tab moves HUD chips, prompt, dialogue buttons in reading order; focus returns to the play surface after a layer closes (`ui:restore-focus`) | manual: Tab through hub, journal, Layout help, settings | PENDING |
| 11 | No keyboard trap: every layer closes with Escape or its Back key; Tab is never prevented (including in a typing scene) | manual plus e2e `?` / Escape round trip | PENDING |
| 12 | Practice region: Tab trap is announced and Escape exits (only in terminal scenes that declare it) | manual in o01-desk-label | PENDING |
| 13 | Reduced motion: OS setting and the Settings toggle stop walk-cycle looping (frame 0), tablet flash and lamp loops; state changes still happen | engine AnimationPlayer test plus manual toggle | PENDING |
| 14 | High contrast: `.hc` raises panel/text contrast; focus ring still visible | manual screenshot at 1366x768 | PENDING |
| 15 | Larger text: `.large-text` grows text without clipping dialogue, HUD or inset | manual screenshot at 1366x768 and 1920x1080 | PENDING |
| 16 | Live region announces every objective change and `vm:announce` | scenario: read `#live` after each step | PENDING |
| 17 | Minimum text 16 px in the rendered page | browser: scan computed `font-size` of every text node | PENDING |
| 18 | Contrast in the rendered page for markers (teal, coral, gold, violet) against the floor | manual screenshots | PENDING |
| 19 | No audio element or request; no `Audio` or `AudioContext` in `game/src` | skeleton.test.js, a11y.test.js | PASS |
| 20 | Every mouse command has a keyboard route (`ui:command` list in CONTRACTS 7.3) | manual | PENDING |

## Failures filed as tasks

None from the automated rows. Findings from other checks that touch accessibility: the lap marker (3,12) and the west desk marker (7,10) are drawn under the keyboard inset while the avatar approaches (see `inset.test.js`, todo test). Owner: level data or UI inset placement.

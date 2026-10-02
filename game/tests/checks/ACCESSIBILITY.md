# Accessibility checklist, level 1 (task 6.4)

Status key: PASS (automated, `node --test tests/checks/a11y.test.js`, or measured in the real page), FAIL (filed below). Last run on the integrated page (`feat/game-integration`) at 1366x768 and 1920x1080 in the Browser pane; screenshots are in `tests/e2e/screenshots/`.

| # | Check | How | Result |
| --- | --- | --- | --- |
| 1 | Kit type scale has nothing under 16 px | a11y.test.js | PASS |
| 2 | Game CSS font sizes come from the scale or are at least 16 px | a11y.test.js | PASS |
| 3 | Game CSS uses kit tokens only, imports `tokens.css` | a11y.test.js | PASS |
| 4 | Focus ring is the `--focus` token and never removed | a11y.test.js | PASS |
| 5 | CSS motion is guarded by `prefers-reduced-motion` or `.rm` | a11y.test.js | PASS |
| 6 | `index.html` has `lang`, a polite live region, no positive tabindex, no audio | a11y.test.js | PASS |
| 7 | No positive tabindex or Tab trap in `game/src` | a11y.test.js | PASS |
| 8 | Contrast of every text-on-panel pair in `tokens.css` is WCAG AA | `check_contrast.py` via a11y.test.js | PASS |
| 9 | Settings classes `.rm`, `.large-text`, `.hc` exist and are applied | page: `#stage` class after each setting | PASS (`stage rm large-text hc`) |
| 10 | Focus order: HUD chips in reading order; focus returns to the play surface after a layer closes | real Tab presses: stage, Journal chip, Layout help chip, stage. Journal: rows, detail region, Also buttons, Close, wraps. Fixed two bugs: the scroll region made Tab skip the Also buttons; focus was not restored because `ui:restore-focus` fired before the layer's view-model was cleared | PASS after fixes (`integration.test.js` focus test) |
| 11 | No keyboard trap: every layer closes with Escape or its Back key; Tab is never prevented | real Esc closes journal, Layout help, Settings, Controls; modal Tab wraps inside the layer; Tab keydown is not claimed in the hub or in the label scene (`isClaimed` never true for Tab) | PASS |
| 12 | Practice region Tab trap | level 01 declares no Tab practice region (later levels do) | N/A for level 1 |
| 13 | Reduced motion: OS setting and the Settings toggle stop looping animation; state changes still happen | Settings "On": stage `.rm`, `world.reducedMotion` true, 0 running CSS animations; the setting reaches the world through `vm:settings-flags` and `ui:settings-applied`; frame-0 hold is covered by `tests/engine/animation.test.js` and `world.test.js` | PASS |
| 14 | High contrast: `.hc` raises panel/text contrast; focus ring still visible | Settings screenshot with larger text and high contrast: white borders, plain panels (`settings-large-text-high-contrast-1366x768.jpg`) | PASS |
| 15 | Larger text grows without clipping dialogue, HUD or inset | lap with larger text (`lap-large-text-1366x768.jpg`); clip scan of hub, journal, Layout help with a card, Controls, Settings with the reset card: no overflow, nothing outside the stage. Fixed: the inset effect cell overflowed by 3 px (now wraps) | PASS after fix |
| 16 | Live region announces every objective change and `vm:announce` | `#live` read after steps: "Objective: Step out of the elevator and listen to Ivo's welcome." and later objectives | PASS |
| 17 | Minimum text 16 px in the rendered page | scan of every visible text node: setup, calibration, hub, dialogue, inset, popup, label, journal, Layout help (with card), Settings, Controls: minimum 16 px (18 px with larger text) | PASS |
| 18 | Markers readable against the floor | markers differ by shape (conversation, terminal, route, glitch) with a halo, plus a check badge when reached; edge arrow carries the same colour and a text label | PASS (screenshots) |
| 19 | No audio element or request | skeleton.test.js, a11y.test.js | PASS |
| 20 | Every mouse command has a keyboard route | `selectKeyboard` and `chooseRow` by arrows and Return; `continue`, `skip`, `back` by Return and Esc; `openLayer` by Q, `?`, journal Also rows; `selectTab` by Left and Right or Tab; `selectKey` by focus; `setSetting`, `resetProgress` by Settings rows and Return; `rideHub` by its journal row | PASS |

## Failures filed as tasks

- The Browser pane hides when the app view moves away, which throttles `requestAnimationFrame` to about 1 fps for the page. Only a test environment effect, but the game then runs at a fifth of its speed; no throttling guard was added (a visible tab runs at 60 fps).
- A real keyboard sends `code: 'Backquote'` for the Hint key; drivers that send no `code` now fall back to the character (interpreter fix, tested).
- Rows 10 and 15 above found real defects that are fixed; no open accessibility failure.

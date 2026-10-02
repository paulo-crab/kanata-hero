# Layout manifest

The machine-readable form of the real keyboard layout, `~/.config/kanata/kanata.kbd`. The game ships it, Layout help is drawn from it, and the checks here keep the design documents, the gesture inventory and the UI kit in step with it. Nothing in this directory ever writes to `kanata.kbd`, and the file is never copied into the repo: the manifest records its path, sha256 and line count.

| File | Role |
| --- | --- |
| `layout-manifest.json` | **Generated.** Never hand-edited. 83 physical keys, four layers, sequences, keyboards, 68 inventory rows |
| `layout-manifest.schema.json` | JSON Schema (draft 2020-12) of the manifest, schema version 1.0 |
| `generate_manifest.py` | Parses `kanata.kbd` (cross-checks `navigation-only.kbd`) and writes the manifest. `--check` fails when the committed manifest is stale |
| `kbd_parse.py` | Reader for the subset of Kanata syntax the file uses; unknown structure stops generation with a line number |
| `inventory_links.py` | Which keys and layers produce each inventory row, plus what the config must give for the row to be true (`expect`) |
| `check_layout.py` | The consistency checks; `validate_levels.py --all` runs them and `--selftest` runs their mutation tests |
| `kit-known-mismatches.json` | UI kit drawing disagreements the UI team has not fixed yet (the check fails on anything new) |
| `CONTRADICTIONS.md` | Every disagreement found among the config, the documents, the inventory and the UI kit, with owners |

## Commands

```
python design/layout/generate_manifest.py            # regenerate (needs ~/.config/kanata/kanata.kbd)
python design/layout/generate_manifest.py --check    # exit 1 if the manifest no longer matches the live file
python design/layout/check_layout.py -v              # every consistency check, with info lines
python design/layout/check_layout.py --selftest      # 31 cases that break a binding on purpose
python design/levels/validate_levels.py --all        # includes check_layout.py
```

Generation is deterministic: the same source file and the same `gesture-inventory.json` give byte-identical output. The `generated` date is kept while the source hash is unchanged. If the source file is absent (CI, another machine) `--check` prints "source not found, skipped" and exits 0; `check_layout.py` then skips only the live-hash comparison and still checks the committed manifest. When `kanata.kbd` changes, run the generator, read the diff and commit it; `check_layout.py` warns ("changed since the manifest was generated") until you do.

## Manifest fields

Top level: `schema_version` (1.0), `manifest_version` (`1.0+` and the first 8 hex digits of the source hash), `generated`, `source` (`path`, `sha256`, `lines`, `process_unmapped_keys`, and the Kanata `version` and `revision` from `build-info.json`), `scope` (Swedish remaps are excluded and listed), `assumptions`, `variables` (the file's `defvar`), `hands` (the left- and right-hand key lists that drive same-hand protection), `timings`, `layers`, `keyboards`, `outputs`, `keys`, `sequences`, `practice`, `reserved_keys`, `inventory`.

- **`layers`**: `base`, `nav`, `numbers-symbols`, `practice` with their Kanata layer name, kind (`default`, `while-held`, `toggle`), entry and exit text, and `activated_by` (key, keyboard, `after_ms`, `scope`). Scope `full` is Caps for `nav`; Right Command (Right Alt on the Microsoft keyboard) is `partial`: it gives the four arrows but not the Caps-only outputs.
- **`timings`**: the hold decisions: `home-row-hold` 200 ms, `caps-hold` 200 ms (hold also starts when another key is pressed), `space-hold` 220 ms, `tab-hold` 250 ms, each with the Kanata action and the keys.
- **`keys`**: every physical key of the US MacBook keyboard: `id` (the UI kit's ids: `a`, `Caps`, `Space`, `Cmd-R`, `Opt-L`...), `kanata` name, `position` (`row` 0 to 5, `column`, `x_u`, `width_u` in keyboard units; Up and Down are half-height keys; `null` for keys a MacBook reaches with fn, plus the Microsoft Right Ctrl), `label`, `hand`, `in_defsrc`, `keyboards`, and `layers.<layer>`.
- **`layers.<layer>` entry**: `behaviour` is `plain`, `tap-hold`, `layer-hold`, `silent` (XX, which is how practice silences the original keys), `passthrough` (not in the config, so it types as usual) or `inherits` (transparent: look at `falls_to`, the layer below). Other fields: `tap` and `hold` (an output name and label; `hold.kind` is `modifier`, `layer` or `macro`), `timing` (variant, `hold_ms`, `trigger_hand`), `legend` (the short text Layout help prints under the keycap), `chord` (reload and practice toggle), `requires_physical` (the nav output needs that real key down), `exceptions` (`when`, `does`; Swedish ones are marked `scope: swedish`), `device_variants.microsoft`, `differs_from_base`, `retained_from_base`, `alias` and `line` (where it comes from in the file).
- **`outputs`**: for each output name, the browser's view: `event_key`, `event_code`, `event_flags` (`ctrlKey`...), and the typed character. Matching in the game is on these, not on the Kanata names.
- **`keyboards`**: `macbook` (default) and `microsoft` (device 045e:07a5): bottom-row layout, and for Microsoft the `remap` of Alt to Command, Windows to Option, Right Alt to Right Command plus nav, Right Windows to Right Option.
- **`sequences`**: `violento-toggle` (Control + Alt + GUI + V, read from the **physical** keys, so home-row holds do not count), `reload-config` (Control + Shift + R, which does count held modifiers), and `emergency-exit` (Left Control + Space + Escape, `status: present_unverified`: the config only mentions it in a comment, so no screen may call it guaranteed).
- **`inventory`**: one row per gesture-inventory id (B01 to B15, N01 to N21, S01 to S26, V01 to V06): `lessons` (`introduced`, `reviewed`, `all`, the level numbers from `gesture-inventory.json`), `verification` (`observed`, `player_confirmed` or `external_only`, mapped from the inventory's `confidence`), `links` (key, layer, role `output`, `hold`, `layer-key`, `silenced` or `context`, and the `expect` the generator and the checker verify), `sequences`, and `observed` (`rule`: what the browser sees and cannot see; `events`: the `key`, `code` and `flags` of each observable output).

## How it is used

- **Layout help.** Each tab draws `keys[*].layers[tab]`: the `legend` under a keycap, `behaviour: silent` as XX, `tap`/`hold`/`timing`/`exceptions` in the detail card (hint grammar from `outputs[...].label`), `layers[tab].activated_by` for the held Caps or Space keycap, `keyboards.microsoft.remap` for the Microsoft switch, and `practice.silenced_keys` plus the `emergency-exit` entry for the practice tab. Keys with `position: null` are listed in a note, not drawn.
- **Input interpreter and feedback.** `inventory[*].observed.events` say which `KeyboardEvent` counts for a row; `verification` decides whether the game may score it (`observed`) or must ask the player (`player_confirmed`, `external_only`). `reserved_keys` are the two commands (`?`, Backtick) no scene may ask for.
- **Key-bindings document.** `check_layout.py` reads the Decisions table of `design/ui-key-bindings.md` and `art-direction/ui-kit/bindings.py` and checks each gesture against the manifest (Return = tap-hold Caps + N, Esc = tap Caps, arrows = Caps + H, J, K, L, Q, Backtick, `?` = tap-hold F then `/`, and that physical Return, Esc and the arrows are silent on practice). A new binding row fails as "unverified" until `BINDING_ROWS` in `check_layout.py` covers it.
- **Level validator.** `validate_levels.py --all` calls `check_layout.run()`: inventory ids equal the manifest ids, lessons, verification and `source_line` agree, every link and `expect` is true, every special key behaviour is linked by some row, the UI kit tabs match, hint lines in `levels.md` and the level data are true, and no inventory output is `?` or Backtick. Reserved-key use in scene tasks stays in `validate_levels.py` (existing rule).

## Changing things

- **New or changed inventory row:** edit `design/levels/gesture-inventory.json` and add or adjust its entry in `inventory_links.py`, then regenerate. The generator refuses to write a manifest in which a link's `expect` is false.
- **UI kit fixed:** delete its entry from `kit-known-mismatches.json`.
- **Not modelled:** Swedish letters (kept as exceptions, never taught); macOS-level keys Kanata does not see (fn); the Microsoft keyboard's arrow cluster and Menu key.

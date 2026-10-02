"""The in-game key bindings, as data: one source for the Controls screen, the prompts' wording and
the lint in check_contrast.py. The prose decisions (why each key, what was rejected, the impact on
levels.md) are in design/ui-key-bindings.md; this module and that document must agree, and
check_contrast.py fails when they do not.

A binding is an OUTPUT the browser observes (event.key), plus the Kanata gesture that makes it on
this layout. The game never knows which physical key made the output, so a physical Return key on
the base layer counts as Return: the hint teaches the gesture, the output is what is observed.

Contexts (the scene classes a binding can be live in):
  world        walking the map, a person or device in range (incl. `walk` scenes)
  dialogue     a modal conversation: portrait, text, Continue and Skip
  instruction  a non-modal instruction line: a hint-bearing line for the step that is live
  overlay      journal, Layout help, elevator map, settings, setup, artifact frame, award, results
  scene        terminal, editor, form, label, keypad and log scenes (letters are text there)
  duel         the glitch duel after a wrong result (focus is on Retry)
"""

CONTEXTS = ("world", "dialogue", "instruction", "overlay", "scene", "duel")

# Keys the game never binds (browser or OS owns them, or they are text, or they trap focus).
NEVER_BOUND = {"Tab", "Space", "Cmd", "Ctrl", "Option", "Alt", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8",
               "F9", "F10", "F11", "F12", "Backspace", "Delete"}

# Characters a scene may never ask the player to type, because they are commands in every scene.
RESERVED_IN_SCENES = {"`", "?"}

# Keys that are text in a scene. A binding on one of these may be live in `scene` only if it is reserved.
TEXT_KEYS = {"Return", "Q", "`", "?", "Space", "Tab", "Backspace"}

BINDINGS = [
    dict(
        id="interact", action="Interact", key="Return", event="Enter",
        gesture="tap-hold Caps + N", alt="mouse click",
        taught="setup calibration step 2 (Caps + N); first used at level 01 arrival",
        contexts={"world"}, layers=("base", "nav", "practice"),
        aria="Interact, talk or use. Key Return. Hint: Return is tap-hold Caps and N.",
        where="Prompt beside a person or device in range, and the elevator call panel",
    ),
    dict(
        id="continue", action="Continue", key="Return", event="Enter",
        gesture="tap-hold Caps + N", alt="mouse click",
        taught="setup calibration step 2 (Caps + N); first used at level 01 arrival",
        contexts={"dialogue", "overlay"}, layers=("base", "nav", "practice"),
        aria="Continue. Key Return. Hint: Return is tap-hold Caps and N.",
        where="Dialogue footer; the primary button of setup, award, results and the elevator",
    ),
    dict(
        id="skip", action="Skip", key="Esc", event="Escape",
        gesture="tap Caps", alt="tap-hold Caps + [ (named from level 07)",
        taught="level 01 popup (tap Caps); alternative taught at level 07",
        contexts={"dialogue"}, layers=("base", "nav", "practice"),
        aria="Skip the conversation. Key Escape. Hint: Escape is tap Caps.",
        where="Dialogue footer",
    ),
    dict(
        id="back", action="Back, close, leave", key="Esc", event="Escape",
        gesture="tap Caps", alt="tap-hold Caps + [ (named from level 07)",
        taught="level 01 popup (tap Caps); alternative taught at level 07",
        contexts={"overlay", "scene", "duel"}, layers=("base", "nav", "practice"),
        aria="Back, close or leave. Key Escape. Hint: Escape is tap Caps.",
        where="Header of every overlay; the bar of every terminal, form and duel scene",
    ),
    dict(
        id="move", action="Move or choose", key="Arrows", event="ArrowUp/Down/Left/Right",
        gesture="tap-hold Caps + H, J, K, L", alt="mouse click",
        taught="setup calibration step 1 (Caps + H); level 01 loop (all four)",
        contexts={"world", "overlay"}, layers=("base", "nav", "practice"),
        aria="Move or choose. Arrow keys. Hint: the arrows are tap-hold Caps and H, J, K or L.",
        where="Walking; lists in the journal, elevator, settings and setup",
    ),
    dict(
        id="journal", action="Open the journal", key="Q", event="q",
        gesture="tap Q", alt="mouse click",
        taught="plain letter tap (base typing, level 02); introduced by Ivo at level 01",
        contexts={"world"}, layers=("base", "nav", "practice"),
        aria="Open the journal. Key Q. Hint: Q is a plain tap.",
        where="HUD chip, top right; the journal's own header (Q closes it too)",
    ),
    dict(
        id="hint", action="Show hint", key="`", event="Backquote (code)",
        gesture="tap `", alt="mouse click",
        taught="plain tap; introduced by Ivo at level 01 and shown on the first Focused prompt",
        contexts={"world", "dialogue", "instruction", "scene"}, layers=("base", "nav", "practice"),
        aria="Show hint. Key Backtick. Hint: Backtick is a plain tap; Kanata leaves it alone.",
        where="HUD chip (Standard and Focused); the dashed Show hint prompt on Focused lines",
    ),
    dict(
        id="help", action="Layout help", key="?", event="?",
        gesture="tap-hold F (Shift), then tap /", alt="journal row, then Return",
        taught="setup calibration step 5 (F as Shift); named at level 01 (Ivo's tablet)",
        contexts={"world", "dialogue", "instruction", "overlay", "scene"}, layers=("base", "nav", "practice"),
        aria="Layout help. Key question mark. Hint: question mark is tap-hold F for Shift, then tap slash.",
        where="HUD chip, top right; the journal's Layout reference row",
    ),
    dict(
        id="retry", action="Retry this turn", key="Return", event="Enter",
        gesture="tap-hold Caps + N", alt="mouse click",
        taught="setup calibration step 2 (Caps + N)",
        contexts={"duel"}, layers=("base", "nav", "practice"),
        aria="Retry this turn. Key Return. Hint: Return is tap-hold Caps and N.",
        where="Under the code in a glitch duel, focused after a wrong result",
    ),
]


def check():
    """Return a list of (ok, text) results; check_contrast.py prints them."""
    out = []
    by = {b["id"]: b for b in BINDINGS}
    out.append((len(by) == len(BINDINGS), "every binding has a unique id"))
    bad = [b["id"] for b in BINDINGS if b["key"] in NEVER_BOUND]
    out.append((not bad, "no binding uses Tab, Space, Command, Control, Option, F-keys, Backspace or Delete" + (f": {bad}" if bad else "")))
    bad = [b["id"] for b in BINDINGS if not b["gesture"].startswith(("tap", "tap-hold")) or not b["taught"]]
    out.append((not bad, "every binding names a Kanata gesture and where it is taught" + (f": {bad}" if bad else "")))
    bad = [b["id"] for b in BINDINGS if not set(b["layers"]) >= {"base", "nav", "practice"}]
    out.append((not bad, "every binding works on base, nav and practice (or documents the alternative)" + (f": {bad}" if bad else "")))
    bad = [b["id"] for b in BINDINGS if "scene" in b["contexts"] and b["key"] in TEXT_KEYS and b["key"] not in RESERVED_IN_SCENES]
    out.append((not bad, "a binding live in a typing scene is a reserved character, never ordinary text" + (f": {bad}" if bad else "")))
    clash = []
    for i, a in enumerate(BINDINGS):
        for b in BINDINGS[i + 1:]:
            if a["key"] == b["key"] and a["contexts"] & b["contexts"]:
                clash.append(f'{a["id"]}/{b["id"]} on {a["key"]} in {sorted(a["contexts"] & b["contexts"])}')
    out.append((not clash, "no two actions share a key in the same context" + (f": {clash}" if clash else "")))
    bad = [b["id"] for b in BINDINGS if not set(b["contexts"]) <= set(CONTEXTS)]
    out.append((not bad, "contexts come from the fixed list" + (f": {bad}" if bad else "")))
    return out

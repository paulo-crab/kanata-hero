"""Which keys and layers produce each gesture-inventory row, what the browser observes, and what the
generator must find in kanata.kbd for the row to be true.

Every link carries an `expect` dict. generate_manifest.py refuses to write a manifest in which an
expectation fails against the parsed config, and check_layout.py re-checks the committed manifest, so a
row can never keep claiming an output the config no longer produces.

Key ids are the manifest's physical-key ids (see generate_manifest.physical_keys): letters and digits as
typed, "Space", "Tab", "Caps", "Return", "Esc", "Backspace", "Delete", "Shift-L", "Cmd-R", ...
Expectation fields (all optional):
  tap            label of the tap output           (entry.tap.label)
  hold           label of the hold output, "layer:<id>" for a layer, or the macro label
  hold_ms        hold timeout in ms
  behaviour      entry.behaviour
  silent         true when the entry is XX
  trigger_hand   same-hand protection list ("left" or "right")
  shift_retained true/false for a nav motion (Shift survives into the output or is dropped)
  retained       true when the layer keeps the base action unchanged
  chord          chord kind ("reload" or "layer-switch")
  chord_target   layer the chord switches to
  requires_physical   the physical key the nav output is gated on
  exception      text that must appear in one of the entry's exceptions (does)
  microsoft      label of what the key does on the Microsoft keyboard ("layer:nav" for the nav layer)
  legend         the legend text
"""

HOME_L = [("a", "Left Control"), ("s", "Left Option"), ("d", "Left Command"), ("f", "Left Shift")]
HOME_R = [("j", "Right Shift"), ("k", "Right Command"), ("l", "Right Option"), (";", "Right Control")]
NAV_OUT = {
    "N01": ("h", "Left"), "N02": ("j", "Down"), "N03": ("k", "Up"), "N04": ("l", "Right"),
    "N05": ("b", "Option+Left"), "N06": ("w", "Option+Right"), "N07": ("0", "Command+Left"),
    "N08": ("4", "Command+Right"), "N09": ("u", "Page Up"), "N10": ("d", "Page Down"),
    "N11": ("t", "Command+Up"), "N12": ("g", "Command+Down"), "N13": ("m", "Backspace"),
    "N14": ("Space", "Backspace"), "N15": (",", "Forward Delete"), "N16": ("x", "Control+D"),
    "N17": ("n", "Return"), "N18": ("[", "Escape"),
}
NUM_KEYS = {"S01": "a", "S02": "s", "S03": "d", "S04": "f", "S05": "g", "S06": "h", "S07": "j", "S08": "k",
            "S09": "l", "S10": ";", "S11": "'", "S12": "q", "S13": "w", "S14": "e", "S15": "r", "S16": "t",
            "S17": "y", "S18": "u", "S19": "i", "S20": "o", "S21": "p", "S22": "[", "S23": "]"}
ARROWS = [("h", "Left"), ("j", "Down"), ("k", "Up"), ("l", "Right")]
SILENT_PRACTICE = ["Backspace", "Delete", "Return", "Esc", "Left", "Right", "Up", "Down", "Home", "End", "PgUp", "PgDn",
                   "Shift-L", "Shift-R", "Ctrl-L", "Ctrl-R", "Opt-L", "Cmd-L", "Opt-R", "Cmd-R"]
DIGITS = list("1234567890")


def L(key, layer, role, **expect):
    d = {"key": key, "layer": layer, "role": role}
    if expect:
        d["expect"] = expect
    return d


def build(inventory_rows):
    """Return {id: {"links": [...], "sequences": [...], "rule": str}} for every inventory row."""
    inv = {r["id"]: r for r in inventory_rows}
    R = {}

    def put(rid, links, rule, sequences=()):
        R[rid] = {"links": links, "sequences": list(sequences), "rule": rule}

    plain = [("b", "b"), ("w", "w"), ("0", "0"), ("4", "4"), ("u", "u"), ("t", "t"), ("m", "m"), ("x", "x"),
             ("n", "n"), ("v", "v"), ("r", "r"), (",", ","), ("g", "g"), ("h", "h")]
    put("B01", [L(k, "base", "output", tap=t, behaviour="plain") for k, t in plain],
        "Each tap arrives as keydown with key equal to the character (b w 0 4 u t m x n v r comma g h). Nothing in "
        "the browser separates a plain tap from the same character typed any other way; keys outside the config "
        "(q e i o p y z c and the punctuation row) pass through the same way.")
    put("B02", [L(k, "base", "output", tap=k) for k in "asdfjkl;"],
        "keydown key is the letter or semicolon with no modifier flag, when the key is released (or rolled into a "
        "same-hand key) before the 200 ms hold.")
    put("B03", [L(k, "base", "hold", hold=h, hold_ms=200, tap=k) for k, h in HOME_L],
        "After about 200 ms the held key acts as a modifier: the next key arrives with ctrlKey (A), altKey (S), "
        "metaKey (D) or shiftKey (F) true. The modifier's own keydown is a side effect and no task may require it.")
    put("B04", [L(k, "base", "hold", hold=h, hold_ms=200, tap=k) for k, h in HOME_R],
        "Mirror of B03: the next key arrives with shiftKey (J), metaKey (K), altKey (L) or ctrlKey (;) true.")
    put("B05", [L(k, "base", "hold", trigger_hand="left", hold_ms=200) for k, _ in HOME_L]
        + [L(k, "base", "hold", trigger_hand="right", hold_ms=200) for k, _ in HOME_R],
        "Hold on one hand, press a key on the other: the second key arrives with the modifier flag set. If the next "
        "key is on the same hand the home-row key resolves as a tap at once and the page sees two letters, so a "
        "same-hand roll is text.")
    put("B06", [L("Caps", "base", "output", tap="Escape", hold="layer:nav", hold_ms=200, behaviour="tap-hold"),
                L("Caps", "base", "layer-key", hold="layer:nav")],
        "A tap released before 200 ms arrives as keydown Escape. A hold raises no event; it shows only in the next "
        "key's output (an arrow, Backspace, Return...). Pressing another key while Caps is down starts the hold at once.")
    put("B07", [L("Space", "base", "output", tap="Space", hold="layer:numbers-symbols", hold_ms=220, behaviour="tap-hold"),
                L("Space", "base", "layer-key", hold="layer:numbers-symbols")],
        "A tap arrives as keydown ' ' (key Space). A hold of about 220 ms raises no event; the next key arrives as "
        "its numbers-symbols output. Pressing a second key before 220 ms types a space then the key.")
    put("B08", [L("Space", "base", "output", exception="Space")],
        "With a modifier already down, Space arrives as keydown ' ' with that modifier flag (an ordinary shortcut). "
        "The OS may take Command+Space, so it is demonstrated, never required as observed output.")
    put("B09", [L("Tab", "base", "output", tap="Tab", hold="Shift+Command+Space", hold_ms=250, behaviour="tap-hold")],
        "A tap arrives as keydown Tab. A hold of 250 ms sends Shift+Command+Space once to macOS to launch the "
        "external Homerow app; the page may see nothing, so the effect is player-confirmed.")
    put("B10", [L("Tab", "base", "output", exception="Tab")],
        "With a modifier already down, Tab arrives as keydown Tab with that modifier flag (an ordinary shortcut); "
        "OS-reserved cases are demonstrated, not scored.")
    put("B11", [L("Cmd-R", "base", "layer-key", hold="layer:nav", legend="+ nav"),
                L("Opt-R", "base", "layer-key", microsoft="layer:nav")]
        + [L(k, "nav", "output", tap=t) for k, t in ARROWS],
        "Right Command (Right Alt on the Microsoft keyboard) held with H J K L arrives as ArrowLeft, ArrowDown, ArrowUp "
        "or ArrowRight with no metaKey (Right Command is removed from arrows). Any other key with Right Command held "
        "arrives as its ordinary Command shortcut; the Caps-only mappings are not granted.")
    put("B12", [L(k, "base", "output", behaviour="plain") for k in
                ["Backspace", "Delete", "Return", "Esc", "Left", "Right", "Up", "Down", "Home", "End", "PgUp", "PgDn",
                 "Shift-L", "Shift-R", "Ctrl-L", "Ctrl-R", "Opt-L", "Cmd-L"]],
        "Physical editing, movement and modifier keys arrive as their ordinary events on base: Backspace, Delete, "
        "Enter, Escape, the arrows, Home, End, PageUp, PageDown, and the modifier flags.")
    put("B13", [L("r", "base", "output", chord="reload", behaviour="plain", tap="r")],
        "Not observable. Kanata reloads its own configuration when a Control and a Shift (home-row holds count, because "
        "the chord reads held modifiers) are down with R, and Option or Command is not; the page sees only modifier flags "
        "and an r keydown (plain Control+R is untouched).", ["reload-config"])
    put("B14", [L("v", "base", "output", chord="layer-switch", chord_target="practice", tap="v", behaviour="plain")],
        "No browser event identifies the toggle; the page sees a v keydown with modifier flags at most. Home-row holds do "
        "not count (the chord reads physical keys), and V alone types v. The layer change is confirmed by the player.",
        ["violento-toggle"])
    put("B15", [L("Opt-L", "base", "output", microsoft="Left Command"), L("Cmd-L", "base", "output", microsoft="Left Option"),
                L("Opt-R", "base", "output", microsoft="layer:nav"), L("Cmd-R", "base", "output", microsoft="Right Option")],
        "On the Microsoft keyboard the physical Alt arrives as Command (metaKey) and Windows as Option (altKey); Right Alt "
        "arrives as Right Command and also holds nav. The page cannot tell which keyboard produced the event, so the setup "
        "step is player-confirmed.")

    for rid, (k, out) in NAV_OUT.items():
        ex = {"tap": out}
        if rid not in ("N01", "N02", "N03", "N04"):
            ex["requires_physical"] = "caps"      # the four arrows also work from Right Command; the rest need the real Caps key
        links = [L("Caps", "base", "layer-key", hold="layer:nav"), L(k, "nav", "output", **ex)]
        put(rid, links,
            "Caps is held first (the hold raises no event); the second key then arrives as the output shown "
            "(see events). The page cannot tell this from the physical key, and cannot see Caps held.")
    nav_shift = [L("f", "base", "hold", hold="Left Shift"), L("j", "base", "hold", hold="Right Shift")]
    nav_shift += [L(k, "nav", "output", shift_retained=True) for k in ("b", "w", "0", "u", "d", "t", "g", "h", "j", "k", "l")]
    nav_shift += [L("4", "nav", "output", shift_retained=False)]
    put("N19", nav_shift,
        "The Shift hold must be established before Caps is pressed. The next key arrives with shiftKey true for word, page, "
        "document and arrow motions; Caps + 4 drops Shift and arrives as Command+Right without it. While Caps is held F types f and J is Down.")
    put("N20", [L(k, "nav", "output", tap=k, behaviour="plain") for k in "asf;"],
        "With Caps held, A S and F arrive as keydown a, s, f (no modifier): they are not navigation commands. The config also keeps ; "
        "literal on nav (the design document lists only A S F; see CONTRADICTIONS.md).")
    put("N21", [L("Cmd-R", "base", "layer-key", hold="layer:nav"), L("Opt-R", "base", "layer-key", microsoft="layer:nav")]
        + [L(k, "nav", "output", tap=t) for k, t in ARROWS] + [L("b", "nav", "context", requires_physical="caps")],
        "Right Command held with H J K L arrives as the four arrows. The other nav outputs need the real Caps key, so Right "
        "Command + B is still Command + B.")

    for rid, k in NUM_KEYS.items():
        out = inv[rid]["output"].strip()
        put(rid, [L("Space", "base", "layer-key", hold="layer:numbers-symbols"), L(k, "numbers-symbols", "output", tap=out)],
            "Space is held about 220 ms first (no event); the key then arrives as the listed character. The page cannot tell this "
            "from the physical number row or a Shift+number chord, so the output is observed but its source is not.")
    put("S24", [L("n", "numbers-symbols", "output", tap="n", retained=True), L("m", "numbers-symbols", "output", tap="m", retained=True)],
        "With Space held, N and M arrive as keydown n and m.")
    put("S25", [L("Caps", "numbers-symbols", "layer-key", hold="layer:nav"), L("Tab", "numbers-symbols", "output", hold="Shift+Command+Space", hold_ms=250)],
        "Caps held over the numbers layer still starts nav (the next key arrives as its nav output); Tab keeps its tap and 250 ms hold, "
        "whose external effect is player-confirmed.")
    put("S26", [L("Space", "base", "output", exception="Space")],
        "With a modifier already down, Space arrives as keydown ' ' with that modifier flag; the held-Space layer is not entered.")

    put("V01", [L("v", "base", "output", chord="layer-switch", chord_target="practice"),
                L("v", "practice", "output", chord="layer-switch", chord_target="base")],
        "No event shows either direction; the player confirms. The same chord (Control, Option and Command held on their physical keys, then V) "
        "enters and leaves.", ["violento-toggle"])
    put("V02", [L(k, "practice", "silenced", silent=True) for k in ("Backspace", "Shift-L")],
        "The self-check is a physical Shift or Backspace in a safe text box that does nothing while practice is on; the page sees only the absence "
        "of an event, which proves nothing, so it stays player-confirmed.")
    put("V03", [L(k, "practice", "hold", hold=h, hold_ms=200) for k, h in HOME_L + HOME_R]
        + [L(k, "practice", "silenced", silent=True) for k in ("Shift-L", "Shift-R", "Ctrl-L", "Ctrl-R", "Opt-L", "Cmd-L", "Opt-R", "Cmd-R")],
        "Home-row holds work as on base (the next key arrives with the modifier flag); the physical modifier keys send nothing.")
    nav_k = ["h", "j", "k", "l", "b", "w", "0", "4", "u", "d", "t", "g", "m", ",", "n", "["]
    put("V04", [L("Caps", "practice", "layer-key", hold="layer:nav")] + [L(k, "nav", "output") for k in nav_k]
        + [L(k, "practice", "silenced", silent=True) for k in ("Return", "Esc", "Backspace", "Delete", "Left", "Right", "Up", "Down")],
        "Caps gestures arrive as on base. The physical Return, Escape, Backspace, Delete and arrows send nothing on practice.")
    put("V05", [L("Space", "practice", "layer-key", hold="layer:numbers-symbols")]
        + [L(k, "numbers-symbols", "output") for k in NUM_KEYS.values()]
        + [L(d, "practice", "silenced", silent=True) for d in DIGITS],
        "Held-Space outputs arrive as on base; the physical digits 1 to 0 send nothing, but the page cannot tell a digit from Space + A..;, so the "
        "evidence is player-confirmed.")
    put("V06", [],
        "Not observable and not defined in the config (a comment says so): Kanata's built-in emergency exit quits the Kanata process. Present as a "
        "last resort only, and only after its behaviour is verified on the target machine.", ["emergency-exit"])
    missing = [rid for rid in inv if rid not in R]
    extra = [rid for rid in R if rid not in inv]
    if missing or extra:
        raise ValueError(f"inventory link table out of step with gesture-inventory.json: missing {missing}, extra {extra}")
    return R

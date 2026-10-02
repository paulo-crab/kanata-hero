#!/usr/bin/env python3
"""Consistency checks for the layout manifest. Called by design/levels/validate_levels.py (--all and --selftest).

    python design/layout/check_layout.py              run every check
    python design/layout/check_layout.py -v           also print warnings and info lines
    python design/layout/check_layout.py --selftest   mutation tests: deliberately break a binding, expect a failure

What is checked (all against the committed layout-manifest.json; kanata.kbd itself is only read to warn when its hash moved):
  1. the manifest validates against layout-manifest.schema.json and is internally consistent;
  2. every inventory row of gesture-inventory.json is in the manifest and vice versa (ids, lessons, verification,
     source_line in docs/game-design.md), every link names a real key and layer, and every link expectation is true;
  3. every key that does something special on a layer is reached by at least one inventory row;
  4. every binding of design/ui-key-bindings.md (and art-direction/ui-kit/bindings.py) is produced by the manifest as the
     document says (Return = tap-hold Caps + N, Esc = tap Caps, Caps + H/J/K/L arrows, Q, Backtick, ? = tap-hold F then /);
  5. the UI kit's Layout help drawings (art-direction/ui-kit/kit_screens.py) match the manifest per layer and keyboard;
     known disagreements are listed in kit-known-mismatches.json (owner: UI team) and anything new fails;
  6. Hint lines ("X is tap-hold Caps + Y") in levels.md and in the level data produce what they claim;
  7. the reserved characters (? and Backtick) are never an inventory output and stay reachable.
"""
import argparse
import copy
import json
import os
import re
import sys
import types
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from generate_manifest import expect_failures, sha256_of, SOURCE, SOURCE_DISPLAY  # noqa: E402

MANIFEST = HERE / "layout-manifest.json"
SCHEMA = HERE / "layout-manifest.schema.json"
INVENTORY = ROOT / "design" / "levels" / "gesture-inventory.json"
GAME_DESIGN = ROOT / "docs" / "game-design.md"
BINDINGS_DOC = ROOT / "design" / "ui-key-bindings.md"
LEVELS_MD = ROOT / "levels.md"
KIT_DIR = ROOT / "art-direction" / "ui-kit"
KNOWN_KIT = HERE / "kit-known-mismatches.json"
DISTRICTS = ["orientation", "records", "systems", "nightshift", "executive"]
LAYERS = ("base", "nav", "numbers-symbols", "practice")
CONFIDENCE = {"output-observed": "observed", "player-confirmed": "player_confirmed", "external-only": "external_only"}


class Result:
    def __init__(self):
        self.errors, self.warnings, self.infos = [], [], []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")

    def info(self, msg):
        self.infos.append(msg)


def jload(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def by_id(manifest):
    return {k["id"]: k for k in manifest["keys"]}


def tap_event(manifest, entry):
    """event.key of an entry's tap output, or None."""
    tap = entry.get("tap")
    if not tap:
        return None
    return manifest["outputs"].get(tap["kanata"], {}).get("event_key")


# --------------------------------------------------------------------------- 1. schema and structure

def check_schema(manifest, res):
    try:
        import jsonschema
    except ImportError:
        res.warn("layout-manifest.json", "jsonschema is not installed; schema not checked")
        return
    schema = jload(SCHEMA)
    v = jsonschema.Draft202012Validator(schema)
    errs = sorted(v.iter_errors(manifest), key=lambda e: list(e.absolute_path))
    for e in errs[:8]:
        path = "/".join(str(p) for p in e.absolute_path)
        res.err("layout-manifest.json", f"schema: {path}: {e.message[:140]}")
    if len(errs) > 8:
        res.err("layout-manifest.json", f"schema: {len(errs) - 8} more errors")


def check_structure(manifest, res):
    where = "layout-manifest.json"
    keys = manifest["keys"]
    ids = [k["id"] for k in keys]
    dup = sorted({i for i in ids if ids.count(i) > 1})
    if dup:
        res.err(where, f"duplicate key ids: {dup}")
    for k in keys:
        for l in LAYERS:
            e = k["layers"].get(l)
            if e is None:
                res.err(where, f"key {k['id']} has no {l} entry")
                continue
            if e["behaviour"] == "inherits" and not e.get("falls_to"):
                res.err(where, f"key {k['id']} {l}: inherits without falls_to")
            if e["behaviour"] == "tap-hold" and not (e.get("tap") and e.get("hold") and e.get("timing")):
                res.err(where, f"key {k['id']} {l}: tap-hold without tap, hold and timing")
            for out in [e.get("tap")] + ([e["hold"].get("output")] if e.get("hold") else []):
                if out and not out.get("external") and out["kanata"] not in manifest["outputs"] and out["kanata"] not in ("macro", "lrld"):
                    res.err(where, f"key {k['id']} {l}: output {out['kanata']!r} has no entry in outputs")
    rows = {}
    for k in keys:
        p = k["position"]
        if p:
            rows.setdefault(p["row"], []).append(p)
    for r, ps in sorted(rows.items()):
        if r == 0:
            continue
        width = sum(p["width_u"] for p in ps if "height_u" not in p or p.get("stack") == "upper")
        if abs(width - 14.5) > 0.76:     # 15u rows (the bottom row has a half-unit gap)
            res.err(where, f"row {r}: widths add up to {width}u, expected about 15u")
    kid = set(ids)
    for kb in ("macbook", "microsoft"):
        for item in manifest["keyboards"][kb]["bottom_row"]:
            src = item["source"]
            if src and not any(k["kanata"] == src for k in keys):
                res.err(where, f"keyboards.{kb}: bottom row source {src!r} is not a key")
    seq_ids = {s["id"] for s in manifest["sequences"]}
    for s in ("violento-toggle", "reload-config", "emergency-exit"):
        if s not in seq_ids:
            res.err(where, f"sequence {s} missing")
    em = next((s for s in manifest["sequences"] if s["id"] == "emergency-exit"), None)
    if em and (em.get("status") != "present_unverified" or em.get("verification") != "external_only"):
        res.err(where, "the emergency sequence must be recorded as present_unverified and external_only until verified")
    tg = next((s for s in manifest["sequences"] if s["id"] == "violento-toggle"), None)
    if tg and tg["label"] != "Control + Alt + GUI + V":
        res.err(where, f"Violento toggle label is {tg['label']!r}")
    for l in manifest["layers"]:
        for a in l["activated_by"]:
            if a["key"] not in kid:
                res.err(where, f"layer {l['id']}: activator {a['key']} is not a key")
    for t in manifest["timings"]:
        for kk in t["keys"]:
            if kk not in kid:
                res.err(where, f"timing {t['id']}: key {kk} is not a key")
    ms = {r["physical"] for r in manifest["keyboards"]["microsoft"]["remap"]}
    if ms != {"Alt-L", "Win-L", "Alt-R", "Win-R"}:
        res.err(where, f"Microsoft remap covers {sorted(ms)}")


# --------------------------------------------------------------------------- 2/3. inventory parity, links, coverage

def check_inventory(manifest, inventory, game_design_lines, res):
    where = "gesture-inventory.json"
    inv = {r["id"]: r for r in inventory["rows"]}
    man = {r["id"]: r for r in manifest["inventory"]}
    for rid in sorted(set(inv) - set(man)):
        res.err(where, f"row {rid} is missing from the layout manifest")
    for rid in sorted(set(man) - set(inv)):
        res.err("layout-manifest.json", f"inventory id {rid} is not in gesture-inventory.json")
    if len(inv) != 68:
        res.warn(where, f"{len(inv)} rows (the design document lists 68)")
    keys = by_id(manifest)
    gd = game_design_lines
    for rid, r in inv.items():
        m = man.get(rid)
        if m is None:
            continue
        less = sorted(set([r["introduced_in"]] + list(r.get("reviewed_in", []))))
        if m["lessons"] != {"introduced": r["introduced_in"], "reviewed": r.get("reviewed_in", []), "all": less}:
            res.err("layout-manifest.json", f"{rid}: lessons differ from gesture-inventory.json (introduced_in / reviewed_in)")
        if m["verification"] != CONFIDENCE.get(r.get("confidence")):
            res.err("layout-manifest.json", f"{rid}: verification {m['verification']!r} differs from the inventory confidence {r.get('confidence')!r}")
        if (m["verification"] == "external_only") != bool(r["external_only"]) or (m["verification"] == "player_confirmed") != bool(r["player_confirmed"]):
            res.err(where, f"{rid}: external_only / player_confirmed flags disagree with confidence {r.get('confidence')!r}")
        for f in ("layer", "input", "output", "group"):
            if m[f] != r[f]:
                res.err("layout-manifest.json", f"{rid}: {f} differs from gesture-inventory.json ({m[f]!r} vs {r[f]!r})")
        if not m["links"] and not m["sequences"]:
            res.err("layout-manifest.json", f"{rid}: not linked to any key or sequence")
        if m["verification"] == "observed" and not m["observed"]["events"]:
            res.err("layout-manifest.json", f"{rid}: an observed row needs at least one observable event")
        for lk in m["links"]:
            key = keys.get(lk["key"])
            if key is None:
                res.err("layout-manifest.json", f"{rid}: link to unknown key {lk['key']!r}")
                continue
            for msg in expect_failures(key, lk["layer"], lk.get("expect", {})):
                res.err("layout-manifest.json", f"{rid}: {msg}")
        seqs = {s["id"] for s in manifest["sequences"]}
        for s in m["sequences"]:
            if s not in seqs:
                res.err("layout-manifest.json", f"{rid}: unknown sequence {s!r}")
        if gd is not None:
            ln = r["source_line"]
            ok = 1 <= ln <= len(gd) and gd[ln - 1].startswith(f"| {r['group']} |")
            if not ok:
                res.err(where, f"{rid}: source_line {ln} does not point at the {r['group']} row of docs/game-design.md")
    if inventory.get("manifest") != "design/layout/layout-manifest.json":
        res.err(where, "the inventory should point at design/layout/layout-manifest.json (field 'manifest')")
    # coverage: no special key behaviour may live outside the inventory
    linked = {(lk["key"], lk["layer"]) for m in man.values() for lk in m["links"]}
    linked_keys = {k for k, _ in linked}
    special = []
    for k in manifest["keys"]:
        for l in LAYERS:
            e = k["layers"][l]
            sw = any(x.get("scope") == "swedish" for x in e.get("exceptions", []))
            if e["behaviour"] in ("tap-hold", "layer-hold", "silent") or e.get("chord") or (l in ("nav", "numbers-symbols") and e.get("differs_from_base")):
                new_here = l in ("nav", "numbers-symbols") and e.get("differs_from_base")
                if (k["id"], l) in linked or (not new_here and k["id"] in linked_keys):
                    continue
                special.append(f"{k['id']}@{l}")
    if special:
        res.err("layout-manifest.json", f"keys with special behaviour that no inventory row links: {', '.join(special)}")
    res.info(f"inventory: {len(man)} manifest rows, {sum(len(m['links']) for m in man.values())} key links, all checked against the parsed layout")


# --------------------------------------------------------------------------- 4. ui-key-bindings.md

def nav_labels(manifest, event_key):
    out = []
    for k in manifest["keys"]:
        e = k["layers"]["nav"]
        flags = manifest["outputs"].get((e.get("tap") or {}).get("kanata"), {}).get("event_flags", ["x"])
        if e.get("explicit") and tap_event(manifest, e) == event_key and e["behaviour"] == "plain" and not flags:
            out.append(k)
    return out


def key_text(k):
    return k["label"].upper() if len(k["label"]) == 1 and k["label"].isalpha() else k["label"]


def expected_gestures(manifest, res):
    """The phrases the key-bindings document and bindings.py must use, derived from the manifest."""
    where = "layout-manifest.json"
    keys = by_id(manifest)

    def one(event_key, what):
        ks = nav_labels(manifest, event_key)
        if len(ks) != 1:
            res.err(where, f"binding check: expected exactly one nav key to produce {what}, found {[key_text(k) for k in ks]}")
            return "?"
        return key_text(ks[0])

    ret = one("Enter", "Return")
    esc = one("Escape", "Escape")
    arrows = [one(a, a) for a in ("ArrowLeft", "ArrowDown", "ArrowUp", "ArrowRight")]
    q = keys["q"]
    grave = keys["`"]
    return {
        "return": f"tap-hold Caps + {ret}",
        "esc_tap": "tap Caps",
        "esc_caps": f"tap-hold Caps + `{esc}`",
        "arrows": "tap-hold Caps + " + ", ".join(arrows),
        "updown": f"tap-hold Caps + {arrows[2]} / {arrows[1]}",
        "q": f"tap {key_text(q)}",
        "backtick": "tap `",
        "help": "tap-hold F (Shift), then tap `/`",
        "help_plain": "tap-hold F (Shift), then tap /",
    }


BINDING_ROWS = [  # (action cell in the Decisions table, expectation keys)
    ("Interact (talk, use a device, call the elevator)", ["return"]),
    ("Continue (dialogue, award, results, setup)", ["return"]),
    ("Skip (a conversation)", ["esc_tap"]),
    ("Back, close, leave", ["esc_tap", "esc_caps"]),
    ("Move, and choose in a list", ["arrows"]),
    ("Show hint", ["backtick"]),
    ("Journal", ["q"]),
    ("Layout help", ["help"]),
    ("Elevator: open the map", ["return"]),
    ("Elevator: pick a floor, confirm, go back", ["updown", "return", "esc_tap"]),
    ("Retry (glitch duel, after a wrong result)", ["return"]),
]
BINDING_IDS = {  # bindings.py id -> expectation key (gesture string must contain it)
    "interact": "return", "continue": "return", "skip": "esc_tap", "back": "esc_tap", "move": "arrows",
    "journal": "q", "hint": "backtick", "help": "help", "retry": "return",
}


def check_bindings(manifest, doc_text, kit_bindings, res):
    where = "design/ui-key-bindings.md"
    keys = by_id(manifest)
    exp = expected_gestures(manifest, res)
    ent = lambda kid, l: keys[kid]["layers"][l]

    # semantic facts the table relies on
    for l in ("base", "practice"):
        c = ent("Caps", l)
        if not (c["behaviour"] == "tap-hold" and c["tap"]["label"] == "Escape" and c["hold"].get("layer") == "nav"):
            res.err(where, f"Caps on {l} must tap Escape and hold the nav layer (Esc = tap Caps, Return = tap-hold Caps + N); manifest has {c.get('tap', {}).get('label')} / {c.get('hold')}")
    for kid, want in (("Return", "Return"), ("Esc", "Escape"), ("Left", "Left"), ("Right", "Right"), ("Up", "Up"), ("Down", "Down")):
        b, p = ent(kid, "base"), ent(kid, "practice")
        if b["behaviour"] != "plain" or (b.get("tap") or {}).get("label") != want:
            res.err(where, f"physical {kid} must produce {want} on base")
        if p["behaviour"] != "silent":
            res.err(where, f"the document says physical {kid} is silent on practice; the manifest has {p['behaviour']}")
    nret = ent("n", "nav")
    if tap_event(manifest, nret) != "Enter" or nret.get("requires_physical") != "caps":
        res.err(where, "Caps + N must give Return and only with the real Caps key (Right Command + N is not Return)")
    for kid, ek in (("h", "ArrowLeft"), ("j", "ArrowDown"), ("k", "ArrowUp"), ("l", "ArrowRight")):
        if tap_event(manifest, ent(kid, "nav")) != ek:
            res.err(where, f"Caps + {kid.upper()} must produce {ek}")
    if tap_event(manifest, ent("[", "nav")) != "Escape":
        res.err(where, "Caps + [ must produce Escape")
    for kid in ("q", "`"):
        for l in ("base", "nav", "practice"):
            e = ent(kid, l)
            if e["behaviour"] not in ("passthrough", "inherits"):
                res.err(where, f"{kid} must be unmapped (a plain tap) on {l}; the manifest has {e['behaviour']}")
    f = ent("f", "base")
    fp = ent("f", "practice")
    for l, e in (("base", f), ("practice", fp)):
        h = e.get("hold") or {}
        if not (e["behaviour"] == "tap-hold" and (h.get("output") or {}).get("kanata") == "lsft"):
            res.err(where, f"? needs F to hold Left Shift on {l}")
        if (e.get("timing") or {}).get("trigger_hand") != "left":
            res.err(where, f"? needs F's same-hand protection to be the left-hand list on {l}; a right-hand list would make F + / a roll")
    slash = keys["/"]
    if slash["hand"] != "right" or slash["layers"]["base"]["behaviour"] != "passthrough":
        res.err(where, "? needs / to be an unmapped right-hand key")
    j = ent("j", "base")
    if (j.get("timing") or {}).get("trigger_hand") != "right" or slash["hand"] != "right":
        res.err(where, "the document says J + / types j/ (same hand); the manifest disagrees")

    # the table rows
    lines = [l for l in doc_text.split("\n") if l.startswith("| ")]
    seen = set()
    for action, wants in BINDING_ROWS:
        row = next((l for l in lines if l.startswith(f"| {action} |")), None)
        if row is None:
            res.err(where, f"Decisions table has no row for {action!r}")
            continue
        seen.add(action)
        for w in wants:
            if exp[w] not in row:
                res.err(where, f"row {action!r} should name the gesture {exp[w]!r} (what kanata.kbd gives); row says: {row[:120]}")
    for l in lines:
        m = re.match(r"^\| ([^|]+?) \| \*\*", l)
        if m and m.group(1) not in seen and m.group(1) not in ("Action",) and ("tap" in l):
            res.err(where, f"unverified binding row {m.group(1)!r}: add it to BINDING_ROWS in check_layout.py")
    if kit_bindings is not None:
        for b in kit_bindings:
            w = BINDING_IDS.get(b["id"])
            if w == "help":
                if exp["help_plain"] not in b["gesture"] and exp["help"] not in b["gesture"]:
                    res.err("art-direction/ui-kit/bindings.py", f"binding 'help' gesture {b['gesture']!r} should contain {exp['help_plain']!r}")
                continue
            if w and exp[w] not in b["gesture"]:
                res.err("art-direction/ui-kit/bindings.py", f"binding {b['id']!r} gesture {b['gesture']!r} should contain {exp[w]!r}")
            if b["id"] == "back" and exp["esc_caps"].replace("`", "") .replace("[", "[") not in b["alt"]:
                res.err("art-direction/ui-kit/bindings.py", f"binding 'back' alternative should name Caps + [ ({b['alt']!r})")
            if b["id"] == "retry" and exp["return"] not in b["gesture"]:
                res.err("art-direction/ui-kit/bindings.py", "retry gesture")
    res.info("bindings: 11 rows of design/ui-key-bindings.md and the bindings.py gestures match the manifest")


# --------------------------------------------------------------------------- 5. UI kit drawings

def drawn_keys(manifest):
    return [k for k in manifest["keys"] if k["position"] and k["position"]["row"] >= 1 and "macbook" in k["keyboards"]]


def kit_id(k):
    return "UpDown" if k["id"] in ("Up", "Down") else k["id"]


def is_special(e):
    return e["behaviour"] in ("tap-hold", "layer-hold") or bool(e.get("chord"))


def expected_kit(manifest, tab):
    exp = {}
    keys = drawn_keys(manifest)
    layer = next(l for l in manifest["layers"] if l["id"] == tab)
    for k in keys:
        kid = kit_id(k)
        e, base = k["layers"][tab], k["layers"]["base"]
        if tab == "base":
            if is_special(e):
                exp[kid] = ("map", e.get("legend"))
        elif tab == "practice":
            if e["behaviour"] == "silent":
                if kid == "UpDown" and not all(manifest_key["layers"]["practice"]["behaviour"] == "silent" for manifest_key in keys if kit_id(manifest_key) == "UpDown"):
                    continue
                exp[kid] = ("silent", "XX")
            elif is_special(e):
                exp[kid] = ("map", e.get("legend"))
        else:
            if e["behaviour"] in ("inherits", "passthrough"):
                continue
            if e.get("differs_from_base") and e["behaviour"] == "plain" and e.get("legend"):
                exp[kid] = ("same" if e["legend"].startswith("= ") else "map", e["legend"])
            elif e.get("retained_from_base"):
                if is_special(base):
                    exp[kid] = ("map", base.get("legend"))
                elif e["behaviour"] == "plain" and len(e["tap"]["label"]) == 1 and e["tap"]["label"].isalpha():
                    exp[kid] = ("same", f"= {e['tap']['label']}")
    if tab in ("nav", "numbers-symbols"):
        for a in layer["activated_by"]:
            if a["scope"] == "full" and a["keyboard"] in ("macbook", "both"):
                exp[kit_id(next(k for k in manifest["keys"] if k["id"] == a["key"]))] = ("layer", "hold")
    return exp


def compare_kit_tab(manifest, ks, tab):
    """List of (mismatch id, message)."""
    exp = expected_kit(manifest, tab)
    drawn = ks.ANN[tab]
    if tab == "base":
        pass
    out = []
    for kid in sorted(set(exp) | {k for k, v in drawn.items() if v[1]}):
        d = drawn.get(kid)
        x = exp.get(kid)
        if x and not d:
            out.append((f"{tab}:{kid}:missing", f"the {tab} tab does not draw {kid}, but the manifest says it is {x[0]} {x[1]!r}"))
        elif d and not x:
            out.append((f"{tab}:{kid}:extra", f"the {tab} tab draws {kid} as {d[1]} {d[0]!r}, which the manifest does not support"))
        elif d and x:
            sub, kind = d[0], d[1]
            if kind != x[0]:
                out.append((f"{tab}:{kid}:kind", f"the {tab} tab draws {kid} as {kind}, the manifest says {x[0]}"))
            elif x[0] in ("map", "same") and sub != x[1] and sub not in [s.strip() for s in (x[1] or "").split("|")]:
                out.append((f"{tab}:{kid}:label", f"the {tab} tab prints {sub!r} under {kid}, the manifest says {x[1]!r}"))
    return out


def kit_mismatches(manifest, ks):
    out = []
    for tab in LAYERS:
        out += compare_kit_tab(manifest, ks, tab)
    # keyboard geometry
    mac = [(i, w) for row in ks.mac_rows() for (i, _, w) in row if i != "gap"]
    flat = []
    for i, w in mac:
        flat += [("Up", w), ("Down", w)] if i == "UpDown" else [(i, w)]
    man = [(k["id"], k["position"]["width_u"]) for k in sorted(drawn_keys(manifest), key=lambda k: (k["position"]["row"], k["position"]["column"]))]
    if flat != man:
        a = [x for x in flat if x not in man]
        b = [x for x in man if x not in flat]
        out.append(("geometry:macbook", f"kit rows differ from the manifest: only in kit {a}, only in manifest {b}"))
    ms_kit = [(i, w) for (i, _, w) in ks.ms_row()]
    ms_man = [(x["id"], x["width_u"]) for x in manifest["keyboards"]["microsoft"]["bottom_row"]]
    if ms_kit != ms_man:
        out.append(("geometry:microsoft", f"kit Microsoft bottom row {ms_kit} differs from the manifest {ms_man}"))
    remap = {r["physical"]: r["legend"] for r in manifest["keyboards"]["microsoft"]["remap"]}
    kit_remap = {k: v[0] for k, v in ks.MS_BASE.items()}
    if remap != kit_remap:
        out.append(("remap:microsoft", f"kit Microsoft remap {kit_remap} differs from the manifest {remap}"))
    # detail cards
    keys = by_id(manifest)
    f, l_, q = keys["f"]["layers"]["base"], keys["l"]["layers"]["base"], keys["q"]["layers"]["numbers-symbols"]
    base_txt = " ".join(str(x) for pair in ks.DETAIL["base"]["dl1"] for x in pair)
    if f"{f['hold']['after_ms']} ms" not in base_txt or "lsft" not in base_txt:
        out.append(("detail:base", f"the base detail card (F) should say {f['hold']['after_ms']} ms and lsft"))
    nav_txt = " ".join(str(x) for pair in ks.DETAIL["nav"]["dl1"] for x in pair)
    if "ralt" not in nav_txt:
        out.append(("detail:nav", "the nav detail card (L) should say the hold is ralt"))
    nums_txt = " ".join(str(x) for pair in ks.DETAIL["numbers-symbols"]["dl2"] for x in pair)
    sp = keys["Space"]["layers"]["base"]["hold"]["after_ms"]
    if q["tap"]["label"] not in nums_txt or str(sp) not in nums_txt:
        out.append(("detail:numbers-symbols", f"the numbers-symbols detail card (Q) should say {q['tap']['label']!r} and {sp} ms"))
    pr_txt = " ".join(str(x) for pair in ks.DETAIL["practice"]["dl2"] for x in pair)
    if "Caps + M" not in pr_txt or tap_event(manifest, keys["m"]["layers"]["nav"]) != "Backspace":
        out.append(("detail:practice", "the practice detail card (Backspace) should name Caps + M, which must give Backspace"))
    # the practice tab's 'also silent' note
    try:
        html = ks.layout_screen("practice")
    except Exception as e:  # pragma: no cover
        html = ""
        out.append(("render:practice", f"layout_screen('practice') failed: {e}"))
    hidden = [k for k in manifest["keys"] if not (k["position"] and k["position"]["row"] >= 1) and k["layers"]["practice"]["behaviour"] == "silent"]
    words = {"Esc": "Esc", "Delete": "Forward Delete", "Home": "Home", "End": "End", "PgUp": "Page Up", "PgDn": "Page Up"}
    for k in hidden:
        if k["id"] == "Ctrl-R":
            continue
        if words.get(k["id"], k["id"]) not in html:
            out.append((f"note:practice:{k['id']}", f"the practice tab's 'Also silent' note does not mention {k['id']}"))
    return out


def check_kit(manifest, ks, known, res):
    where = "art-direction/ui-kit/kit_screens.py"
    found = kit_mismatches(manifest, ks)
    known_ids = {k["id"] for k in known}
    for mid, msg in found:
        if mid not in known_ids:
            res.err(where, f"new mismatch with the manifest [{mid}]: {msg}")
        else:
            res.info(f"known UI kit mismatch [{mid}]: {msg}")
    now = {m for m, _ in found}
    for k in known:
        if k["id"] not in now:
            res.err("design/layout/kit-known-mismatches.json", f"entry {k['id']!r} no longer applies (the UI kit was fixed): remove it")
    res.info(f"ui kit: {len(found)} known mismatch(es) with the Layout help tabs, none new")


# --------------------------------------------------------------------------- 6. hint lines

HINT = re.compile(r"(?:^|then |, )([^,]+?) is tap-hold (Caps|Space)(?: \([^)]*\))? \+ (Space|\S)(?=[,. ]|$)")
OR_HINT = re.compile(r"\bor tap-hold (Caps|Space)(?: \([^)]*\))? \+ (Space|\S)(?=[,. ]|$)")


def norm_name(s):
    s = s.strip()
    s = s[5:] if s.startswith("then ") else s
    s = s.replace(" Arrow", "").replace(" + ", "+")
    m = re.match(r"^(.) \(Shift \+ .+\)$", s)
    return m.group(1) if m else s


def hint_claims(text):
    """(claimed output, layer, key) tuples found in one hint sentence."""
    text = text.replace("**", "")
    out = []
    m = HINT.search(text)
    first = None
    for m in HINT.finditer(text):
        first = norm_name(m.group(1))
        out.append((first, "nav" if m.group(2) == "Caps" else "numbers-symbols", m.group(3)))
    if first and out:
        for o in OR_HINT.finditer(text):
            out.append((first, "nav" if o.group(1) == "Caps" else "numbers-symbols", o.group(2)))
    return out


def check_hint_claim(manifest, claim, where, res):
    out, layer, keytxt = claim
    keys = manifest["keys"]
    want = keytxt.lower() if keytxt.isalpha() and len(keytxt) == 1 else keytxt
    k = next((x for x in keys if x["label"] == want or (x["id"] == keytxt and keytxt == "Space")), None)
    if k is None:
        res.err(where, f"hint names unknown key {keytxt!r}")
        return
    e = k["layers"][layer]
    got = (e.get("tap") or {}).get("label")
    if got != out and not (out == "Command" or out.startswith("Shift")):
        res.err(where, f"hint says {out} is tap-hold {'Caps' if layer == 'nav' else 'Space'} + {keytxt}, but kanata.kbd gives {got!r}")


def check_hints(manifest, levels_text, data_hints, res):
    n = 0
    if levels_text is not None:
        for i, line in enumerate(levels_text.split("\n"), 1):
            if "Hint:" in line:
                for claim in hint_claims(line.split("Hint:", 1)[1]):
                    n += 1
                    check_hint_claim(manifest, claim, f"levels.md:{i}", res)
    for where, text in data_hints:
        for claim in hint_claims(text):
            n += 1
            check_hint_claim(manifest, claim, where, res)
    res.info(f"hints: {n} 'X is tap-hold Caps/Space + Y' claims in levels.md and level data checked against the manifest")


def collect_data_hints():
    out = []
    for d in DISTRICTS:
        for sub in ("levels", "mira"):
            for p in sorted((ROOT / "design" / "levels" / d / sub).glob("*.json")):
                try:
                    data = jload(p)
                except ValueError:
                    continue
                for x in data.get("dialogue", []):
                    h = x.get("hint")
                    if h and h.get("gesture"):
                        out.append((f"{p.relative_to(ROOT)}:{x.get('id')}", h["gesture"]))
    return out


# --------------------------------------------------------------------------- 7. reserved characters

def check_reserved(manifest, res):
    where = "layout-manifest.json"
    for r in manifest["inventory"]:
        for ev in r["observed"]["events"]:
            if ev["key"] in ("?", "`") or ev["code"] == "Backquote":
                res.err(where, f"{r['id']}: an inventory output is a reserved character ({ev['key']!r}); ? and Backtick are commands in every scene")
        if r["id"].startswith("S") and r["id"] <= "S23":
            for lk in r["links"]:
                e = by_id(manifest)[lk["key"]]["layers"][lk["layer"]]
                if (e.get("tap") or {}).get("label") in ("?", "`"):
                    res.err(where, f"{r['id']}: a held-Space output is {e['tap']['label']!r}")
    for rk in manifest["reserved_keys"]:
        if rk["character"] == "`":
            missing = [l for l in ("base", "nav", "practice") if l not in rk.get("passthrough_on", [])]
            if missing:
                res.err(where, f"Backtick must pass through untouched on base, nav and practice; mapped on {missing}")
    outs = {o["label"] for o in manifest["outputs"].values()}
    if "`" in outs and False:
        res.err(where, "unreachable")


# --------------------------------------------------------------------------- 8. live source

def check_source(manifest, res):
    if not SOURCE.exists():
        res.info(f"layout manifest: source not found ({SOURCE_DISPLAY}), live-file check skipped")
        return
    sha = sha256_of(SOURCE.read_text(encoding="utf-8"))
    if sha != manifest["source"]["sha256"]:
        res.warn(SOURCE_DISPLAY, f"changed since the manifest was generated (manifest {manifest['source']['sha256'][:12]}, live {sha[:12]}): "
                                 "run python design/layout/generate_manifest.py and review the diff")
    else:
        res.info(f"layout manifest matches the live {SOURCE_DISPLAY} (sha256 {sha[:12]})")


# --------------------------------------------------------------------------- orchestration

def load_kit():
    sys.path.insert(0, str(KIT_DIR))
    try:
        import kit_screens
        return kit_screens
    finally:
        sys.path.remove(str(KIT_DIR))


def read_lines(path):
    try:
        return Path(path).read_text(encoding="utf-8").split("\n")
    except OSError:
        return None


def run(ctx=None, live=True):
    """Run every check. ctx can override manifest, inventory, doc texts and the kit module (the self-test does)."""
    ctx = ctx or {}
    res = Result()
    manifest = ctx.get("manifest") or jload(MANIFEST)
    inventory = ctx.get("inventory") or jload(INVENTORY)
    check_schema(manifest, res)
    if res.errors:                      # a manifest that does not match its schema cannot be checked further
        return res
    check_structure(manifest, res)
    check_inventory(manifest, inventory, ctx["game_design"] if "game_design" in ctx else read_lines(GAME_DESIGN), res)
    ks = ctx.get("kit") or load_kit()
    doc = ctx["bindings_doc"] if "bindings_doc" in ctx else BINDINGS_DOC.read_text(encoding="utf-8")
    check_bindings(manifest, doc, ks.bindings.BINDINGS, res)
    known = ctx["known"] if "known" in ctx else jload(KNOWN_KIT)["known_mismatches"]
    check_kit(manifest, ks, known, res)
    levels = ctx["levels_md"] if "levels_md" in ctx else LEVELS_MD.read_text(encoding="utf-8")
    hints = ctx["data_hints"] if "data_hints" in ctx else collect_data_hints()
    check_hints(manifest, levels, hints, res)
    check_reserved(manifest, res)
    if live:
        check_source(manifest, res)
    return res


# --------------------------------------------------------------------------- self-test

def selftest():
    """Break one binding at a time and expect the matching failure. Returns 0 when every case behaves."""
    base_manifest = jload(MANIFEST)
    inv = jload(INVENTORY)
    ks = load_kit()
    doc = BINDINGS_DOC.read_text(encoding="utf-8")
    levels = LEVELS_MD.read_text(encoding="utf-8")
    gd = read_lines(GAME_DESIGN)
    known = jload(KNOWN_KIT)["known_mismatches"]

    def key(m, kid):
        return next(k for k in m["keys"] if k["id"] == kid)

    def lab(m, kid, layer, label):
        e = key(m, kid)["layers"][layer]
        e["tap"] = dict(e["tap"], label=label)

    def tap_to(m, kid, layer, kanata):
        e = key(m, kid)["layers"][layer]
        e["tap"] = dict(e["tap"], kanata=kanata)
        m["outputs"].setdefault(kanata, {"label": kanata, "event_key": "Unidentified", "event_code": "Unidentified", "event_flags": []})

    cases = []   # (label, mutate(ctx) , expected substring or None)

    def case(label, fn, expect):
        cases.append((label, fn, expect))

    def m_(fn):
        def go(ctx):
            fn(ctx["manifest"])
        return go

    case("clean state passes", lambda c: None, None)
    case("Caps + H no longer Left", m_(lambda m: lab(m, "h", "nav", "Right")), "N01")
    case("Caps + N no longer Return (binding doc)", m_(lambda m: tap_to(m, "n", "nav", "esc")), "Return")
    case("Caps tap changed from Escape", m_(lambda m: lab(m, "Caps", "base", "Tab")), "Caps on base must tap Escape")
    case("F stops holding Shift", m_(lambda m: key(m, "f")["layers"]["base"]["hold"].__setitem__("output", {"kanata": "lctl", "label": "Left Control"})), "? needs F to hold Left Shift")
    case("F same-hand list switched to the right hand", m_(lambda m: key(m, "f")["layers"]["base"]["timing"].__setitem__("trigger_hand", "right")), "left-hand list")
    case("Physical Return stays silent no more on practice", m_(lambda m: key(m, "Return")["layers"]["practice"].update(behaviour="plain")), "physical Return is silent on practice")
    case("Backtick gets mapped", m_(lambda m: key(m, "`")["layers"]["base"].update(behaviour="plain")), "must be unmapped")
    case("Q gets mapped on practice", m_(lambda m: key(m, "q")["layers"]["practice"].update(behaviour="silent")), "q must be unmapped")
    case("an inventory row is dropped from the manifest", m_(lambda m: m["inventory"].pop(5)), "missing from the layout manifest")
    case("the manifest has an inventory id the inventory lacks", m_(lambda m: m["inventory"][0].__setitem__("id", "B99")), "B99")
    case("lessons differ", m_(lambda m: m["inventory"][20]["lessons"].__setitem__("introduced", 9)), "lessons differ")
    case("verification differs", m_(lambda m: m["inventory"][8].__setitem__("verification", "observed")), "verification")
    case("a link points at a missing key", m_(lambda m: m["inventory"][16]["links"][1].__setitem__("key", "nope")), "unknown key")
    case("a link expectation is false (Caps + B)", m_(lambda m: lab(m, "b", "nav", "Option+Right")), "N05")
    case("a held-Space output changes", m_(lambda m: lab(m, "q", "numbers-symbols", "1")), "S12")
    case("a reserved character becomes an inventory output", m_(lambda m: m["inventory"][16]["observed"]["events"].append({"key": "?", "code": "Slash", "flags": ["shiftKey"], "source": "/", "layer": "base"})), "reserved character")
    case("the emergency sequence is marked verified", m_(lambda m: next(s for s in m["sequences"] if s["id"] == "emergency-exit").update(status="verified")), "present_unverified")
    case("a key gains a special behaviour no row links (Z silent on nav)", m_(lambda m: key(m, "z")["layers"]["nav"].update(behaviour="silent", explicit=True)), "no inventory row links")
    case("schema: a layer entry loses its behaviour", m_(lambda m: key(m, "a")["layers"]["base"].pop("behaviour")), "schema")

    def doc_change(old, new):
        def go(ctx):
            assert old in doc, old
            ctx["bindings_doc"] = doc.replace(old, new, 1)
        return go
    case("the key-bindings doc names the wrong Return gesture", doc_change("| Retry (glitch duel, after a wrong result) | **Return** | tap-hold Caps + N |", "| Retry (glitch duel, after a wrong result) | **Return** | tap-hold Caps + M |"), "Retry")
    case("the key-bindings doc says ? is a right-hand hold", doc_change("tap-hold F (Shift), then tap `/`", "tap-hold J (Shift), then tap `/`"), "Layout help")
    case("the key-bindings doc gains an unverified row", doc_change("| Retry (glitch duel", "| Zoom the map | **Z** | tap Z | n.a. | works |\n| Retry (glitch duel"), "unverified binding row")

    def kit_patch(fn):
        def go(ctx):
            k = types.SimpleNamespace(**vars(ks))
            k.ANN = {t: dict(v) for t, v in ks.ANN.items()}
            fn(k)
            ctx["kit"] = k
        return go
    case("the kit stops drawing Caps + H as an arrow", kit_patch(lambda k: k.ANN["nav"].pop("h")), "nav:h:missing")
    case("the kit draws a key the config does not change", kit_patch(lambda k: k.ANN["nav"].__setitem__("z", ("Z!", "map", 0))), "nav:z:extra")
    case("the kit prints the wrong hold modifier", kit_patch(lambda k: k.ANN["base"].__setitem__("a", ("Shift", "map", 0))), "base:a:label")
    case("the kit draws a silent key as working", kit_patch(lambda k: k.ANN["practice"].__setitem__("Return", ("Return", "", 0))), "practice:Return")
    case("a stale known-mismatch entry", lambda c: c.__setitem__("known", known + [{"id": "nav:h:missing", "reason": "x"}]), "no longer applies")
    case("a hint in levels.md names the wrong key", lambda c: c.__setitem__("levels_md", levels.replace("Option + Left is **tap-hold Caps** + **B**", "Option + Left is **tap-hold Caps** + **W**", 1)), "hint says Option+Left")
    case("a level-data hint names the wrong key", lambda c: c.__setitem__("data_hints", [("level-x", "Down Arrow is tap-hold Caps + K.")]), "hint says Down")
    case("an inventory source_line is stale", lambda c: c.__setitem__("game_design", [""] + gd), "source_line")

    failures = 0
    for label, fn, expect in cases:
        ctx = {"manifest": copy.deepcopy(base_manifest), "inventory": copy.deepcopy(inv), "game_design": gd, "kit": ks, "known": known,
               "bindings_doc": doc, "levels_md": levels, "data_hints": collect_data_hints()}
        fn(ctx)
        res = run(ctx, live=False)
        if expect is None:
            ok = not res.errors
        else:
            ok = any(expect in e for e in res.errors)
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  layout: {label}" + ("" if ok else f"\n        expected {expect!r}; errors: {res.errors[:3]}"))
    print(f"layout selftest: {len(cases) - failures}/{len(cases)} cases behaved as expected")
    return 1 if failures else 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    res = run()
    if args.verbose:
        for x in res.infos:
            print(f"info:    {x}")
        for x in res.warnings:
            print(f"warning: {x}")
    for x in res.errors:
        print(f"ERROR:   {x}")
    print(f"layout: {len(res.errors)} errors, {len(res.warnings)} warnings")
    return 1 if res.errors else 0


if __name__ == "__main__":
    sys.exit(main())

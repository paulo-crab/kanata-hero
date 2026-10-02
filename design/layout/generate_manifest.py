#!/usr/bin/env python3
"""Generate design/layout/layout-manifest.json from the live Kanata configuration.

    python design/layout/generate_manifest.py            write the manifest (needs ~/.config/kanata/kanata.kbd)
    python design/layout/generate_manifest.py --check    fail when the committed manifest no longer matches the live file
    python design/layout/generate_manifest.py --stdout   print instead of writing

The source of truth is ~/.config/kanata/kanata.kbd (outside this repository, read only: this script never
writes to it and never copies it into the repo; the manifest records its path, sha256 and line count).
Generation is deterministic: the same source and the same gesture-inventory.json give byte-identical output.
The generation date is kept from the committed manifest while the source hash is unchanged.

--check exits 0 with a "source not found, skipped" line when the file is absent (CI, another machine).
Structure that the parser does not recognise stops generation with the line number instead of producing a guess.
See README.md for the manifest fields and how the game, the key-bindings document and the level validator use it.
"""
import argparse
import datetime
import hashlib
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
from kbd_parse import Config, KbdError, MODIFIERS  # noqa: E402

SOURCE_DISPLAY = "~/.config/kanata/kanata.kbd"
SOURCE = Path(os.path.expanduser(SOURCE_DISPLAY))
NAV_ONLY = Path(os.path.expanduser("~/.config/kanata/navigation-only.kbd"))
BUILD_INFO = Path(os.path.expanduser("~/.config/kanata/build-info.json"))
MANIFEST = HERE / "layout-manifest.json"
INVENTORY = ROOT / "design" / "levels" / "gesture-inventory.json"
SCHEMA_VERSION = "1.0"
LAYERS = ("base", "nav", "numbers-symbols", "practice")


class GenError(Exception):
    pass


# --------------------------------------------------------------------------- vocabulary

SHIFTED = {"1": "!", "2": "@", "3": "#", "4": "$", "5": "%", "6": "^", "7": "&", "8": "*", "9": "(", "0": ")",
           "-": "_", "=": "+"}
MOD_LABEL = {"lctl": "Left Control", "rctl": "Right Control", "lalt": "Left Option", "ralt": "Right Option",
             "lmet": "Left Command", "rmet": "Right Command", "lsft": "Left Shift", "rsft": "Right Shift"}
MOD_EVENT = {"lctl": ("Control", "ControlLeft", "ctrlKey"), "rctl": ("Control", "ControlRight", "ctrlKey"),
             "lalt": ("Alt", "AltLeft", "altKey"), "ralt": ("Alt", "AltRight", "altKey"),
             "lmet": ("Meta", "MetaLeft", "metaKey"), "rmet": ("Meta", "MetaRight", "metaKey"),
             "lsft": ("Shift", "ShiftLeft", "shiftKey"), "rsft": ("Shift", "ShiftRight", "shiftKey")}
MOD_SHORT = {"lctl": "Ctrl", "rctl": "Ctrl", "lalt": "Opt", "ralt": "Opt", "lmet": "Cmd", "rmet": "Cmd",
             "lsft": "Shift", "rsft": "Shift"}
MOD_PLAIN = {"lctl": "Control", "rctl": "Control", "lalt": "Option", "ralt": "Option", "lmet": "Command",
             "rmet": "Command", "lsft": "Shift", "rsft": "Shift"}
SPECIAL = {  # kanata name: (label, event.key, event.code)
    "spc": ("Space", " ", "Space"), "tab": ("Tab", "Tab", "Tab"), "ret": ("Return", "Enter", "Enter"),
    "esc": ("Escape", "Escape", "Escape"), "bspc": ("Backspace", "Backspace", "Backspace"),
    "del": ("Forward Delete", "Delete", "Delete"), "left": ("Left", "ArrowLeft", "ArrowLeft"),
    "rght": ("Right", "ArrowRight", "ArrowRight"), "up": ("Up", "ArrowUp", "ArrowUp"),
    "down": ("Down", "ArrowDown", "ArrowDown"), "home": ("Home", "Home", "Home"), "end": ("End", "End", "End"),
    "pgup": ("Page Up", "PageUp", "PageUp"), "pgdn": ("Page Down", "PageDown", "PageDown"),
    "caps": ("Caps", "CapsLock", "CapsLock"), "grv": ("`", "`", "Backquote"),
    ";": (";", ";", "Semicolon"), "[": ("[", "[", "BracketLeft"), "]": ("]", "]", "BracketRight"),
    "'": ("'", "'", "Quote"), ",": (",", ",", "Comma"), ".": (".", ".", "Period"), "/": ("/", "/", "Slash"),
    "-": ("-", "-", "Minus"), "=": ("=", "=", "Equal"), "\\": ("\\", "\\", "Backslash"),
}
ARROW_LEGEND = {"left": "←", "down": "↓", "up": "↑", "rght": "→"}
HAND_NAMES = {"left-hand-keys": "left", "right-hand-keys": "right"}
DEVICE_NAMES = {1: "microsoft"}


def key_event(name):
    """(label, event.key, event.code) of a plain kanata key name."""
    if name in SPECIAL:
        return SPECIAL[name]
    if len(name) == 1 and name.isalpha():
        return (name, name, "Key" + name.upper())
    if len(name) == 1 and name.isdigit():
        return (name, name, "Digit" + name)
    if name.startswith("f") and name[1:].isdigit():
        return (name.upper(), name.upper(), name.upper())
    raise GenError(f"no event mapping for key {name!r}")


def out_key(name, mods=(), releases=None):
    """Describe one key press (with modifiers) as the browser will see it."""
    mods = list(mods)
    if name in MOD_EVENT and not mods:
        ek, ec, flag = MOD_EVENT[name]
        return {"kanata": name, "label": MOD_LABEL[name], "event_key": ek, "event_code": ec, "event_flags": [flag]}
    label, ek, ec = key_event(name)
    d = {"kanata": ("+".join(mods + [name]) if mods else name)}
    if mods == ["lsft"] and name in SHIFTED:
        ch = SHIFTED[name]
        d = {"kanata": f"S-{name}", "label": ch, "event_key": ch, "event_code": ec, "event_flags": ["shiftKey"],
             "typed": ch}
    elif mods:
        d["label"] = "+".join([MOD_PLAIN[m] for m in mods] + [label.upper() if len(label) == 1 else label])
        d["event_key"], d["event_code"] = ek, ec
        d["event_flags"] = sorted({MOD_EVENT[m][2] for m in mods})
    else:
        d["label"], d["event_key"], d["event_code"], d["event_flags"] = label, ek, ec, []
        if len(label) == 1:
            d["typed"] = label
    if releases is not None:
        d["shift_retained"] = releases != "all" and "lsft" not in releases and "rsft" not in releases
    return d


# --------------------------------------------------------------------------- physical keyboard (US / MacBook)

def _rows():
    r0 = [("Esc", "esc", 1.5)] + [(f"F{i}", f"f{i}", 1) for i in range(1, 13)]
    r1 = [("`", "grv", 1)] + [(c, c, 1) for c in "1234567890"] + [("-", "-", 1), ("=", "=", 1), ("Backspace", "bspc", 2)]
    r2 = [("Tab", "tab", 1.5)] + [(c, c, 1) for c in "qwertyuiop"] + [("[", "[", 1), ("]", "]", 1), ("\\", "\\", 1.5)]
    r3 = [("Caps", "caps", 1.75)] + [(c, c, 1) for c in "asdfghjkl"] + [(";", ";", 1), ("'", "'", 1), ("Return", "ret", 2.25)]
    r4 = [("Shift-L", "lsft", 2.25)] + [(c, c, 1) for c in "zxcvbnm"] + [(",", ",", 1), (".", ".", 1), ("/", "/", 1), ("Shift-R", "rsft", 2.75)]
    r5 = [("fn", None, 1), ("Ctrl-L", "lctl", 1), ("Opt-L", "lalt", 1), ("Cmd-L", "lmet", 1.25), ("Space", "spc", 5),
          ("Cmd-R", "rmet", 1.25), ("Opt-R", "ralt", 1), ("gap", None, 0.5), ("Left", "left", 1), ("Up", "up", 1),
          ("Down", "down", 1), ("Right", "rght", 1)]
    return [r0, r1, r2, r3, r4, r5]


# Keys that exist on a full-size (Microsoft) keyboard but not as MacBook keys (a MacBook reaches them with fn).
EXTENDED = [("Delete", "del", "fn + Backspace on a MacBook"), ("Home", "home", "fn + Left on a MacBook"),
            ("End", "end", "fn + Right on a MacBook"), ("PgUp", "pgup", "fn + Up on a MacBook"),
            ("PgDn", "pgdn", "fn + Down on a MacBook")]


def physical_keys():
    """Ordered list of dicts: id, kanata, position, width. No behaviour yet."""
    keys = []
    for ri, row in enumerate(_rows()):
        col, x = 0, 0.0
        for kid, kn, w in row:
            if kid == "gap":
                x += w
                continue
            pos = {"row": ri, "column": col, "x_u": round(x, 2), "width_u": w}
            if kid in ("Up", "Down"):
                pos["height_u"] = 0.5
                pos["stack"] = "upper" if kid == "Up" else "lower"
            keys.append({"id": kid, "kanata": kn, "position": pos, "keyboards": ["macbook", "microsoft"]
                         if kid != "fn" else ["macbook"]})
            col += 1
            x += w
    for kid, kn, reach in EXTENDED:
        keys.append({"id": kid, "kanata": kn, "position": None, "reach": reach, "keyboards": ["macbook", "microsoft"]})
    keys.append({"id": "Ctrl-R", "kanata": "rctl", "position": None, "reach": "Right Control exists on the Microsoft keyboard only",
                 "keyboards": ["microsoft"]})
    return keys


# --------------------------------------------------------------------------- describing actions

def mod_names(mods):
    return [MOD_LABEL.get(m, m) for m in mods]


def describe_term(t):
    if "held" in t:
        return MOD_LABEL.get(t["held"], t["held"]) + " held"
    if "input" in t:
        return f"physical {t['input'][1]} pressed"
    if "device_history" in t:
        return "the last key came from the Microsoft keyboard"
    op, args = t["op"], t["args"]
    inner = [describe_term(a) for a in args]
    if op == "or":
        return "any of: " + ", ".join(inner)
    if op == "and":
        return " and ".join(inner)
    return "none of: " + ", ".join(inner)


def describe_cond(c):
    if c.get("default"):
        return "otherwise"
    return " and ".join(describe_term(t) for t in c["all"])


def cond_is_real_gate(c):
    """A single physical-key gate such as (input real caps): returns the key name, else None."""
    if "all" in c and len(c["all"]) == 1 and "input" in c["all"][0] and c["all"][0]["input"][0] == "real":
        return c["all"][0]["input"][1]
    return None


def cond_has_device(c):
    return "all" in c and any("device_history" in t for t in c["all"])


def contains_swedish(node):
    """A macro that presses Option (the Swedish letter sequences) anywhere inside the action."""
    if isinstance(node, dict):
        if node.get("kind") == "macro":
            for st in node["steps"]:
                if st.get("kind") == "unmod" and ("lalt" in st["mods"]):
                    return True
        return any(contains_swedish(v) for v in node.values())
    if isinstance(node, list):
        return any(contains_swedish(v) for v in node)
    return False


def brief(node):
    k = node["kind"]
    if k == "key":
        return out_key(node["key"], node["mods"])["label"]
    if k == "unmod":
        return out_key(node["key"], node["mods"], node["releases"])["label"]
    if k == "tap-hold":
        return f"tap {brief(node['tap'])}, hold {brief(node['hold'])}"
    if k == "macro":
        return macro_label(node)
    if k == "layer-while-held":
        return f"hold the {node['layer']} layer"
    if k == "layer-switch":
        return f"switch to the {node['layer']} layer"
    if k == "multi":
        return " + ".join(brief(a) for a in node["actions"])
    if k == "fork":
        return f"{brief(node['default'])}; with Shift: {brief(node['alternate'])}"
    if k == "switch":
        return "depends on what is held"
    if k == "reload":
        return "reload the Kanata configuration"
    if k == "silent":
        return "nothing (XX)"
    return k


def macro_label(node):
    parts = []
    for st in node["steps"]:
        if st["kind"] == "unmod":
            parts.append(out_key(st["key"], st["mods"])["label"])
        else:
            parts.append(out_key(st["key"])["label"])
    return ", ".join(parts)


def strip(node):
    """Structure of an action without line numbers or alias names, for comparing layers."""
    if isinstance(node, dict):
        return {k: strip(v) for k, v in node.items() if k not in ("line", "alias")}
    if isinstance(node, list):
        return [strip(v) for v in node]
    return node


def sig(node):
    return json.dumps(strip(node), sort_keys=True)


# --------------------------------------------------------------------------- the manifest builder

class Builder:
    def __init__(self, cfg, source_text, inventory):
        self.cfg = cfg
        self.text = source_text
        self.inv = inventory
        self.devices = {DEVICE_NAMES.get(int(k), f"device-{k}"): v for k, v in cfg.devices.items()}
        self.left = cfg.var_list("left-hand-keys")
        self.right = cfg.var_list("right-hand-keys")
        for need in ("base", "nav", "practice", "numbers-symbols"):
            if need not in cfg.layers:
                raise GenError(f"layer {need!r} is missing from the config")
        self.gate = self._nav_gate_key()

    def _nav_gate_key(self):
        """The physical key that the Caps-only navigation additions require ((input real caps))."""
        found = set()

        def walk(n):
            if isinstance(n, dict):
                if "cases" in n:
                    for c in n["cases"]:
                        g = cond_is_real_gate(c["when"])
                        if g:
                            found.add(g)
                for v in n.values():
                    walk(v)
            elif isinstance(n, list):
                for v in n:
                    walk(v)
        for src, node in self.cfg.layers["nav"]["entries"].items():
            walk(self.cfg.norm(node))
        if len(found) != 1:
            raise GenError(f"expected the nav layer to be gated on exactly one physical key, found {sorted(found)}")
        return found.pop()

    # ---------------------------------------------------------------- summaries
    def hold_of(self, node):
        k = node["kind"]
        if k == "key":
            o = out_key(node["key"], node["mods"])
            return {"kind": "modifier", "output": o, "label": o["label"]}
        if k == "layer-while-held":
            return {"kind": "layer", "layer": node["layer"]}
        if k == "macro":
            return {"kind": "macro", "label": macro_label(node), "external": True}
        if k == "multi":
            layer = next((a for a in node["actions"] if a["kind"] == "layer-while-held"), None)
            outs = [out_key(a["key"], a["mods"]) for a in node["actions"] if a["kind"] == "key"]
            if layer:
                return {"kind": "layer", "layer": layer["layer"], "also_outputs": outs}
        raise GenError(f"cannot describe hold action {k}")

    def summarize(self, node):
        k = node["kind"]
        s = {}
        if node.get("alias"):
            s["alias"] = node["alias"]
        if k == "key":
            s.update(behaviour="plain", tap=out_key(node["key"], node["mods"]))
        elif k == "unmod":
            s.update(behaviour="plain", tap=out_key(node["key"], node["mods"], node["releases"]))
        elif k == "macro":
            s.update(behaviour="plain", tap={"kanata": "macro", "label": macro_label(node), "external": True})
        elif k == "silent":
            s.update(behaviour="silent")
        elif k == "transparent":
            s.update(behaviour="inherits")
        elif k == "layer-while-held":
            s.update(behaviour="layer-hold", hold={"kind": "layer", "layer": node["layer"]})
        elif k == "multi":
            s.update(behaviour="layer-hold", hold=self.hold_of(node))
        elif k == "tap-hold":
            tap = self.summarize(node["tap"])
            t = {"variant": node["variant"], "tap_timeout_ms": node["tap_ms"], "hold_ms": node["hold_ms"]}
            if node["variant"] == "tap-hold-tap-keys":
                var = node["trigger_keys_var"]
                t["same_hand_rolls_type_the_tap"] = True
                t["trigger_hand"] = HAND_NAMES.get(var)
                if node.get("require_prior_idle_ms") is not None:
                    t["require_prior_idle_ms"] = node["require_prior_idle_ms"]
            if node["variant"] == "tap-hold-press":
                t["hold_starts_when_another_key_is_pressed"] = True
            hold = self.hold_of(node["hold"])
            hold["after_ms"] = node["hold_ms"]
            s.update(behaviour="tap-hold", tap=tap["tap"], hold=hold, timing=t)
        elif k == "fork":
            s.update(self.summarize(node["default"]))
            s["shift_variant"] = brief(node["alternate"])
        elif k == "switch":
            s.update(self.summarize_switch(node))
        elif k == "reload":
            s.update(behaviour="plain", tap={"kanata": "lrld", "label": "reload configuration"})
        else:
            raise GenError(f"cannot summarise action {k}")
        return s

    def summarize_switch(self, node):
        cases = node["cases"]
        primary = next((c for c in cases if c["when"].get("default")), None)
        gated = next((c for c in cases if cond_is_real_gate(c["when"])), None)
        exceptions, extras = [], {}
        chord = None
        for c in cases:
            then = c["then"]
            e = {"when": describe_cond(c["when"]), "does": brief(then)}
            if contains_swedish(then):
                e["scope"] = "swedish"
            if c is gated:
                continue
            if cond_has_device(c["when"]):
                extras.setdefault("device_variants", {})[DEVICE_NAMES.get(c["when"]["all"][0]["device_history"][0], "device")] = self.summarize(then)
                continue
            if c is primary:
                continue
            if then["kind"] in ("layer-switch", "reload"):
                chord = {"kind": "reload" if then["kind"] == "reload" else "layer-switch",
                         "target": then.get("layer"), "when": self.chord_description(c["when"]),
                         "uses_physical_input": self.cond_uses_input(c["when"]), "line": c["line"]}
                continue
            exceptions.append(e)
        if gated is not None:
            main = gated["then"]
            extras["requires_physical"] = cond_is_real_gate(gated["when"])
            if primary is not None:
                exceptions.append({"when": f"{extras['requires_physical']} is not physically held (the Right Command route)",
                                   "does": brief(primary["then"])})
        elif primary is not None:
            main = primary["then"]
        else:
            raise GenError("a switch without a default case cannot be summarised")
        s = self.summarize(main)
        s.pop("alias", None)
        s["contextual"] = True
        if exceptions:
            s["exceptions"] = exceptions
        if chord:
            s["chord"] = chord
        s.update(extras)
        return s

    def cond_uses_input(self, c):
        def walk(t):
            if "input" in t:
                return True
            if "op" in t:
                return any(walk(a) for a in t["args"])
            return False
        return any(walk(t) for t in c.get("all", []))

    def chord_description(self, c):
        """Names of the modifier groups a chord condition requires."""
        groups = []

        def collect(t):
            if "op" in t and t["op"] == "and":
                for a in t["args"]:
                    collect(a)
            elif "op" in t and t["op"] == "or":
                names = []
                for a in t["args"]:
                    names.append(a["input"][1] if "input" in a else a.get("held"))
                groups.append({"any_of": names})
            elif "op" in t and t["op"] == "not":
                groups.append({"none_of": [a.get("held") for a in t["args"]]})
        for t in c["all"]:
            collect(t)
        return groups

    # ---------------------------------------------------------------- legends
    def legend(self, s, layer, key_label=None):
        if s.get("chord"):
            return "reload" if s["chord"]["kind"] == "reload" else "toggle"
        b = s["behaviour"]
        if b == "tap-hold":
            h, t = s["hold"], s["tap"]
            if h["kind"] == "modifier":
                return MOD_SHORT[h["output"]["kanata"]]
            if h["kind"] == "macro":
                return "Homerow"
            if h["kind"] == "layer":
                short = "numbers" if h["layer"] == "numbers-symbols" else h["layer"]
                if t["label"] == "Space":
                    return f"tap Space | hold {short}"
                return f"{'Esc' if t['label'] == 'Escape' else t['label']} | {short}"
        if b == "layer-hold" and s["hold"].get("also_outputs"):
            return "+ " + s["hold"]["layer"]
        if b == "silent":
            return "XX"
        if b == "plain" and "tap" in s and layer in ("nav", "numbers-symbols"):
            if key_label and len(key_label) == 1 and s["tap"]["label"] == key_label:
                return f"= {key_label}"         # the key stays what it is here (a letter, or ;)
            return self.output_legend(s["tap"])
        return None

    @staticmethod
    def output_legend(o):
        k = o["kanata"]
        if k in ARROW_LEGEND:
            return ARROW_LEGEND[k]
        table = {"lalt+left": "Word ←", "lalt+rght": "Word →", "lmet+left": "Line ←", "lmet+rght": "Line →",
                 "lmet+up": "Doc ↑", "lmet+down": "Doc ↓", "lctl+d": "Ctrl+D", "pgup": "Page ↑", "pgdn": "Page ↓",
                 "del": "Delete", "bspc": "Bksp", "ret": "Return", "esc": "Esc"}
        if k in table:
            return table[k]
        if "typed" in o and not o["typed"].isalpha():
            return o["typed"]          # a digit or a shifted symbol; plain letters get "= x" instead
        return None

    # ---------------------------------------------------------------- per key and layer
    def layer_entry(self, layer, key):
        src = key["kanata"]
        L = self.cfg.layers[layer]
        node = L["entries"].get(src) if src else None
        line = getattr(node, "line", None)
        explicit = node is not None
        if node is None:
            if L["form"] == "deflayermap":
                norm = {"kind": "transparent"}
            elif src and src in self.cfg.src:
                raise GenError(f"{layer}: source key {src} has no action")
            else:
                return {"behaviour": "passthrough", "explicit": False}
        else:
            norm = self.cfg.norm(node)
        s = self.summarize(norm)
        s["explicit"] = explicit
        if line:
            s["line"] = line
        if s["behaviour"] == "inherits":
            return {"behaviour": "inherits", "explicit": explicit, "falls_to": ["base", "practice"], **({"line": line} if line else {})}
        s["_sig"] = sig(norm)
        return s

    def build_keys(self):
        keys = physical_keys()
        for k in keys:
            src = k["kanata"]
            k["label"] = key_event(src)[0] if src and src not in MODIFIERS else k["id"]
            k["hand"] = "left" if src in self.left else "right" if src in self.right else None
            k["in_defsrc"] = bool(src and src in self.cfg.src)
            if src:
                ent = {l: self.layer_entry(l, k) for l in LAYERS}
            else:
                ent = {l: {"behaviour": "passthrough", "explicit": False} for l in LAYERS}
            base = ent["base"]
            for l in ("nav", "numbers-symbols"):
                e = ent[l]
                if e["behaviour"] in ("inherits", "passthrough"):
                    continue
                same = e.get("_sig") == base.get("_sig")
                e["differs_from_base"] = not same
                e["retained_from_base"] = same
            for l in LAYERS:
                e = ent[l]
                if e["behaviour"] in ("passthrough", "inherits"):
                    continue
                lg = self.legend(e, l, k["label"])
                if lg:
                    e["legend"] = lg
            for e in ent.values():
                e.pop("_sig", None)
            k["layers"] = {l: sort_layer_entry(ent[l]) for l in LAYERS}
        return keys


def sort_layer_entry(e):
    order = ["behaviour", "explicit", "alias", "line", "contextual", "tap", "hold", "timing", "legend", "chord",
             "requires_physical", "exceptions", "device_variants", "shift_variant", "falls_to",
             "differs_from_base", "retained_from_base"]
    out = {k: e[k] for k in order if k in e}
    for k in e:
        if k not in out:
            out[k] = e[k]
    return out


# --------------------------------------------------------------------------- expectations (shared with check_layout.py)

def expect_failures(key, layer, ex):
    """Return a list of strings: what an inventory link expects of key.layers[layer] that is not true."""
    e = key["layers"][layer]
    bad = []
    where = f"{key['id']}@{layer}"

    def hold_label(h):
        if h is None:
            return None
        if h["kind"] == "layer":
            return "layer:" + h["layer"]
        return h["label"]

    for name, want in ex.items():
        if name == "tap":
            got = (e.get("tap") or {}).get("label")
        elif name == "hold":
            got = hold_label(e.get("hold"))
        elif name == "hold_ms":
            got = (e.get("hold") or {}).get("after_ms")
        elif name == "behaviour":
            got = e.get("behaviour")
        elif name == "silent":
            got = e.get("behaviour") == "silent"
        elif name == "trigger_hand":
            got = (e.get("timing") or {}).get("trigger_hand")
        elif name == "shift_retained":
            got = (e.get("tap") or {}).get("shift_retained")
        elif name == "retained":
            got = bool(e.get("retained_from_base"))
        elif name == "chord":
            got = (e.get("chord") or {}).get("kind")
        elif name == "chord_target":
            got = (e.get("chord") or {}).get("target")
        elif name == "requires_physical":
            got = e.get("requires_physical")
        elif name == "legend":
            got = e.get("legend")
        elif name == "exception":
            got = want if any(want == x.get("does") for x in e.get("exceptions", [])) else [x.get("does") for x in e.get("exceptions", [])]
        elif name == "microsoft":
            v = (e.get("device_variants") or {}).get("microsoft")
            got = None if v is None else (("layer:" + v["hold"]["layer"]) if v["behaviour"] == "layer-hold" else (v.get("tap") or {}).get("label"))
        else:
            bad.append(f"{where}: unknown expectation {name!r}")
            continue
        if got != want:
            bad.append(f"{where}: expected {name}={want!r}, manifest has {got!r}")
    return bad


# --------------------------------------------------------------------------- the other blocks

def build_timings(keys):
    groups = {}
    for k in keys:
        e = k["layers"]["base"]
        t = e.get("timing")
        if not t:
            continue
        h = e["hold"]
        if h["kind"] == "modifier":
            gid = "home-row-hold"
        elif h["kind"] == "layer":
            gid = {"nav": "caps-hold", "numbers-symbols": "space-hold"}.get(h["layer"], h["layer"] + "-hold")
        else:
            gid = "tab-hold"
        gk = (gid, t["variant"], t["tap_timeout_ms"], t["hold_ms"])
        groups.setdefault(gk, []).append(k["id"])
    out = []
    meaning = {"home-row-hold": "A S D F / J K L ; become modifiers; a key from the same hand pressed first types the letter",
               "caps-hold": "Caps taps Escape; held (or when another key is pressed) it is the nav layer",
               "space-hold": "Space taps a space; a bare hold activates numbers-symbols",
               "tab-hold": "Tab taps Tab; a bare hold sends Shift+Command+Space once (Homerow app)"}
    for (gid, variant, tap_to, hold), ids in groups.items():
        out.append({"id": gid, "kanata": variant, "tap_timeout_ms": tap_to, "hold_ms": hold, "keys": ids,
                    "meaning": meaning.get(gid, "")})
    return out


def build_sequences(cfg, keys):
    by = {k["id"]: k for k in keys}
    seqs = []

    def group_names(groups):
        out = []
        for g in groups:
            if "any_of" in g:
                first = g["any_of"][0]
                out.append({"name": {"lctl": "Control", "lalt": "Option (Alt)", "lmet": "Command (GUI)", "lsft": "Shift"}.get(first, first),
                            "any_of": g["any_of"]})
            else:
                out.append({"name": "not " + " / ".join(sorted({MOD_PLAIN[x] for x in g["none_of"]})), "none_of": g["none_of"]})
        return out

    def layers_with_chord(keyid, kind):
        res = []
        for l in LAYERS:
            e = by[keyid]["layers"][l]
            if e.get("chord", {}).get("kind") == kind or e["behaviour"] == "inherits":
                res.append(l)
        return res

    v = by["v"]["layers"]["base"]
    c = v.get("chord")
    if not c or c["kind"] != "layer-switch":
        raise GenError("base layer V no longer carries the practice toggle chord")
    seqs.append({"id": "violento-toggle", "label": "Control + Alt + GUI + V", "enters": c["target"], "leaves_to": "base",
                 "modifier_groups": group_names(c["when"]), "then_key": "v", "reads_physical_input": c["uses_physical_input"],
                 "home_row_holds_count": not c["uses_physical_input"],
                 "works_on_layers": layers_with_chord("v", "layer-switch"), "source_line": c["line"],
                 "verification": "player_confirmed",
                 "note": "Control, Option and Command are read from the physical keys on either side (also on the Microsoft keyboard, regardless of the Alt/Windows swap); V alone types v."})
    r = by["r"]["layers"]["base"].get("chord")
    if not r or r["kind"] != "reload":
        raise GenError("base layer R no longer carries the reload chord")
    seqs.append({"id": "reload-config", "label": "Control + Shift + R", "action": "reload the Kanata configuration",
                 "modifier_groups": group_names(r["when"]), "then_key": "r", "reads_physical_input": r["uses_physical_input"],
                 "home_row_holds_count": not r["uses_physical_input"],
                 "works_on_layers": [l for l in LAYERS if by["r"]["layers"][l].get("chord") or by["r"]["layers"][l]["behaviour"] == "inherits"],
                 "source_line": r["line"], "verification": "external_only",
                 "note": "Plain Control+R is not reserved. Option or Command held cancels the chord."})
    emergency = None
    for line, text in cfg.comments:
        if "Left Control + Space + Escape" in text:
            emergency = (line, text)
    seqs.append({"id": "emergency-exit", "label": "Left Control + Space + Escape",
                 "action": "Kanata's built-in emergency exit (quits the Kanata process; not a layer toggle)",
                 "physical_keys": ["lctl", "spc", "esc"], "defined_in_config": False,
                 "source_line": emergency[0] if emergency else None,
                 "source_text": emergency[1] if emergency else None,
                 "verification": "external_only", "status": "present_unverified",
                 "note": "The configuration only documents it in a comment; it is built into Kanata. Its runtime behaviour on this machine (including whether the service restarts) has not been verified, so no screen may call it guaranteed."})
    return seqs


def build_keyboards(cfg, keys, builder):
    by = {k["kanata"]: k for k in keys if k["kanata"]}
    mac_bottom = [{"id": i, "source": s, "width_u": w} for i, s, w in _rows()[5] if i != "gap"]
    ms_bottom = [("Ctrl-L", "lctl", 1.25), ("Win-L", "lmet", 1.25), ("Alt-L", "lalt", 1.25), ("Space", "spc", 6.25),
                 ("Alt-R", "ralt", 1.25), ("Win-R", "rmet", 1.25), ("Menu", None, 1.25), ("Ctrl-R", "rctl", 1.25)]
    phys = {"lalt": "Alt-L", "lmet": "Win-L", "ralt": "Alt-R", "rmet": "Win-R"}
    short = {"lmet": "Cmd", "lalt": "Opt", "rmet": "R Cmd", "ralt": "R Opt"}
    remap = []
    for src, pname in phys.items():
        e = by[src]["layers"]["base"]
        v = (e.get("device_variants") or {}).get("microsoft")
        if v is None:
            raise GenError(f"{src} no longer has a Microsoft-keyboard variant")
        if v["behaviour"] == "plain":
            emits = v["tap"]["kanata"]
            label = v["tap"]["label"]
            also = None
        else:
            outs = v["hold"].get("also_outputs") or []
            emits = outs[0]["kanata"]
            label = outs[0]["label"]
            also = "holds the " + v["hold"]["layer"] + " layer"
        item = {"physical": pname, "source": src, "emits": emits, "label": label, "legend": "→ " + short[emits]}
        if also:
            item["also"] = also
        remap.append(item)
    devices = {}
    for name, d in builder.devices.items():
        devices[name] = {"vendor_id": d["vendor_id"], "product_id": d["product_id"],
                         "usb_id": f"{d['vendor_id']:04x}:{d['product_id']:04x}"}
    return {
        "default": "macbook",
        "macbook": {"label": "MacBook (US ANSI), the default", "bottom_row": mac_bottom, "remap": []},
        "microsoft": {"label": "Microsoft keyboard (USB receiver)", "device": devices.get("microsoft"),
                      "bottom_row": [{"id": i, "source": s, "width_u": w} for i, s, w in ms_bottom], "remap": remap,
                      "note": "The remap applies when the most recent key press came from this device (kanata device-history). Its arrow cluster is not drawn."},
    }


def build_layers(cfg, keys, builder):
    acts = {"nav": [], "numbers-symbols": [], "practice": []}
    for k in keys:
        e = k["layers"]["base"]
        v = (e.get("device_variants") or {}).get("microsoft")
        variants = [("macbook" if v else "both", e)]
        if v:
            variants.append(("microsoft", v))
        for kb, ent in variants:
            h = ent.get("hold")
            if h and h["kind"] == "layer":
                scope = "full" if (k["kanata"] == builder.gate or h["layer"] == "numbers-symbols") else "partial"
                item = {"key": k["id"], "keyboard": kb, "after_ms": h.get("after_ms"), "scope": scope}
                if (ent.get("timing") or {}).get("hold_starts_when_another_key_is_pressed"):
                    item["starts_on_next_key"] = True
                acts[h["layer"]].append(item)
    acts["practice"].append({"key": "v", "keyboard": "both", "sequence": "violento-toggle", "scope": "full"})
    return [
        {"id": "base", "title": "Base / normal", "kanata_layer": "base", "kind": "default",
         "entry": "Default at startup; reached again by the Violento toggle chord", "activated_by": []},
        {"id": "nav", "title": "Caps navigation", "kanata_layer": "nav", "kind": "while-held",
         "entry": "Hold Caps (immediately when another key is pressed, else after 200 ms); Right Command (Right Alt on the Microsoft keyboard) gives the arrows only",
         "exit": "Release the key; a tap of Caps is Escape", "activated_by": acts["nav"]},
        {"id": "numbers-symbols", "title": "Held-Space numbers and symbols", "kanata_layer": "numbers-symbols", "kind": "while-held",
         "entry": "Hold bare Space for about 220 ms", "exit": "Release Space", "activated_by": acts["numbers-symbols"]},
        {"id": "practice", "title": "Violento practice", "kanata_layer": "practice", "kind": "toggle",
         "entry": "Control + Alt + GUI + V on the physical keys", "exit": "The same chord", "activated_by": acts["practice"]},
    ]


def event_of(out, **extra):
    d = {"key": out["event_key"], "code": out["event_code"], "flags": out["event_flags"]}
    d.update(extra)
    return d


def build_inventory(keys, inv, links_by_id):
    by = {k["id"]: k for k in keys}
    rows, problems = [], []
    verification = {"output-observed": "observed", "player-confirmed": "player_confirmed", "external-only": "external_only"}
    for r in inv["rows"]:
        spec = links_by_id[r["id"]]
        links, events = [], []
        for lk in spec["links"]:
            key = by.get(lk["key"])
            if key is None:
                problems.append(f"{r['id']}: unknown key {lk['key']!r}")
                continue
            ex = lk.get("expect", {})
            problems += [f"{r['id']}: {m}" for m in expect_failures(key, lk["layer"], ex)]
            links.append(lk)
            e = key["layers"][lk["layer"]]
            if lk["role"] == "output" and e.get("tap") and e["tap"].get("event_key"):
                events.append(event_of(e["tap"], source=lk["key"], layer=lk["layer"]))
            elif lk["role"] == "hold" and e.get("hold", {}).get("kind") == "modifier":
                events.append(event_of(e["hold"]["output"], source=lk["key"], layer=lk["layer"], after_ms=e["hold"].get("after_ms"), side_effect=True))
        seen, uniq = set(), []
        for ev in events:
            s_ = json.dumps(ev, sort_keys=True)
            if s_ not in seen:
                seen.add(s_)
                uniq.append(ev)
        lessons = sorted(set([r["introduced_in"]] + list(r.get("reviewed_in", []))))
        rows.append({
            "id": r["id"], "group": r["group"], "layer": r["layer"], "input": r["input"], "output": r["output"],
            "lessons": {"introduced": r["introduced_in"], "reviewed": r.get("reviewed_in", []), "all": lessons},
            "verification": verification[r["confidence"]], "links": links, "sequences": spec["sequences"],
            "observed": {"rule": spec["rule"], "events": uniq},
        })
    if problems:
        raise GenError("inventory links disagree with the parsed config:\n  " + "\n  ".join(problems))
    return rows


# --------------------------------------------------------------------------- assembly

def compact_outputs(node, table):
    """Move the browser-event data of every output into one table keyed by the kanata output name."""
    if isinstance(node, dict):
        if "event_key" in node:
            row = {k: node[k] for k in ("label", "event_key", "event_code", "event_flags", "typed") if k in node}
            old = table.setdefault(node["kanata"], row)
            if old != row:
                raise GenError(f"output {node['kanata']!r} has two different event descriptions")
            for k in ("event_key", "event_code", "event_flags", "typed"):
                node.pop(k, None)
        for v in list(node.values()):
            compact_outputs(v, table)
    elif isinstance(node, list):
        for v in node:
            compact_outputs(v, table)


def sha256_of(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def build_manifest(source_text, inventory, today, build_info=None):
    cfg = Config(source_text)
    b = Builder(cfg, source_text, inventory)
    keys = b.build_keys()
    import inventory_links
    links = inventory_links.build(inventory["rows"])
    sha = sha256_of(source_text)
    nlines = source_text.count("\n") + (0 if source_text.endswith("\n") else 1)
    seqs = build_sequences(cfg, keys)
    silenced = [k["id"] for k in keys if k["layers"]["practice"]["behaviour"] == "silent"]
    sw = sorted({k["id"] for k in keys for e in k["layers"].values()
                 if any(x.get("scope") == "swedish" for x in e.get("exceptions", []))})
    grave = next(k for k in keys if k["id"] == "`")
    inventory_rows = build_inventory(keys, inventory, links)
    outputs = {}
    compact_outputs(keys, outputs)
    manifest = {
        "schema_version": SCHEMA_VERSION,
        "manifest_version": f"{SCHEMA_VERSION}+{sha[:8]}",
        "generated": today,
        "generator": "design/layout/generate_manifest.py",
        "source": {"path": SOURCE_DISPLAY, "sha256": sha, "lines": nlines,
                   "process_unmapped_keys": cfg.defcfg.get("process-unmapped-keys") == "yes"},
        "scope": {"in": ["base", "nav", "numbers-symbols", "practice", "Microsoft modifier variant"],
                  "excluded": "Swedish letter remaps: the Option-held cases on [ ; ' are recorded as exceptions with scope swedish and are never taught",
                  "swedish_keys": sw},
        "assumptions": ["Keys that deflayermap numbers-symbols does not list are transparent (they fall to the layer below).",
                        "A nav output with requires_physical is produced only while that physical key is down; Right Command holds the nav layer but does not give those mappings."],
        "variables": {k: (cfg.var_list(k) if k.endswith("keys") else int(str(cfg.vars[k]))) for k in cfg.vars},
        "hands": {"left": b.left, "right": b.right},
        "timings": build_timings(keys),
        "layers": build_layers(cfg, keys, b),
        "keyboards": build_keyboards(cfg, keys, b),
        "outputs": dict(sorted(outputs.items())),
        "keys": keys,
        "sequences": seqs,
        "practice": {"silenced_keys": silenced,
                     "note": "Keys that practice maps to XX. Every key outside defsrc passes through (process-unmapped-keys yes), so grave, minus, equals and the other unmapped keys still type."},
        "reserved_keys": [
            {"character": "`", "key": "`", "role": "Hint key",
             "passthrough_on": [l for l in LAYERS if grave["layers"][l]["behaviour"] == "passthrough"]},
            {"character": "?", "key": "/", "role": "Layout help key", "gesture": "tap-hold F (left-hand Shift), then tap /"},
        ],
        "inventory": inventory_rows,
    }
    if build_info is not None:
        manifest["source"]["kanata"] = build_info
    return manifest, cfg


def dump(manifest):
    return json.dumps(manifest, indent=1, ensure_ascii=False) + "\n"


def read_build_info():
    try:
        d = json.loads(BUILD_INFO.read_text(encoding="utf-8"))
        return {"version": d.get("version"), "revision": d.get("revision"), "from": "~/.config/kanata/build-info.json"}
    except (OSError, ValueError):
        return None


def cross_check_nav_only(cfg):
    """Compare the aliases that navigation-only.kbd shares with kanata.kbd. Returns notes (never an error)."""
    if not NAV_ONLY.exists():
        return ["navigation-only.kbd not found, skipped"]
    try:
        other = Config(NAV_ONLY.read_text(encoding="utf-8"))
    except KbdError as e:
        return [f"navigation-only.kbd could not be read: {e}"]
    names = ("left-alt", "left-win", "right-alt", "right-win", "caps", "rnav", "left", "down", "up", "right", "homerow", "homerow-tab")
    shared = [n for n in cfg.aliases if n in other.aliases and (n.startswith("nav-") or n in names)]
    notes = []
    def effect(node):
        # what the alias does, ignoring how the nav-only file adds its Space marker (nop0) to conditions
        if node["kind"] == "switch":
            return [strip(c["then"]) for c in node["cases"]]
        return strip(node)

    for n in shared:
        a, c = effect(cfg.norm(cfg.aliases[n])), effect(other.norm(other.aliases[n]))
        if json.dumps(a, sort_keys=True) != json.dumps(c, sort_keys=True):
            notes.append(f"alias {n} does something different in navigation-only.kbd")
    return [f"cross-checked {len(shared)} shared aliases against navigation-only.kbd, {len(notes)} differ"] + notes


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="fail when the committed manifest no longer matches the live file")
    ap.add_argument("--stdout", action="store_true", help="print the manifest instead of writing it")
    args = ap.parse_args(argv)

    if not SOURCE.exists():
        if args.check:
            print(f"layout manifest: source not found ({SOURCE_DISPLAY}), skipped")
            return 0
        print(f"error: {SOURCE_DISPLAY} not found; generation needs the live file", file=sys.stderr)
        return 2
    text = SOURCE.read_text(encoding="utf-8")
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    committed = None
    if MANIFEST.exists():
        try:
            committed = json.loads(MANIFEST.read_text(encoding="utf-8"))
        except ValueError:
            committed = None
    today = datetime.date.today().isoformat()
    sha = sha256_of(text)
    if committed and committed.get("source", {}).get("sha256") == sha:
        today = committed.get("generated", today)
    build_info = read_build_info()
    if args.check and committed:
        build_info = committed.get("source", {}).get("kanata", build_info)
    try:
        manifest, cfg = build_manifest(text, inventory, today, build_info)
    except (KbdError, GenError, ValueError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 2
    out = dump(manifest)
    for note in cross_check_nav_only(cfg):
        print(f"note: {note}")
    if args.check:
        if not MANIFEST.exists():
            print("layout manifest: not committed yet; run generate_manifest.py", file=sys.stderr)
            return 1
        if MANIFEST.read_text(encoding="utf-8") == out:
            print(f"layout manifest: up to date with {SOURCE_DISPLAY} (sha256 {sha[:12]}, {manifest['source']['lines']} lines)")
            return 0
        old = committed.get("source", {}) if committed else {}
        why = "the source file changed" if old.get("sha256") != sha else "the generator or gesture-inventory.json changed"
        print(f"layout manifest: STALE ({why}); committed sha256 {str(old.get('sha256'))[:12]} vs live {sha[:12]}. "
              f"Run: python design/layout/generate_manifest.py, review the diff, commit it.", file=sys.stderr)
        return 1
    if args.stdout:
        sys.stdout.write(out)
        return 0
    MANIFEST.write_text(out, encoding="utf-8")
    try:
        import jsonschema
        schema = json.loads((HERE / "layout-manifest.schema.json").read_text(encoding="utf-8"))
        jsonschema.validate(manifest, schema)
    except ImportError:
        print("note: jsonschema not installed, schema not checked")
    except FileNotFoundError:
        print("note: layout-manifest.schema.json not found yet, schema not checked")
    print(f"wrote {MANIFEST.relative_to(ROOT)}: {len(manifest['keys'])} keys, {len(manifest['inventory'])} inventory rows, "
          f"source sha256 {sha[:12]}, {manifest['source']['lines']} lines")
    return 0


if __name__ == "__main__":
    sys.exit(main())

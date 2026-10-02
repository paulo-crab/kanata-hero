"""Reader for the subset of Kanata configuration syntax that ~/.config/kanata/kanata.kbd uses.

It turns the file into plain data (no behaviour is guessed): a tree of atoms and lists with line
numbers, the defsrc / defvar / defalias / deflayer / deflayermap forms, and a normaliser that
turns each action into a small dict ("kind": key, silent, transparent, tap-hold, layer-while-held,
layer-switch, multi, switch, fork, macro, unmod, reload, nop). Anything it does not recognise raises
KbdError with the line number, so a structural change in the config is loud instead of silently
producing a wrong manifest.

Used by generate_manifest.py; has no dependency outside the standard library.
"""

MODIFIERS = ("lctl", "rctl", "lalt", "ralt", "lmet", "rmet", "lsft", "rsft")
MOD_PREFIX = {"C": "lctl", "A": "lalt", "S": "lsft", "M": "lmet"}


class KbdError(Exception):
    pass


class Atom(str):
    line = 0


class Lst(list):
    line = 0


def _tokenize(text):
    toks, comments = [], []
    i, line, n = 0, 1, len(text)
    while i < n:
        c = text[i]
        if c == "\n":
            line += 1
            i += 1
        elif c in " \t\r":
            i += 1
        elif text.startswith(";;", i):
            j = i
            while j < n and text[j] != "\n":
                j += 1
            comments.append((line, text[i + 2:j].strip()))
            i = j
        elif text.startswith("#|", i):
            j = text.find("|#", i)
            if j < 0:
                raise KbdError(f"line {line}: unterminated block comment")
            line += text.count("\n", i, j)
            i = j + 2
        elif c in "()":
            toks.append((c, line))
            i += 1
        else:
            j = i
            while j < n and text[j] not in " \t\r\n()":
                j += 1
            toks.append((text[i:j], line))
            i = j
    return toks, comments


def parse(text):
    """Return (forms, comments). forms is a list of top-level Lst; comments is [(line, text)]."""
    toks, comments = _tokenize(text)
    pos = 0

    def read():
        nonlocal pos
        tok, line = toks[pos]
        pos += 1
        if tok == "(":
            node = Lst()
            node.line = line
            while True:
                if pos >= len(toks):
                    raise KbdError(f"line {line}: unclosed parenthesis")
                if toks[pos][0] == ")":
                    pos += 1
                    return node
                node.append(read())
        if tok == ")":
            raise KbdError(f"line {line}: unexpected )")
        a = Atom(tok)
        a.line = line
        return a

    forms = []
    while pos < len(toks):
        forms.append(read())
    return forms, comments


class Config:
    """The parsed file: source keys, variables, aliases and layers."""

    def __init__(self, text):
        forms, self.comments = parse(text)
        self.text = text
        self.src = []
        self.vars = {}
        self.aliases = {}
        self.alias_line = {}
        self.layers = {}          # name -> {"form": "deflayer"|"deflayermap", "entries": {src: node}, "line": n}
        self.layer_order = []
        self.defcfg = {}
        self.devices = {}
        for f in forms:
            if not isinstance(f, Lst) or not f or not isinstance(f[0], Atom):
                raise KbdError(f"line {f.line}: unexpected top-level form")
            head = str(f[0])
            if head == "defcfg":
                items = f[1:]
                for i in range(0, len(items) - 1, 2):
                    self.defcfg[str(items[i])] = str(items[i + 1])
            elif head == "defsrc":
                self.src = [str(x) for x in f[1:]]
            elif head == "defvar":
                items = f[1:]
                for i in range(0, len(items), 2):
                    self.vars[str(items[i])] = items[i + 1]
            elif head == "definputdevices":
                items = f[1:]
                for i in range(0, len(items), 2):
                    dev = {}
                    for kv in items[i + 1]:
                        dev[str(kv[0])] = int(kv[1]) if str(kv[1]).isdigit() else str(kv[1])
                    self.devices[str(items[i])] = dev
            elif head == "defalias":
                items = f[1:]
                if len(items) % 2:
                    raise KbdError(f"line {f.line}: defalias has an odd number of items")
                for i in range(0, len(items), 2):
                    name = str(items[i])
                    self.aliases[name] = items[i + 1]
                    self.alias_line[name] = items[i].line
            elif head == "deflayer":
                name = str(f[1])
                acts = list(f[2:])
                if len(acts) != len(self.src):
                    raise KbdError(f"line {f.line}: layer {name} has {len(acts)} actions for {len(self.src)} source keys")
                self.layers[name] = {"form": "deflayer", "entries": dict(zip(self.src, acts)), "line": f.line}
                self.layer_order.append(name)
            elif head == "deflayermap":
                name = str(f[1][0])
                items = list(f[2:])
                if len(items) % 2:
                    raise KbdError(f"line {f.line}: deflayermap {name} has an odd number of items")
                entries = {str(items[i]): items[i + 1] for i in range(0, len(items), 2)}
                self.layers[name] = {"form": "deflayermap", "entries": entries, "line": f.line}
                self.layer_order.append(name)
            else:
                raise KbdError(f"line {f.line}: unknown top-level form {head!r}")

    def var_list(self, name):
        v = self.vars[name]
        return [str(x) for x in v] if isinstance(v, Lst) else [str(v)]

    # ------------------------------------------------------------------ action normaliser
    def norm(self, n, _depth=0):
        if _depth > 12:
            raise KbdError(f"line {n.line}: alias nesting too deep")
        d = _depth + 1
        if isinstance(n, Atom):
            s = str(n)
            if s.startswith("@"):
                name = s[1:]
                if name not in self.aliases:
                    raise KbdError(f"line {n.line}: unknown alias {s}")
                out = dict(self.norm(self.aliases[name], d))
                out.setdefault("alias", name)
                return out
            if s.startswith("$"):
                name = s[1:]
                if name not in self.vars:
                    raise KbdError(f"line {n.line}: unknown variable {s}")
                return self.norm(self.vars[name], d)
            if s == "_":
                return {"kind": "transparent"}
            if s == "XX":
                return {"kind": "silent"}
            if s == "lrld":
                return {"kind": "reload"}
            if s == "nop0":
                return {"kind": "nop"}
            mods, key = [], s
            while len(key) > 2 and key[1] == "-" and key[0] in MOD_PREFIX:
                mods.append(MOD_PREFIX[key[0]])
                key = key[2:]
            return {"kind": "key", "key": key, "mods": mods}
        if not n:
            raise KbdError(f"line {n.line}: empty action list")
        head = str(n[0])
        args = n[1:]
        if head in ("tap-hold", "tap-hold-press", "tap-hold-tap-keys"):
            out = {"kind": "tap-hold", "variant": head}
            out["tap_ms"] = self._int(args[0])
            out["hold_ms"] = self._int(args[1])
            out["tap"] = self.norm(args[2], d)
            out["hold"] = self.norm(args[3], d)
            rest = args[4:]
            if head == "tap-hold-tap-keys":
                keys = rest[0]
                var = None
                if isinstance(keys, Atom) and str(keys).startswith("$"):
                    var = str(keys)[1:]
                    keys = self.vars[var]
                out["trigger_keys_var"] = var
                out["trigger_keys"] = [str(x) for x in keys]
                rest = rest[1:]
            out["require_prior_idle_ms"] = None
            for opt in rest:
                if isinstance(opt, Lst) and str(opt[0]) == "require-prior-idle":
                    out["require_prior_idle_ms"] = self._int(opt[1])
                else:
                    raise KbdError(f"line {n.line}: unknown tap-hold option {opt}")
            return out
        if head in ("layer-while-held", "layer-switch"):
            return {"kind": head, "layer": str(args[0])}
        if head == "multi":
            return {"kind": "multi", "actions": [self.norm(a, d) for a in args]}
        if head == "fork":
            return {"kind": "fork", "default": self.norm(args[0], d), "alternate": self.norm(args[1], d),
                    "when_held": [str(x) for x in args[2]]}
        if head == "macro":
            return {"kind": "macro", "steps": [self._macro_step(a, d) for a in args]}
        if head == "unmod":
            return self._unmod(n, args)
        if head == "switch":
            cases, i = [], 0
            while i < len(args):
                if i + 1 >= len(args):
                    raise KbdError(f"line {n.line}: switch case without an action")
                cond, act = args[i], args[i + 1]
                brk = str(args[i + 2]) if i + 2 < len(args) else None
                if brk not in ("break", "fallthrough"):
                    raise KbdError(f"line {n.line}: switch case needs break or fallthrough, got {brk!r}")
                cases.append({"when": self._cond(cond), "then": self.norm(act, d), "line": cond.line,
                              "mode": brk})
                i += 3
            return {"kind": "switch", "cases": cases}
        raise KbdError(f"line {n.line}: unrecognised action {head!r}")

    def _int(self, a):
        s = str(a)
        if s.startswith("$"):
            s = str(self.vars[s[1:]])
        if not s.lstrip("-").isdigit():
            raise KbdError(f"line {getattr(a, 'line', '?')}: expected a number, got {s!r}")
        return int(s)

    def _unmod(self, n, args):
        releases = "all"
        args = list(args)
        if args and isinstance(args[0], Lst):
            releases = [str(x) for x in args[0]]
            args = args[1:]
        names = [str(x) for x in args]
        if not names:
            raise KbdError(f"line {n.line}: unmod without a key")
        return {"kind": "unmod", "releases": releases, "mods": [x for x in names[:-1] if x in MODIFIERS],
                "key": names[-1], "extra": [x for x in names[:-1] if x not in MODIFIERS]}

    def _macro_step(self, a, d):
        if isinstance(a, Lst) and str(a[0]) == "unmod":
            return self._unmod(a, a[1:])
        if isinstance(a, Atom):
            return {"kind": "key", "key": str(a), "mods": []}
        raise KbdError(f"line {a.line}: unsupported macro step")

    def _cond(self, c):
        if not isinstance(c, Lst):
            raise KbdError(f"line {c.line}: switch condition must be a list")
        if not c:
            return {"default": True}
        return {"all": [self._term(t) for t in c]}

    def _term(self, t):
        if isinstance(t, Atom):
            return {"held": str(t)}
        head = str(t[0])
        if head in ("or", "and", "not"):
            return {"op": head, "args": [self._term(x) for x in t[1:]]}
        if head == "input":
            return {"input": [str(t[1]), str(t[2])]}
        if head == "device-history":
            return {"device_history": [int(str(t[1])), int(str(t[2]))]}
        raise KbdError(f"line {t.line}: unsupported switch condition {head!r}")

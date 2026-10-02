#!/usr/bin/env python3
"""Validate Kanata Hero level data.

Usage (from anywhere; paths resolve from this file's location):
    python design/levels/validate_levels.py design/levels/orientation
    python design/levels/validate_levels.py orientation records
    python design/levels/validate_levels.py --all
    python design/levels/validate_levels.py --selftest     (mutation tests for the newer rules)
    python design/levels/validate_levels.py --drop-solved-gaps orientation   (after the kit branch merges)
    add -v to list every warning, --strict to treat warnings as errors.

Exit code is non-zero when any error is found. Warnings cover art_gap props,
inventory rows owned by districts that have not landed yet, and documented
keyboard-inset conflicts. See SCHEMA.md for what each check means.
"""
import argparse
import json
import re
import sys
from collections import deque
from pathlib import Path

try:
    import jsonschema
except ImportError:  # pragma: no cover
    jsonschema = None

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
TILE = 16
DISTRICTS = ["orientation", "records", "systems", "nightshift", "executive"]
CHARACTERS = ["engineer", "ivo", "mira", "noor", "hal", "ada", "vale", "bgworker_a", "bgworker_b"]
CAST_ATLAS = {
    "engineer": "art-direction/gate1/engineer-full-atlas.json",
    "ivo": "art-direction/cast/ivo-atlas.json",
    "mira": "art-direction/cast/mira-atlas.json",
    "noor": "art-direction/cast/noor-atlas.json",
    "hal": "art-direction/cast/hal-atlas.json",
    "ada": "art-direction/cast/ada-atlas.json",
    "vale": "art-direction/cast/vale-atlas.json",
    "bgworker_a": "art-direction/cast/bgworker_a-atlas.json",
    "bgworker_b": "art-direction/cast/bgworker_b-atlas.json",
}
PACE_ATLAS = "art-direction/pace/pace-atlas.json"
PORTRAIT_ATLAS = "art-direction/portraits/portraits-atlas.json"
SCHEMA_PATH = HERE / "level-data.schema.json"
WORLD_PATH = HERE / "world.json"
INVENTORY_PATH = HERE / "gesture-inventory.json"

# Camera model used for the keyboard-inset check (docs/game-design.md, ui-kit/COMPONENTS.md).
VIEW_W, VIEW_H = 320, 180
AVATAR_SCREEN = (160, 100)  # feet anchor: centred, slightly below centre
INSET = (4, 103, 147, 176)  # x0, y0, x1, y1 in logical px (stage x 16-588, y 412-704 at x4)

TIME_KEY = re.compile(r"(time[_-]?limit|timeout|countdown|deadline|timer|seconds|time[_-]?remaining|par[_-]?time|speed[_-]?threshold|max[_-]?ms)", re.I)
HINT_VOCAB = re.compile(r"(tap|hold|physical|XX|stays|stay|literal|passes|still|Right Command|Command|Control|Shift)", re.I)
WHEN_KINDS = {
    "scene_success": "scene", "dialogue_done": "dialogue", "interact": "interaction", "step_done": "step",
    "reach_cell": "cell", "level_complete": "level", "step_start": "step", "trigger": "trigger", "state": "state",
    "request": "dialogue", "trigger_done": "trigger", "player_confirm": "scene",
    "any_of": "group", "count": "group",
}
# Keys reserved by the UI (design/ui-key-bindings.md, rule 5): in every typing scene `?` and Backtick are commands,
# so no scene may require the player to type either.
ABSENT = "absent"  # reserved NPC state: not in the district yet (null pose, no cell, no interaction)
RESERVED_CHARS = ("?", "`")
RESERVED_NAMES = {"backquote", "backtick", "grave", "shift+slash", "shift + slash", "question mark"}


class Report:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.infos = []

    def err(self, where, msg):
        self.errors.append(f"{where}: {msg}")

    def warn(self, where, msg):
        self.warnings.append(f"{where}: {msg}")

    def info(self, msg):
        self.infos.append(msg)


def load_json(path, rep):
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    except FileNotFoundError:
        rep.err(rel(path), "file not found")
    except json.JSONDecodeError as exc:
        rep.err(rel(path), f"invalid JSON: {exc}")
    return None


def rel(path):
    try:
        return str(Path(path).resolve().relative_to(ROOT))
    except ValueError:
        return str(path)


_schema_cache = {}


def schema_check(data, defname, where, rep):
    if jsonschema is None:
        if "schema" not in _schema_cache:
            rep.warn("schema", "jsonschema is not installed; shape checks skipped")
            _schema_cache["schema"] = True
        return True
    if "doc" not in _schema_cache:
        _schema_cache["doc"] = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    doc = _schema_cache["doc"]
    sch = {"$schema": doc["$schema"], "$ref": f"#/$defs/{defname}", "$defs": doc["$defs"]}
    validator = jsonschema.Draft202012Validator(sch)
    ok = True
    for e in sorted(validator.iter_errors(data), key=lambda e: list(e.absolute_path)):
        path = "/".join(str(p) for p in e.absolute_path) or "(root)"
        rep.err(where, f"schema: {path}: {e.message[:200]}")
        ok = False
    return ok


def walk_keys(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield f"{path}/{k}", k
            yield from walk_keys(v, f"{path}/{k}")
    elif isinstance(obj, list):
        for i, v in enumerate(obj):
            yield from walk_keys(v, f"{path}[{i}]")


# --------------------------------------------------------------------------- shared reference data

class Reference:
    """World, inventory, and art atlases loaded once."""

    def __init__(self, rep):
        self.rep = rep
        self.world = load_json(WORLD_PATH, rep)
        self.inventory = load_json(INVENTORY_PATH, rep)
        if self.world is not None:
            if schema_check(self.world, "world", rel(WORLD_PATH), rep):
                for msg in world_link_problems(self.world):
                    rep.err(rel(WORLD_PATH), msg)
        if self.inventory is not None:
            schema_check(self.inventory, "inventory", rel(INVENTORY_PATH), rep)
        self.rows = {r["id"]: r for r in (self.inventory or {}).get("rows", [])}
        self.cast = {}
        for ch, path in CAST_ATLAS.items():
            data = load_json(ROOT / path, rep)
            names = set()
            if data:
                names |= set(data.get("animations", {}))
                names |= set(data.get("variants", {}))
            self.cast[ch] = names
        pace = load_json(ROOT / PACE_ATLAS, rep) or {}
        entries = pace.get("entries", {})
        self.pace = entries if isinstance(entries, dict) else {e["name"]: e for e in entries}
        por = load_json(ROOT / PORTRAIT_ATLAS, rep) or {}
        self.portraits = set(por.get("portraits", {}))
        self.signatures = por.get("signatures", {})
        self._atlas = {}
        self.level_ids = set((self.world or {}).get("state_ids", {}).get("levels_done", []))
        self.seal_ids = set((self.world or {}).get("state_ids", {}).get("seals", []))
        self.artifact_ids = set((self.world or {}).get("state_ids", {}).get("artifacts", []))
        self.patch_ids = set((self.world or {}).get("state_ids", {}).get("patches", []))
        self.flag_ids = set((self.world or {}).get("state_ids", {}).get("flags", []))
        self.link_ids = {l["id"]: l for l in (self.world or {}).get("links", [])}
        self.mira_index = {m["id"]: m for m in (self.world or {}).get("mira_routes", [])}

    def atlas(self, kit_path):
        if kit_path not in self._atlas:
            self._atlas[kit_path] = load_json(ROOT / kit_path, self.rep)
        return self._atlas[kit_path]

    def district_of_level_number(self, n):
        for d in (self.world or {}).get("districts", []):
            if d["levels"][0] <= n <= d["levels"][1]:
                return d["id"]
        return None


def level_number(level_id):
    return int(level_id.rsplit("-", 1)[1])


def reserved_key_hits(task):
    """Labels of the task fields whose required text asks for a reserved key (? or Backtick).

    Only fields that carry text or keys the player must produce are read: target, targets, lines, accepts,
    items[].target and steps[].accepts. Prompts, questions and display strings may mention a question mark."""
    hits = []

    def check(label, val):
        if isinstance(val, str):
            if any(c in val for c in RESERVED_CHARS) or val.strip().lower() in RESERVED_NAMES:
                hits.append(label)
        elif isinstance(val, list):
            for i, item in enumerate(val):
                check(f"{label}[{i}]", item)

    for key in ("target", "targets", "lines", "accepts"):
        if key in task:
            check(key, task[key])
    for i, it in enumerate(task.get("items") or []):
        if isinstance(it, dict) and "target" in it:
            check(f"items[{i}].target", it["target"])
    for i, st in enumerate(task.get("steps") or []):
        if isinstance(st, dict) and "accepts" in st:
            check(f"steps[{i}].accepts", st["accepts"])
    return hits


def world_link_problems(world):
    """Messages for links whose shape is wrong. A panel link (a hidden panel between two districts) carries a
    cell in each district it joins and the seal that reveals it."""
    out = []
    for lk in (world or {}).get("links", []):
        if lk.get("kind") == "panel":
            if len(lk["between"]) != 2:
                out.append(f"link {lk['id']}: a panel link joins exactly two districts")
            if set(lk.get("cells", {})) != set(lk["between"]):
                out.append(f"link {lk['id']}: a panel link needs a cell for each of {lk['between']}")
            if not lk.get("seal_required"):
                out.append(f"link {lk['id']}: a panel link names the seal that reveals it")
    return out


# --------------------------------------------------------------------------- geometry

def in_bounds(cell, size):
    return 0 <= cell[0] < size[0] and 0 <= cell[1] < size[1]


def bfs(grid, start, goal=None, extra_open=frozenset()):
    """4-neighbour BFS over a collision grid (list of strings). Returns dist dict."""
    h, w = len(grid), len(grid[0])
    start = tuple(start)

    def walk(x, y):
        return grid[y][x] == "0" or (x, y) in extra_open

    if not (0 <= start[0] < w and 0 <= start[1] < h) or not walk(*start):
        return {}
    dist = {start: 0}
    q = deque([start])
    while q:
        x, y = q.popleft()
        if goal is not None and (x, y) == tuple(goal):
            break
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in dist and walk(nx, ny):
                dist[(nx, ny)] = dist[(x, y)] + 1
                q.append((nx, ny))
    return dist


def has_free_2x2(grid, cell, extra_open):
    x, y = cell
    h, w = len(grid), len(grid[0])

    def free(a, b):
        return 0 <= a < w and 0 <= b < h and (grid[b][a] == "0" or (a, b) in extra_open)

    for ox in (0, -1):
        for oy in (0, -1):
            if all(free(x + ox + i, y + oy + j) for i in (0, 1) for j in (0, 1)):
                return True
    return False


# --------------------------------------------------------------------------- district validation

class DistrictCheck:
    def __init__(self, ref, ddir, rep):
        self.ref = ref
        self.ddir = Path(ddir)
        self.rep = rep
        self.id = self.ddir.name
        self.district = None
        self.map = None
        self.levels = {}  # id -> data
        self.mira = {}
        self.coverage = None
        self.scenes = {}  # scene id -> (order_key, scene dict, owner label)
        self.dialogue_ids = {}
        self.trigger_ids = {}
        self.step_ids = {}
        self.atlas = None
        self.blocked = None  # derived blocked set
        self.placement_ids = {}
        self.gates = {}
        self.interactions = {}
        self.npcs = {}
        self.light_ids = set()
        self.conflict_notes = []

    def w(self, name):
        return f"{rel(self.ddir)}/{name}"

    # ---- loading
    def load(self):
        rep = self.rep
        if self.id not in DISTRICTS:
            rep.err(rel(self.ddir), f"directory name must be one of {DISTRICTS}")
        dj = load_json(self.ddir / "district.json", rep)
        mj = load_json(self.ddir / "map.json", rep)
        ok = True
        if dj is not None:
            ok &= schema_check(dj, "district", self.w("district.json"), rep)
            self.district = dj
        else:
            ok = False
        if mj is not None:
            ok &= schema_check(mj, "map", self.w("map.json"), rep)
            self.map = mj
        else:
            ok = False
        for p in sorted((self.ddir / "levels").glob("*.json")):
            d = load_json(p, rep)
            if d is None:
                continue
            ok &= schema_check(d, "level", self.w(f"levels/{p.name}"), rep)
            self.levels[d.get("id", p.stem)] = (p, d)
        for p in sorted((self.ddir / "mira").glob("*.json")):
            d = load_json(p, rep)
            if d is None:
                continue
            ok &= schema_check(d, "mira_route", self.w(f"mira/{p.name}"), rep)
            self.mira[d.get("id", p.stem)] = (p, d)
        cj = load_json(self.ddir / "coverage.json", rep)
        if cj is not None:
            ok &= schema_check(cj, "coverage", self.w("coverage.json"), rep)
            self.coverage = cj
        for name in ("LEVEL_SHEET.md", "NEEDS_ART.md"):
            if not (self.ddir / name).exists():
                rep.err(self.w(name), "required file is missing")
        return ok and self.district is not None and self.map is not None

    # ---- run all checks
    def run(self):
        if not self.load():
            self.rep.err(rel(self.ddir), "shape errors above prevent deeper checks")
            return
        self.check_basic()
        self.check_map_assets()
        self.check_collision()
        self.collect_ids()
        self.check_map_refs()
        self.check_routes()
        for lid, (p, d) in sorted(self.levels.items()):
            self.check_level(lid, p, d)
        for rid, (p, d) in sorted(self.mira.items()):
            self.check_mira(rid, p, d)
        self.check_district_refs()
        self.check_coverage()
        self.check_needs_art()
        self.check_inset()

    # ---- helpers
    def size(self):
        return self.map["size_cells"]

    def walkable(self, cell):
        return in_bounds(cell, self.size()) and self.map["collision"][cell[1]][cell[0]] == "0"

    def gate_cells_open(self, upto_number):
        cells = set()
        for g in self.gates.values():
            if level_number(g["opens_after"]) < upto_number:
                cells |= {tuple(c) for c in g["cells"]}
        return cells

    # ---- basic dimensions and identity
    def check_basic(self):
        d, m, rep = self.district, self.map, self.rep
        wd, wm = self.w("district.json"), self.w("map.json")
        if d["id"] != self.id:
            rep.err(wd, f"id {d['id']!r} does not match directory {self.id!r}")
        world_d = next((x for x in (self.ref.world or {}).get("districts", []) if x["id"] == self.id), None)
        if world_d and world_d["size_cells"] is not None and list(world_d["size_cells"]) != list(d["size_cells"]):
            rep.err(wd, f"size_cells {d['size_cells']} differs from world.json {world_d['size_cells']}")
        if list(d["size_cells"]) != list(m["size_cells"]):
            rep.err(wm, f"size_cells {m['size_cells']} differs from district.json {d['size_cells']}")
        w, h = m["size_cells"]
        for key in ("floor", "collision"):
            rows = m[key]
            if len(rows) != h:
                rep.err(wm, f"{key} has {len(rows)} rows, expected {h}")
            for y, row in enumerate(rows):
                if len(row) != w:
                    rep.err(wm, f"{key} row {y} has {len(row)} chars, expected {w}")
        for y, row in enumerate(m["collision"]):
            if set(row) - set("01"):
                rep.err(wm, f"collision row {y} has characters other than 0/1")
        cb = d["camera_bounds"]
        if cb["x"] + cb["w"] > w or cb["y"] + cb["h"] > h:
            rep.err(wd, "camera_bounds exceed the map")
        if cb["w"] < 20 or cb["h"] < 12:
            rep.warn(wd, "camera_bounds smaller than one 320x180 view (20x11.25 cells)")
        if not self.is_dim_ok():
            return
        if not in_bounds(d["hub_cell"], d["size_cells"]):
            rep.err(wd, "hub_cell out of bounds")

    def is_dim_ok(self):
        w, h = self.map["size_cells"]
        return len(self.map["collision"]) == h and all(len(r) == w for r in self.map["collision"]) \
            and len(self.map["floor"]) == h and all(len(r) == w for r in self.map["floor"])

    # ---- atlas names, placements
    def check_map_assets(self):
        d, m, rep = self.district, self.map, self.rep
        wm = self.w("map.json")
        self.atlas = self.ref.atlas(d["kit"])
        if not self.atlas:
            rep.err(self.w("district.json"), f"kit atlas {d['kit']} could not be loaded")
            self.atlas = {"entries": [], "animations": {}, "landmarks": {}}
        self.entries = {e["name"]: e for e in self.atlas.get("entries", [])}
        self.gap_entries = m.get("art_gap_entries", {})
        self.gap_sets = m.get("art_gap_state_sets", {})
        # floor legend
        legend = m["floor_legend"]
        for ch, name in legend.items():
            if name not in self.entries:
                rep.err(wm, f"floor_legend {ch!r}: {name!r} is not in the kit atlas")
        if self.is_dim_ok():
            for y, row in enumerate(m["floor"]):
                for x, ch in enumerate(row):
                    if ch not in legend:
                        rep.err(wm, f"floor ({x},{y}): key {ch!r} not in floor_legend")
                        break
        # gap definitions must be consistent
        for name, g in self.gap_entries.items():
            if name in self.entries:
                rep.warn(wm, f"art_gap_entries {name!r} now exists in the kit atlas; remove the gap")
            fp = g["footprint"]
            cw, ch_ = fp["cells"]
            if len(fp["collision"]) != ch_ or any(len(r) != cw for r in fp["collision"]):
                rep.err(wm, f"art_gap_entries {name!r}: collision rows do not match footprint cells {fp['cells']}")
        for sname, s in self.gap_sets.items():
            if s["default"] not in s["states"]:
                rep.err(wm, f"art_gap_state_sets {sname!r}: default state missing")
            for st, sd in s["states"].items():
                for en in sd["entries"]:
                    if en not in self.gap_entries and en not in self.entries:
                        rep.err(wm, f"art_gap_state_sets {sname}/{st}: entry {en!r} unknown")
        # placements
        gap_used = set()
        gap_count = {}
        for p in m["placements"]:
            pid = p["id"]
            where = f"{wm} placement {pid}"
            if not in_bounds(p["cell"], m["size_cells"]):
                rep.err(where, f"cell {p['cell']} is outside the map")
            if "landmark" in p:
                lm = self.atlas.get("landmarks", {}).get(p["landmark"])
                if lm is None:
                    rep.err(where, f"landmark {p['landmark']!r} not in the kit atlas")
                    continue
                st = p.get("state", lm["default_state"])
                if st not in lm["states"]:
                    rep.err(where, f"landmark state {st!r} unknown")
                continue
            name = p["entry"]
            is_gap = bool(p.get("art_gap"))
            in_kit = name in self.entries or name in self.ref.pace
            in_gap = name in self.gap_entries
            if is_gap:
                gap_used.add(name)
                if in_kit:
                    rep.warn(where, f"art_gap true but {name!r} already exists in the atlas")
                if not in_gap:
                    rep.err(where, f"art_gap entry {name!r} has no definition in map.art_gap_entries")
                else:
                    gap_count[name] = gap_count.get(name, 0) + 1
            elif not in_kit:
                rep.err(where, f"entry {name!r} is not in {d['kit']} or the Pace atlas; use art_gap true")
            if p.get("state_set"):
                ss = p["state_set"]
                sdef = self.atlas.get("animations", {}).get(ss) or self.gap_sets.get(ss)
                if sdef is None:
                    rep.err(where, f"state_set {ss!r} unknown")
                else:
                    st = p.get("state", sdef["default"])
                    if st not in sdef["states"]:
                        rep.err(where, f"state {st!r} not in state set {ss!r}")
                    elif not any(name in sd["entries"] for sd in sdef["states"].values()):
                        rep.err(where, f"entry {name!r} is not drawn in any state of {ss!r}")
            elif p.get("state"):
                rep.err(where, "state given without state_set")
        for name, n in gap_count.items():
            rep.warn(wm, f"art_gap prop {name!r} ({n} placement{'s' if n != 1 else ''}; see NEEDS_ART.md)")
        for name in self.gap_entries:
            if name not in gap_used and not any(name in sd["entries"] for s in self.gap_sets.values() for sd in s["states"].values()):
                rep.warn(wm, f"art_gap_entries {name!r} is defined but never placed")

    def entry_blocks(self, name):
        """Footprint collision rows for an entry name, from the kit, Pace atlas, or an art gap."""
        if name in self.entries:
            return self.entries[name]["collision"]
        if name in self.gap_entries:
            return self.gap_entries[name]["footprint"]["collision"]
        if name in self.ref.pace:
            e = self.ref.pace[name]
            fw, fh = e["footprint_cells"]
            rows = [["0"] * fw for _ in range(fh)]
            for cx, cy in e.get("collision_cells", []):
                rows[cy][cx] = "1"
            return ["".join(r) for r in rows]
        return []

    def placement_cells(self, p):
        """Set of blocked (x, y) cells for one placement, using kitlib's rules."""
        out = set()
        cx, cy = p["cell"]
        if "landmark" in p:
            lm = self.atlas.get("landmarks", {}).get(p["landmark"])
            if not lm:
                return out
            st = lm["states"].get(p.get("state", lm["default_state"]), {})
            fx = cx * TILE + p.get("offset", [0, 0])[0]
            fy = cy * TILE + p.get("offset", [0, 0])[1]
            for part in st.get("parts", []):
                for ry, row in enumerate(self.entry_blocks(part)):
                    for rx, c in enumerate(row):
                        if c == "1":
                            out.add((cx + rx, cy + ry))
            lamps = st.get("lamps")
            if lamps:
                lam_def = self.atlas["animations"][lamps["anim"]]["states"][lamps["state"]]["entries"]
                for dx, dy in lamps["offsets_px"]:
                    lx, ly = (fx + dx) // TILE, (fy + dy) // TILE
                    for en in lam_def:
                        for ry, row in enumerate(self.entry_blocks(en)):
                            for rx, c in enumerate(row):
                                if c == "1":
                                    out.add((lx + rx, ly + ry))
            return out
        names = [p["entry"]]
        if p.get("state_set"):
            ss = p["state_set"]
            sdef = self.atlas.get("animations", {}).get(ss) or self.gap_sets.get(ss)
            if sdef:
                st = p.get("state", sdef["default"])
                names = sdef["states"].get(st, {}).get("entries", names)
        for name in names:
            for ry, row in enumerate(self.entry_blocks(name)):
                for rx, c in enumerate(row):
                    if c == "1":
                        out.add((cx + rx, cy + ry))
        return out

    def check_collision(self):
        m, rep = self.map, self.rep
        wm = self.w("map.json")
        if not self.is_dim_ok():
            self.blocked = set()
            return
        w, h = m["size_cells"]
        derived = {}
        for p in m["placements"]:
            for c in self.placement_cells(p):
                if 0 <= c[0] < w and 0 <= c[1] < h:
                    derived.setdefault(c, []).append(p["id"])
        for x0, y0, rw, rh in m.get("implicit_walls", []):
            for yy in range(y0, y0 + rh):
                for xx in range(x0, x0 + rw):
                    if 0 <= xx < w and 0 <= yy < h:
                        derived.setdefault((xx, yy), []).append("implicit_wall")
        bad = 0
        for y in range(h):
            for x in range(w):
                want = (x, y) in derived
                got = m["collision"][y][x] == "1"
                if want != got and bad < 25:
                    bad += 1
                    if want:
                        rep.err(wm, f"collision ({x},{y}) is 0 but {derived[(x, y)]} blocks it")
                    else:
                        rep.err(wm, f"collision ({x},{y}) is 1 but no placement or implicit wall blocks it")
        self.blocked = {(x, y) for y in range(h) for x in range(w) if m["collision"][y][x] == "1"}

    # ---- id collection and uniqueness
    def collect_ids(self):
        m, d, rep = self.map, self.district, self.rep

        def uniq(label, items, key="id", store=None):
            seen = {}
            for it in items:
                v = it[key]
                if v in seen:
                    rep.err(self.w("map.json" if store is None else store), f"duplicate {label} id {v!r}")
                seen[v] = it
            return seen

        self.placement_ids = uniq("placement", m["placements"])
        self.interactions = uniq("interaction", m["interactions"])
        self.npcs = uniq("npc", m["npcs"])
        self.gates = uniq("gate", m.get("gates", []))
        uniq("zone", m["zones"])
        uniq("spawn", m["spawns"])
        self.light_ids = {l["id"] for l in d["light_states"]}
        uniq("light state", d["light_states"], store="district.json")
        uniq("entrance", d["entrances"], store="district.json")
        uniq("exit", d["exits"], store="district.json")

        global_seen = {}

        def reg(kind, ident, where):
            key = (kind, ident)
            if ident in global_seen.get(kind, {}):
                rep.err(where, f"duplicate {kind} id {ident!r} (also in {global_seen[kind][ident]})")
            global_seen.setdefault(kind, {})[ident] = where

        for lid, (p, lv) in sorted(self.levels.items()):
            wl = rel(p)
            reg("level", lv["id"], wl)
            order_base = lv["number"]
            for i, sc in enumerate(lv["terminal_scenes"]):
                reg("scene", sc["id"], wl)
                self.scenes[sc["id"]] = ((order_base, i), sc, lv["id"])
            for dl in lv["dialogue"]:
                reg("dialogue", dl["id"], wl)
                self.dialogue_ids[dl["id"]] = lv["id"]
            for st in lv["steps"]:
                reg("step", st["id"], wl)
                self.step_ids[st["id"]] = lv["id"]
            for tr in lv["triggers"]:
                reg("trigger", tr["id"], wl)
                self.trigger_ids[tr["id"]] = lv["id"]
        for rid, (p, mr) in sorted(self.mira.items()):
            wl = rel(p)
            base = level_number(mr["available_after"]) + 0.5
            for i, sc in enumerate(mr.get("terminal_scenes", [])):
                reg("scene", sc["id"], wl)
                self.scenes[sc["id"]] = ((base, i), sc, f"mira:{rid}")
            for dl in mr.get("dialogue", []):
                reg("dialogue", dl["id"], wl)
                self.dialogue_ids[dl["id"]] = f"mira:{rid}"
        for sq in d.get("side_quests", []):
            wl = self.w("district.json")
            base = level_number(sq["available_after"]) + 0.25
            for i, sc in enumerate(sq["terminal_scenes"]):
                reg("scene", sc["id"], wl)
                self.scenes[sc["id"]] = ((base, i), sc, f"side:{sq['id']}")
            for dl in sq.get("dialogue", []):
                reg("dialogue", dl["id"], wl)
                self.dialogue_ids[dl["id"]] = f"side:{sq['id']}"

    # ---- map references: cells, interactions, npcs, zones
    def check_map_refs(self):
        m, rep = self.map, self.rep
        wm = self.w("map.json")
        size = m["size_cells"]
        gate_cells_all = {tuple(c) for g in self.gates.values() for c in g["cells"]}
        for gid, g in self.gates.items():
            for c in g["cells"]:
                if not in_bounds(c, size):
                    rep.err(wm, f"gate {gid}: cell {c} out of bounds")
                elif not self.is_dim_ok() or tuple(c) not in self.blocked:
                    rep.err(wm, f"gate {gid}: cell {c} is not blocked in the initial collision (a gate must start closed)")
            if g.get("placement") and g["placement"] not in self.placement_ids:
                rep.err(wm, f"gate {gid}: placement {g['placement']!r} unknown")
            if g["opens_after"] not in self.ref.level_ids:
                rep.err(wm, f"gate {gid}: opens_after {g['opens_after']!r} is not a level id")
        for z in m["zones"]:
            x, y, rw, rh = z["rect"]
            if x + rw > size[0] or y + rh > size[1]:
                rep.err(wm, f"zone {z['id']}: rect outside the map")
        for iid, it in self.interactions.items():
            where = f"{wm} interaction {iid}"
            for c in it["cells"]:
                if not in_bounds(c, size):
                    rep.err(where, f"cell {c} out of bounds")
            if it["kind"] in ("terminal", "npc", "mira", "artifact", "door", "elevator", "sign") and not it.get("approach"):
                if self.is_dim_ok() and all(tuple(c) in self.blocked for c in it["cells"]):
                    rep.err(where, "blocked footprint needs approach cells (where the player stands)")
            for ap in it.get("approach", []):
                c = ap["cell"]
                if not self.is_dim_ok() or not in_bounds(c, size):
                    rep.err(where, f"approach {c} out of bounds")
                    continue
                if not self.walkable(c) and tuple(c) not in gate_cells_all:
                    rep.err(where, f"approach cell {c} is not walkable")
                near = any(abs(c[0] - fc[0]) + abs(c[1] - fc[1]) <= 1 for fc in it["cells"])
                if not near:
                    rep.err(where, f"approach cell {c} is not adjacent to the footprint")
            if it.get("scene_id") and it["scene_id"] not in self.scenes:
                rep.err(where, f"scene_id {it['scene_id']!r} is not defined in any level, route or side quest")
            if it.get("dialogue_id") and it["dialogue_id"] not in self.dialogue_ids:
                rep.err(where, f"dialogue_id {it['dialogue_id']!r} unknown")
            if it.get("npc") and it["npc"] not in self.npcs:
                rep.err(where, f"npc {it['npc']!r} unknown")
            if it.get("placement") and it["placement"] not in self.placement_ids:
                rep.err(where, f"placement {it['placement']!r} unknown")
            for req in it.get("requires", []):
                self.check_token(req, where)
            vw = it.get("visible_when", "")
            if vw.startswith("npc_state:"):
                mt = re.fullmatch(r"npc_state:([A-Za-z0-9_.\-]+)=([A-Za-z0-9_.\-*]+)", vw)
                if not mt:
                    rep.err(where, f"visible_when {vw!r}: use npc_state:<npc id>=<state> (a trailing * matches a prefix)")
                elif mt.group(1) not in self.npcs:
                    rep.err(where, f"visible_when {vw!r}: npc {mt.group(1)!r} unknown")
                else:
                    states = list(self.npcs[mt.group(1)]["poses_by_state"])
                    pat = mt.group(2)
                    hit = [s for s in states if (s.startswith(pat[:-1]) if pat.endswith("*") else s == pat)]
                    if not hit:
                        rep.err(where, f"visible_when {vw!r}: npc {mt.group(1)} has no state {pat!r}")
                    elif all(s == ABSENT for s in hit):
                        rep.err(where, f"visible_when {vw!r}: an NPC that is not present yet cannot be interacted with")
        for nid, n in self.npcs.items():
            where = f"{wm} npc {nid}"
            known = self.ref.cast.get(n["character"], set())
            cells = [n["start_cell"]] + list(n.get("patrol", [])) + list(n.get("cells_by_state", {}).values())
            for c in cells:
                if not in_bounds(c, size):
                    rep.err(where, f"cell {c} out of bounds")
                elif self.is_dim_ok() and not self.walkable(c):
                    rep.err(where, f"cell {c} is not walkable")
            for state, anim in n["poses_by_state"].items():
                if anim is None:
                    if state != ABSENT:
                        rep.err(where, f"state {state!r} has a null pose; only the reserved state {ABSENT!r} (NPC not present yet) may")
                elif known and anim not in known:
                    rep.err(where, f"pose {anim!r} (state {state}) is not an animation of {n['character']}")
            init = n.get("initial_state", "start")
            if init not in n["poses_by_state"]:
                rep.err(where, f"initial state {init!r} is not in poses_by_state")
            if ABSENT in n.get("cells_by_state", {}):
                rep.err(where, f"state {ABSENT!r} is not drawn and has no cell")
        for sp in m["spawns"]:
            if not in_bounds(sp["cell"], size) or (self.is_dim_ok() and not self.walkable(sp["cell"])):
                rep.err(wm, f"spawn {sp['id']}: cell {sp['cell']} is not walkable")

    def check_token(self, tok, where):
        kind, _, arg = tok.partition(":")
        ok = {
            "level": arg in self.ref.level_ids,
            "seal": arg in self.ref.seal_ids,
            "flag": arg in self.ref.flag_ids,
            "artifact": arg in self.ref.artifact_ids,
            "mira": arg in self.ref.mira_index,
        }.get(kind)
        if ok is None:
            self.rep.err(where, f"requirement {tok!r}: prefix must be level:, seal:, flag:, artifact: or mira:")
        elif not ok:
            self.rep.err(where, f"requirement {tok!r}: unknown id")

    # ---- routes
    def check_routes(self):
        m, rep, d = self.map, self.rep, self.district
        wm = self.w("map.json")
        if not self.is_dim_ok():
            return
        grid = m["collision"]
        size = m["size_cells"]
        for seg in m["routes"]["main"]:
            n = level_number(seg["level"])
            opened = self.gate_cells_open(n)
            where = f"{wm} routes.main {seg['level']}"
            self.check_path(seg["cells"], seg["from"], seg["to"], opened, where)
            dist = bfs(grid, seg["from"], seg["to"], opened)
            if tuple(seg["to"]) not in dist:
                rep.err(where, f"BFS: {seg['to']} is not reachable from {seg['from']}")
            width = seg.get("min_width", 2)
            if width >= 2:
                for c in seg["cells"]:
                    if not has_free_2x2(grid, c, opened):
                        rep.err(where, f"cell {c} is narrower than 2 cells (add min_width 1 only where levels.md allows)")
                        break
        for bt in m["routes"]["backtrack"]:
            where = f"{wm} routes.backtrack {bt['id']}"
            opened = self.gate_cells_open(21)
            self.check_path(bt["cells"], bt["from"], bt["to"], opened, where)
            after = level_number(bt["after"]) if bt.get("after") else 0
            if bt.get("after"):
                with_gate = bfs(grid, bt["from"], bt["to"], self.gate_cells_open(21))
                before = bfs(grid, bt["from"], bt["to"], self.gate_cells_open(after))
                wd, bd = with_gate.get(tuple(bt["to"])), before.get(tuple(bt["to"]))
                if wd is None:
                    rep.err(where, "not reachable even with every gate open")
                elif bd is not None and wd >= bd:
                    rep.warn(where, f"shortcut does not shorten the walk ({wd} cells vs {bd} before {bt['after']})")
                elif bd is not None:
                    rep.info(f"backtrack {bt['id']}: {bd} cells before {bt['after']}, {wd} after")
        # entrance to every approach cell and exit with all gates open
        opened_all = self.gate_cells_open(21)
        for ent in d["entrances"]:
            start = ent["cell"]
            if not self.walkable(start):
                rep.err(self.w("district.json"), f"entrance {ent['id']}: cell {start} is not walkable")
                continue
            dist = bfs(grid, start, None, opened_all)
            for iid, it in self.interactions.items():
                for ap in it.get("approach", []):
                    if tuple(ap["cell"]) not in dist and tuple(ap["cell"]) not in opened_all:
                        rep.err(f"{wm} interaction {iid}", f"approach {ap['cell']} unreachable from entrance {ent['id']}")
            for ex in d["exits"]:
                if tuple(ex["cell"]) not in dist and tuple(ex["cell"]) not in opened_all:
                    rep.err(self.w("district.json"), f"exit {ex['id']} cell {ex['cell']} unreachable from entrance {ent['id']}")
        # level-by-level reachability of required interactions: each level's step interactions are reachable
        # at that level's progress state (gates that open after earlier levels only).
        for lid, (p, lv) in sorted(self.levels.items()):
            n = lv["number"]
            opened = self.gate_cells_open(n)
            for st in lv["steps"]:
                it = self.interactions.get(st["interaction"]) if st["interaction"] else None
                if not it:
                    continue
                if st.get("optional"):
                    continue
                for ap in it.get("approach", [])[:1]:
                    start = d["entrances"][0]["cell"]
                    dist = bfs(grid, start, None, opened)
                    if tuple(ap["cell"]) not in dist:
                        rep.err(rel(p), f"step {st['id']}: approach {ap['cell']} of {it['id']} not reachable before level {n} completes")

    def check_path(self, cells, a, b, opened, where):
        if not cells:
            self.rep.err(where, "empty route cells")
            return
        if list(cells[0]) != list(a) or list(cells[-1]) != list(b):
            self.rep.err(where, "cells must start at 'from' and end at 'to'")
        for i, c in enumerate(cells):
            if not in_bounds(c, self.size()):
                self.rep.err(where, f"cell {c} out of bounds")
                return
            if not (self.walkable(c) or tuple(c) in opened):
                self.rep.err(where, f"cell {c} is not walkable at this progress state")
                return
            if i and abs(c[0] - cells[i - 1][0]) + abs(c[1] - cells[i - 1][1]) != 1:
                self.rep.err(where, f"cells {cells[i - 1]} -> {c} are not 4-neighbour steps")
                return

    # ---- when-grammar
    def check_when(self, text, where, kinds=None, allow_request=False):
        for atom in [a.strip() for a in text.split("&")]:
            self.check_atom(atom, where, allow_request)

    def check_atom(self, atom, where, allow_request=False, nested=False):
        """One condition atom. `any_of:<atom>|<atom>` holds when one alternative holds; `count:<n>:<atom>|<atom>|...`
        holds when at least n alternatives hold. Groups do not nest and never contain `request:`."""
        kind, _, arg = atom.partition(":")
        if kind not in WHEN_KINDS:
            self.rep.err(where, f"when {atom!r}: unknown kind {kind!r} (allowed: {', '.join(sorted(WHEN_KINDS))})")
            return
        what = WHEN_KINDS[kind]
        if kind == "request" and not allow_request:
            self.rep.err(where, f"when {atom!r}: request: atoms are Hint key requests and may only be the whole `when` of an on_request hint line")
            return
        if what == "group":
            if nested:
                self.rep.err(where, f"when {atom!r}: any_of and count do not nest")
                return
            need = None
            rest = arg
            if kind == "count":
                num, _, rest = arg.partition(":")
                if not num.isdigit() or int(num) < 1:
                    self.rep.err(where, f"when {atom!r}: count needs a positive integer first (count:<n>:<atom>|<atom>)")
                    return
                need = int(num)
            alts = [a.strip() for a in rest.split("|")]
            if len(alts) < 2 or any(not a for a in alts):
                self.rep.err(where, f"when {atom!r}: {kind} needs at least two non-empty alternatives separated by |")
                return
            if need is not None and need > len(alts):
                self.rep.err(where, f"when {atom!r}: count {need} is more than the {len(alts)} alternatives")
            for a in alts:
                self.check_atom(a, where, False, nested=True)
            return
        ok = True
        if what == "scene":
            ok = arg in self.scenes
        elif what == "dialogue":
            ok = arg in self.dialogue_ids
        elif what == "interaction":
            ok = arg in self.interactions
        elif what == "step":
            ok = arg in self.step_ids
        elif what == "trigger":
            ok = arg in self.trigger_ids
        elif what == "level":
            ok = arg in self.ref.level_ids
        elif what == "cell":
            mt = re.fullmatch(r"(\d+),(\d+)", arg)
            ok = bool(mt) and in_bounds([int(mt.group(1)), int(mt.group(2))], self.size())
        elif what == "state":
            ok = arg == "start" or arg in self.ref.level_ids or arg in self.ref.flag_ids
        if not ok:
            self.rep.err(where, f"when {atom!r}: {what} {arg!r} not found")

    # ---- level checks
    def check_level(self, lid, path, lv):
        rep = self.rep
        wl = rel(path)
        m = self.map
        n = lv["number"]
        if lv["district"] != self.id:
            rep.err(wl, f"district {lv['district']!r} does not match directory")
        if lv["id"] != f"{self.id}-{n:02d}":
            rep.err(wl, f"id {lv['id']!r} must be {self.id}-{n:02d}")
        mt = re.match(r"(\d\d)-", path.name)
        if not mt or int(mt.group(1)) != n:
            rep.err(wl, "file name must start with the two-digit level number")
        world_d = next((x for x in (self.ref.world or {}).get("districts", []) if x["id"] == self.id), None)
        if world_d and not (world_d["levels"][0] <= n <= world_d["levels"][1]):
            rep.err(wl, f"level {n} is outside this district's range {world_d['levels']}")
        for path_, key in walk_keys(lv):
            if TIME_KEY.search(key):
                rep.err(wl, f"field {path_} looks like a time limit; story levels are untimed")
        for req in lv["requires"]:
            if req.startswith(self.id + "-") or req in self.ref.level_ids:
                if req not in self.ref.level_ids:
                    rep.err(wl, f"requires {req!r}: unknown level")
            else:
                self.check_token(req, wl)
        # steps
        for st in lv["steps"]:
            if st["interaction"] and st["interaction"] not in self.interactions:
                rep.err(wl, f"step {st['id']}: interaction {st['interaction']!r} not in map.json")
            self.check_when(st["completes_when"], f"{wl} step {st['id']}")
            if st.get("target_cell") and not self.walkable(st["target_cell"]):
                rep.err(wl, f"step {st['id']}: target_cell {st['target_cell']} not walkable")
        # scenes
        for sc in lv["terminal_scenes"]:
            self.check_scene(sc, wl)
        # gestures
        scene_ids = {s["id"] for s in lv["terminal_scenes"]}
        for gu in lv["gestures"]:
            if gu["id"] not in self.ref.rows:
                rep.err(wl, f"gesture {gu['id']!r} is not in gesture-inventory.json")
            if gu["scene_id"] not in self.scenes:
                rep.err(wl, f"gesture {gu['id']}: scene_id {gu['scene_id']!r} not defined")
        # dialogue
        for dl in lv["dialogue"]:
            self.check_dialogue(dl, wl)
        # triggers
        for tr in lv["triggers"]:
            where = f"{wl} trigger {tr['id']}"
            self.check_when(tr["when"], where)
            for op in tr["then"]:
                self.check_op(op, where)
        # state changes
        sc_ = lv["state_changes"]
        if len(sc_["visible_changes"]) < 2:
            rep.err(wl, "state_changes.visible_changes needs at least 2 entries on a main or review level")
        for vc in sc_["visible_changes"]:
            self.check_visible_change(vc, wl)
        # rewards
        rw = lv["rewards"]
        if rw.get("seal") and rw["seal"] not in self.ref.seal_ids:
            rep.err(wl, f"rewards.seal {rw['seal']!r} is not in world.json")
        if rw.get("seal"):
            ws = next((s for s in (self.ref.world or {}).get("seals", []) if s["id"] == rw["seal"]), None)
            if ws and ws["level"] != lv["id"]:
                rep.err(wl, f"seal {rw['seal']} belongs to {ws['level']}")
        if lv["kind"] == "review" and not rw.get("seal"):
            rep.err(wl, "a review level must grant its seal")
        if rw.get("artifact") and rw["artifact"] not in self.ref.artifact_ids:
            rep.err(wl, f"rewards.artifact {rw['artifact']!r} is not in world.json")
        if rw.get("patch") and rw["patch"] not in self.ref.patch_ids:
            rep.err(wl, f"rewards.patch {rw['patch']!r} is not in world.json")
        oa = lv.get("optional_artifact")
        if oa:
            if oa["id"] not in self.ref.artifact_ids:
                rep.err(wl, f"optional_artifact {oa['id']!r} is not in world.json")
            it = self.interactions.get(oa["interaction"])
            if not it or it["kind"] != "artifact":
                rep.err(wl, f"optional_artifact interaction {oa['interaction']!r} must be an artifact interaction in map.json")
            if oa.get("placement") and oa["placement"] not in self.placement_ids:
                rep.err(wl, f"optional_artifact placement {oa['placement']!r} unknown")
        gl = lv.get("glitch")
        if gl:
            if not self.walkable(gl["cell"]):
                rep.err(wl, f"glitch cell {gl['cell']} not walkable")
            if gl.get("interaction") and gl["interaction"] not in self.interactions:
                rep.err(wl, f"glitch interaction {gl['interaction']!r} unknown")
        for pc in lv.get("pace_copy", []):
            if pc.get("placement"):
                if pc["placement"] not in self.placement_ids:
                    rep.err(wl, f"pace_copy placement {pc['placement']!r} unknown")
        if "1366" not in lv["review_notes"]:
            rep.warn(wl, "review_notes should record the 1366x768 + keyboard inset check")
        # every interaction naming this level exists with a scene
        # (checked from the interaction side in check_map_refs)

    def check_scene(self, sc, wl):
        rep = self.rep
        where = f"{wl} scene {sc['id']}"
        if sc["kind"] != "walk" and not sc.get("task"):
            rep.err(where, "non-walk scenes need a concrete 'task' object (prompt, targets, accepted outputs)")
        if sc["kind"] in ("label", "form", "editor", "keypad", "log"):
            task = sc.get("task", {})
            if not any(k in task for k in ("target", "targets", "items", "steps", "lines")):
                rep.err(where, "task needs target, targets, items, steps or lines")
        if "position_cue" not in sc and sc["kind"] != "walk":
            rep.warn(where, "position_cue not stated (recall scenes must say false)")
        for label in reserved_key_hits(sc.get("task") or {}):
            rep.err(where, f"task.{label} requires typing ? or Backtick, which are reserved UI keys (Layout help and Hint) in every typing scene")

    def check_dialogue(self, dl, wl):
        rep = self.rep
        where = f"{wl} dialogue {dl['id']}"
        speaker = dl["speaker"]
        kind = dl.get("speaker_kind") or ("character" if speaker in CHARACTERS else "object")
        if kind == "character":
            if speaker not in CHARACTERS:
                rep.err(where, f"speaker {speaker!r} is not a character id")
            if not dl["portrait"]:
                rep.err(where, "character lines need a portrait")
            else:
                key = f"{speaker}_{dl['portrait']}"
                if key not in self.ref.portraits:
                    rep.err(where, f"portrait {key!r} is not in portraits-atlas.json")
        else:
            if dl["portrait"] is not None:
                rep.err(where, "object speakers (cards, signs, panels) have no portrait; use null")
        if dl["hint"] is not None:
            h = dl["hint"]
            if kind == "character" and dl["portrait"] != "neutral":
                rep.err(where, "every hint line uses the neutral portrait (levels.md Portrait cue map)")
            if h["key"] not in h["action"]:
                rep.err(where, f"hint.key {h['key']!r} does not appear in hint.action")
            if not HINT_VOCAB.search(h["gesture"]):
                rep.warn(where, "hint.gesture does not use Kanata vocabulary (tap, tap-hold, physical, XX, stays)")
            if h["action"] not in dl["text"] and h["action"].rstrip(".") not in dl["text"]:
                rep.warn(where, "hint.action is not contained in text; text should lead with the action sentence")
        # Dialogue modes (design/ui-key-bindings.md "Dialogue has two modes"): a hint-bearing line is an instruction
        # line that takes no keys; only a conversation line owns Return and Esc.
        if dl["hint"] is not None and dl.get("modal") is True:
            rep.err(where, "a line with a hint is an instruction line: modal must be false or absent (a modal line would own Esc before the popup it describes sees it)")
        # A request is the player pressing the Hint key (Backtick). Only an on_request line answers one, and it answers with the hint.
        if dl.get("on_request"):
            if dl["hint"] is None:
                rep.err(where, "an on_request line answers a Hint key request and must carry a hint")
            if not re.fullmatch(r"request:[^&|\s]+", (dl.get("when") or "").strip()):
                rep.err(where, "an on_request line's when must be exactly request:<dialogue id> (the Hint key was pressed on that line)")
        if dl.get("when"):
            self.check_when(dl["when"], where, allow_request=bool(dl.get("on_request")))

    def check_op(self, op, where):
        rep = self.rep
        name = op["op"]

        def need(key, store, label):
            v = op.get(key)
            if v is None:
                rep.err(where, f"op {name}: missing {key}")
            elif v not in store:
                rep.err(where, f"op {name}: {label} {v!r} unknown")

        if name == "set_state":
            need("target", self.placement_ids, "placement")
            p = self.placement_ids.get(op.get("target"))
            if p and p.get("state_set") and "state" in op:
                sdef = self.atlas.get("animations", {}).get(p["state_set"]) or self.gap_sets.get(p["state_set"])
                if sdef and op["state"] not in sdef["states"]:
                    rep.err(where, f"op set_state: state {op['state']!r} not in {p['state_set']}")
            if p and "landmark" in p:
                lm = self.atlas.get("landmarks", {}).get(p["landmark"])
                if lm and op.get("state") not in lm["states"]:
                    rep.err(where, f"op set_state: landmark state {op.get('state')!r} unknown")
        elif name == "npc_state":
            need("npc", self.npcs, "npc")
            n = self.npcs.get(op.get("npc"))
            if n and op.get("state") not in n["poses_by_state"]:
                rep.err(where, f"op npc_state: state {op.get('state')!r} not in poses_by_state of {op.get('npc')}")
        elif name == "unlock_gate":
            need("gate", self.gates, "gate")
        elif name == "light_state":
            need("light_state", self.light_ids, "light state")
        elif name == "start_dialogue":
            need("dialogue", self.dialogue_ids, "dialogue")
        elif name == "spawn_glitch":
            if op.get("interaction") and op["interaction"] not in self.interactions:
                rep.err(where, f"op spawn_glitch: interaction {op['interaction']!r} unknown")
        elif name == "set_flag":
            if op.get("flag") not in self.ref.flag_ids:
                rep.err(where, f"op set_flag: flag {op.get('flag')!r} is not in world.json state_ids.flags")
        elif name == "complete_level":
            if op.get("level") not in self.ref.level_ids:
                rep.err(where, f"op complete_level: {op.get('level')!r} is not a level id")
        elif name == "grant":
            kind = op.get("kind")
            val = op.get("id")
            store = {"seal": self.ref.seal_ids, "artifact": self.ref.artifact_ids, "patch": self.ref.patch_ids}.get(kind)
            if store is None:
                if kind not in ("desk_decoration",):
                    rep.err(where, "op grant: kind must be seal, artifact, patch or desk_decoration")
            elif val not in store:
                rep.err(where, f"op grant: {kind} {val!r} is not in world.json")

    def check_visible_change(self, vc, wl):
        rep = self.rep
        kind, target = vc["kind"], vc["target"]
        where = f"{wl} visible_change {target}"
        store = {
            "placement_state": self.placement_ids, "landmark_state": self.placement_ids, "npc_pose": self.npcs,
            "light_state": self.light_ids, "gate": self.gates,
        }[kind]
        if target not in store:
            rep.err(where, f"{kind} target {target!r} does not exist in the district")
            return
        if kind == "placement_state":
            p = self.placement_ids[target]
            if not p.get("state_set"):
                rep.err(where, "placement has no state_set, so it cannot change state; use an animation state set")
            else:
                sdef = self.atlas.get("animations", {}).get(p["state_set"]) or self.gap_sets.get(p["state_set"])
                if sdef and vc["to"] not in sdef["states"]:
                    rep.err(where, f"state {vc['to']!r} not in {p['state_set']}")
        elif kind == "landmark_state":
            p = self.placement_ids[target]
            lm = self.atlas.get("landmarks", {}).get(p.get("landmark", ""))
            if not lm:
                rep.err(where, "placement is not a landmark")
            elif vc["to"] not in lm["states"]:
                rep.err(where, f"landmark state {vc['to']!r} unknown")
        elif kind == "npc_pose":
            if vc["to"] not in self.npcs[target]["poses_by_state"] and vc["to"] not in self.npcs[target].get("cells_by_state", {}):
                rep.err(where, f"state {vc['to']!r} is not a pose state of npc {target}")

    # ---- Mira routes
    def check_mira(self, rid, path, mr):
        rep = self.rep
        wl = rel(path)
        m = self.map
        if mr["district"] != self.id:
            rep.err(wl, "district does not match directory")
        idx = self.ref.mira_index.get(mr["id"])
        if not idx:
            rep.err(wl, f"route {mr['id']!r} is not in world.json mira_routes")
        else:
            if idx["district"] != mr["district"] or idx["available_after"] != mr["available_after"]:
                rep.err(wl, "district/available_after differ from world.json")
            if idx["patch"] != mr["reward_patch"]:
                rep.err(wl, f"reward_patch {mr['reward_patch']!r} differs from world.json ({idx['patch']!r})")
        mt = re.match(r"(\d\d)-", path.name)
        if not mt or int(mt.group(1)) != level_number(mr["available_after"]):
            rep.warn(wl, "file name NN should be the level number the route follows")
        for g in mr["skills_required"]:
            if g not in self.ref.rows:
                rep.err(wl, f"skill {g!r} is not in gesture-inventory.json")
        for path_, key in walk_keys(mr):
            if TIME_KEY.search(key) and key not in ("medal_rule",):
                rep.err(wl, f"field {path_} looks like a time limit; use the medal_rule text only")
        opened = self.gate_cells_open(level_number(mr["available_after"]) + 1)
        grid = m["collision"]
        start = mr["start_cell"]
        dist = bfs(grid, start, None, opened)
        if not dist:
            rep.err(wl, f"start_cell {start} is not walkable")
        route_cells = m["routes"]["mira"].get(mr["id"])
        if route_cells is None:
            rep.err(wl, f"map.json routes.mira has no entry for {mr['id']!r}")
        elif [list(c["cell"]) for c in mr["checkpoints"]] != [list(c) for c in route_cells]:
            rep.err(wl, "checkpoint cells differ from map.json routes.mira")
        prev = tuple(start)
        for cp in mr["checkpoints"]:
            c = tuple(cp["cell"])
            if c not in dist:
                rep.err(wl, f"checkpoint {cp['id']}: {list(c)} is not reachable from the start")
            if cp["scene_id"] not in self.scenes:
                rep.err(wl, f"checkpoint {cp['id']}: scene {cp['scene_id']!r} not defined")
            if cp.get("interaction") and cp["interaction"] not in self.interactions:
                rep.err(wl, f"checkpoint {cp['id']}: interaction {cp['interaction']!r} unknown")
        for gu in mr.get("gestures", []):
            if gu["id"] not in self.ref.rows:
                rep.err(wl, f"gesture {gu['id']!r} unknown")
            if gu["scene_id"] not in self.scenes:
                rep.err(wl, f"gesture {gu['id']}: scene {gu['scene_id']!r} undefined")
        for sc in mr.get("terminal_scenes", []):
            self.check_scene(sc, wl)
        for dl in mr.get("dialogue", []):
            self.check_dialogue(dl, wl)
        # the route should visit each checkpoint and return: loop length through BFS
        if dist and mr["checkpoints"]:
            total = 0
            cur = tuple(start)
            for cp in mr["checkpoints"] + [{"cell": start}]:
                d_ = bfs(grid, cur, tuple(cp["cell"]), opened)
                if tuple(cp["cell"]) in d_:
                    total += d_[tuple(cp["cell"])]
                cur = tuple(cp["cell"])
            self.rep.info(f"mira route {mr['id']}: loop of {total} cells over {len(mr['checkpoints'])} checkpoints")

    # ---- district-level refs
    def check_district_refs(self):
        d, rep = self.district, self.rep
        wd = self.w("district.json")
        size = self.map["size_cells"]
        world = self.ref.world or {}
        if not self.walkable(d["hub_cell"]):
            rep.err(wd, f"hub_cell {d['hub_cell']} not walkable")
        gate_cells_all = {tuple(c) for g in self.gates.values() for c in g["cells"]}
        for ent in d["entrances"]:
            lk = self.ref.link_ids.get(ent["from"]["link"])
            if not lk:
                rep.err(wd, f"entrance {ent['id']}: link {ent['from']['link']!r} not in world.json")
            elif ent["from"]["district"] not in lk["between"] or self.id not in lk["between"]:
                rep.err(wd, f"entrance {ent['id']}: link {lk['id']} is between {lk['between']}")
        for ex in d["exits"]:
            lk = self.ref.link_ids.get(ex["to"]["link"])
            if not lk:
                rep.err(wd, f"exit {ex['id']}: link {ex['to']['link']!r} not in world.json")
            elif ex["to"]["district"] not in lk["between"] or self.id not in lk["between"]:
                rep.err(wd, f"exit {ex['id']}: link {lk['id']} is between {lk['between']}")
            link_cell = (lk or {}).get("cells", {}).get(self.id)
            if link_cell and list(ex["cell"]) != list(link_cell):
                rep.err(wd, f"exit {ex['id']}: cell {ex['cell']} differs from world.json link {lk['id']} cell {link_cell} for {self.id}")
            if not in_bounds(ex["cell"], size):
                rep.err(wd, f"exit {ex['id']}: cell out of bounds")
            elif not self.walkable(ex["cell"]) and tuple(ex["cell"]) not in gate_cells_all:
                rep.err(wd, f"exit {ex['id']}: cell {ex['cell']} is blocked and not part of a gate")
            if ex.get("gate") and ex["gate"] not in self.gates:
                rep.err(wd, f"exit {ex['id']}: gate {ex['gate']!r} unknown")
        el = d["elevator"]
        if el["placement"] not in self.placement_ids:
            rep.err(wd, f"elevator placement {el['placement']!r} not in map.json")
        stop = next((x for x in world.get("districts", []) if x["id"] == self.id), None)
        if stop and el["link"] != stop["elevator_stop"]["link"]:
            rep.err(wd, f"elevator link {el['link']!r} differs from world.json {stop['elevator_stop']['link']!r}")
        for c in (el["cell"], el.get("arrival_cell")):
            if c and not in_bounds(c, size):
                rep.err(wd, f"elevator cell {c} out of bounds")
        if el.get("arrival_cell") and not self.walkable(el["arrival_cell"]):
            rep.err(wd, f"elevator arrival_cell {el['arrival_cell']} not walkable")
        for ls in d["light_states"]:
            if ls["applies_when"] not in self.trigger_ids:
                rep.err(wd, f"light state {ls['id']}: applies_when {ls['applies_when']!r} is not a trigger id in any level")
            for ch in ls["changes"]:
                p = self.placement_ids.get(ch["placement"])
                if not p:
                    rep.err(wd, f"light state {ls['id']}: placement {ch['placement']!r} unknown")
                    continue
                sdef = self.atlas.get("animations", {}).get(p.get("state_set", "")) or self.gap_sets.get(p.get("state_set", ""))
                lm = self.atlas.get("landmarks", {}).get(p.get("landmark", ""))
                if sdef and ch["state"] not in sdef["states"]:
                    rep.err(wd, f"light state {ls['id']}: state {ch['state']!r} not in {p['state_set']}")
                elif lm and ch["state"] not in lm["states"]:
                    rep.err(wd, f"light state {ls['id']}: landmark state {ch['state']!r} unknown")
                elif not sdef and not lm:
                    rep.err(wd, f"light state {ls['id']}: placement {ch['placement']} has no state set or landmark")
        for ps in d.get("pace_signs", []):
            if ps["placement"] not in self.placement_ids:
                rep.err(wd, f"pace sign placement {ps['placement']!r} unknown")
        for sq in d.get("side_quests", []):
            if sq["giver"] not in self.npcs:
                rep.err(wd, f"side quest {sq['id']}: giver {sq['giver']!r} is not an npc")
            for iid in sq["interactions"]:
                if iid not in self.interactions:
                    rep.err(wd, f"side quest {sq['id']}: interaction {iid!r} unknown")
            for sc in sq["terminal_scenes"]:
                self.check_scene(sc, wd)
            for gu in sq.get("gestures", []):
                if gu["id"] not in self.ref.rows:
                    rep.err(wd, f"side quest gesture {gu['id']!r} unknown")
            for dl in sq.get("dialogue", []):
                self.check_dialogue(dl, wd)
        # an NPC that starts absent must be brought in by some trigger
        for nid, n in self.npcs.items():
            if n.get("initial_state", "start") == ABSENT:
                arrives = any(op.get("op") == "npc_state" and op.get("npc") == nid and op.get("state") != ABSENT
                              for _, (_, lv) in self.levels.items() for tr in lv["triggers"] for op in tr["then"])
                if not arrives:
                    rep.err(wd, f"npc {nid} starts {ABSENT} but no level trigger ever brings it in (npc_state op)")
        # every level of this district named in world.json must exist
        if stop:
            first, last = stop["levels"]
            for n in range(first, last + 1):
                lid = f"{self.id}-{n:02d}"
                if lid not in self.levels:
                    rep.err(rel(self.ddir), f"missing level file for {lid}")
        # world mira routes of this district must exist
        for mid, mr in self.ref.mira_index.items():
            if mr["district"] == self.id and mid not in self.mira:
                rep.err(rel(self.ddir), f"missing mira route file for {mid}")

    # ---- coverage
    def check_coverage(self):
        rep = self.rep
        wc = self.w("coverage.json")
        cov = self.coverage
        if cov is None:
            return
        if cov["district"] != self.id:
            rep.err(wc, "district does not match directory")
        # what the levels actually claim, per gesture and phase
        claims = {}

        def add_claims(gestures):
            for gu in gestures:
                for ph in gu["phases"]:
                    claims.setdefault(gu["id"], {}).setdefault(ph, set()).add(gu["scene_id"])

        for _, (p, lv) in self.levels.items():
            add_claims(lv["gestures"])
        for _, (p, mr) in self.mira.items():
            add_claims(mr.get("gestures", []))
        for sq in self.district.get("side_quests", []):
            add_claims(sq.get("gestures", []))
        # owned gestures: introduced_in a level of this district
        owned_by_level = {}
        for gid, row in self.ref.rows.items():
            lid = f"{self.id}-{row['introduced_in']:02d}"
            if self.ref.district_of_level_number(row["introduced_in"]) == self.id:
                owned_by_level.setdefault(lid, []).append(gid)
        computed_uncovered = []
        for lid in sorted(self.levels):
            owned = sorted(owned_by_level.get(lid, []))
            entry = cov["levels"].get(lid)
            if entry is None:
                rep.err(wc, f"no coverage entry for {lid}")
                continue
            if sorted(entry["owned"]) != owned:
                rep.err(wc, f"{lid}: owned {sorted(entry['owned'])} differs from inventory introduced_in {owned}")
            for gid in owned:
                row = self.ref.rows[gid]
                phases = entry["gestures"].get(gid)
                if phases is None:
                    computed_uncovered.append((lid, gid, ["guided", "variation", "recall"]))
                    rep.err(wc, f"{lid}: gesture {gid} has no coverage row")
                    continue
                if row["external_only"]:
                    if not phases:
                        computed_uncovered.append((lid, gid, ["any"]))
                        rep.err(wc, f"{lid}: external-only gesture {gid} needs at least one scene")
                    continue
                missing = [ph for ph in ("guided", "variation", "recall") if ph not in phases]
                if missing:
                    computed_uncovered.append((lid, gid, missing))
                    rep.err(wc, f"{lid}: gesture {gid} lacks {missing}")
                    continue
                orders = {}
                for ph in ("guided", "variation", "recall"):
                    sid = phases[ph]
                    if sid not in self.scenes:
                        rep.err(wc, f"{lid}/{gid}: {ph} scene {sid!r} not defined")
                        orders = None
                        break
                    if sid not in claims.get(gid, {}).get(ph, set()):
                        rep.err(wc, f"{lid}/{gid}: {ph} scene {sid!r} is not claimed as '{ph}' for {gid} by any level, route or side quest")
                    orders[ph] = self.scenes[sid][0]
                if orders:
                    if not orders["variation"] > orders["guided"]:
                        rep.err(wc, f"{lid}/{gid}: variation scene must come after the guided scene")
                    if not orders["recall"] > orders["variation"]:
                        rep.err(wc, f"{lid}/{gid}: recall scene must come after the variation scene")
                    rsc = self.scenes[phases["recall"]][1]
                    if rsc.get("position_cue") is not False:
                        rep.err(wc, f"{lid}/{gid}: recall scene {rsc['id']!r} must declare position_cue false")
        if cov["uncovered"]:
            rep.err(wc, f"uncovered must be empty, found {len(cov['uncovered'])} entries")
        for lid in cov["levels"]:
            if lid not in self.levels:
                rep.err(wc, f"coverage entry for unknown level {lid}")
        for rid, gestures in cov.get("mira", {}).items():
            if rid not in self.mira:
                rep.err(wc, f"coverage.mira has unknown route {rid!r}")
            for gid, phases in gestures.items():
                if gid not in self.ref.rows:
                    rep.err(wc, f"coverage.mira/{rid}: gesture {gid!r} unknown")
                for ph, sid in phases.items():
                    if ph in ("guided", "variation", "recall") and sid not in self.scenes:
                        rep.err(wc, f"coverage.mira/{rid}/{gid}: scene {sid!r} undefined")
        for lid, gid, missing in computed_uncovered:
            self.rep.info(f"uncovered {lid} {gid}: {missing}")

    # ---- NEEDS_ART.md lists every art_gap name
    def check_needs_art(self):
        path = self.ddir / "NEEDS_ART.md"
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        for name in self.gap_entries:
            if f"`{name}`" not in text:
                self.rep.err(self.w("NEEDS_ART.md"), f"art_gap prop `{name}` is not listed")

    # ---- keyboard inset
    def check_inset(self):
        m, d, rep = self.map, self.district, self.rep
        cb = d["camera_bounds"]
        map_px = (cb["w"] * TILE, cb["h"] * TILE)
        ox, oy = cb["x"] * TILE, cb["y"] * TILE

        def camera_for(px, py):
            cx = min(max(px - AVATAR_SCREEN[0], ox), ox + map_px[0] - VIEW_W)
            cy = min(max(py - AVATAR_SCREEN[1], oy), oy + map_px[1] - VIEW_H)
            return cx, cy

        def overlaps(x0, y0, x1, y1):
            return x0 < INSET[2] and x1 > INSET[0] and y0 < INSET[3] and y1 > INSET[1]

        conflicts = []
        for iid, it in self.interactions.items():
            for ap in it.get("approach", [])[:1]:
                ax, ay = ap["cell"][0] * TILE + 8, ap["cell"][1] * TILE + 16  # feet anchor
                cx, cy = camera_for(ax, ay)
                sx, sy = ax - cx, ay - cy
                avatar_hit = overlaps(sx - 8, sy - 24, sx + 8, sy)
                tgt = it["cells"]
                tx0 = min(c[0] for c in tgt) * TILE - cx
                ty0 = min(c[1] for c in tgt) * TILE - cy
                tx1 = (max(c[0] for c in tgt) + 1) * TILE - cx
                ty1 = (max(c[1] for c in tgt) + 1) * TILE - cy
                target_hit = overlaps(tx0, ty0, tx1, ty1)
                if avatar_hit or target_hit:
                    conflicts.append((iid, "avatar" if avatar_hit else "", "target" if target_hit else ""))
        # main-route and Mira checkpoint cells: report where the avatar itself would sit under the inset
        route_hits = []
        seen = set()
        for seg in m["routes"]["main"]:
            for c in seg["cells"]:
                seen.add(tuple(c))
        for cells in m["routes"]["mira"].values():
            for c in cells:
                seen.add(tuple(c))
        for c in sorted(seen):
            ax, ay = c[0] * TILE + 8, c[1] * TILE + 16
            cx, cy = camera_for(ax, ay)
            sx, sy = ax - cx, ay - cy
            if overlaps(sx - 8, sy - 24, sx + 8, sy):
                route_hits.append(c)
        if route_hits:
            rep.warn(self.w("map.json"), f"{len(route_hits)} main-route or checkpoint cells put the avatar under the keyboard inset: " + ", ".join(f"({x},{y})" for x, y in route_hits[:12]) + (" ..." if len(route_hits) > 12 else ""))
        sheet = self.ddir / "LEVEL_SHEET.md"
        text = sheet.read_text(encoding="utf-8") if sheet.exists() else ""
        if conflicts:
            if "keyboard-inset" not in text.lower() and "keyboard inset" not in text.lower():
                rep.err(self.w("LEVEL_SHEET.md"), "document the keyboard-inset conflicts (section 'Keyboard-inset conflicts')")
            for iid, a, t in conflicts:
                if f"`{iid}`" not in text:
                    rep.err(self.w("LEVEL_SHEET.md"), f"keyboard-inset conflict at interaction `{iid}` is not documented")
            rep.warn(self.w("map.json"), "keyboard-inset conflicts at: " + ", ".join(
                f"{i} ({'+'.join(x for x in (a, t) if x)})" for i, a, t in conflicts))


# --------------------------------------------------------------------------- inventory linkage

def inventory_linkage(ref, rep, validated, landed):
    linked = set()
    for dist in landed:
        ddir = HERE / dist
        for p in sorted((ddir / "levels").glob("*.json")):
            try:
                lv = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            linked |= {g["id"] for g in lv.get("gestures", []) if isinstance(g, dict) and "id" in g}
        for p in sorted((ddir / "mira").glob("*.json")):
            try:
                mr = json.loads(p.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                continue
            linked |= {g["id"] for g in mr.get("gestures", []) if isinstance(g, dict) and "id" in g}
    by_owner = {}
    for gid, row in ref.rows.items():
        if gid in linked:
            continue
        by_owner.setdefault(ref.district_of_level_number(row["introduced_in"]) or "?", []).append(gid)
    rep.info(f"inventory: {len(linked & set(ref.rows))}/{len(ref.rows)} rows linked to a level in landed districts ({', '.join(landed) or 'none'})")
    for owner, ids in sorted(by_owner.items()):
        if owner in validated:
            rep.err("gesture-inventory.json", f"rows owned by {owner} but linked to no level: {', '.join(sorted(ids))}")
        else:
            state = "landed" if owner in landed else "not delivered yet"
            rep.warn("gesture-inventory.json", f"{len(ids)} rows owned by {owner} ({state}) are not linked to a level yet: {', '.join(sorted(ids))}")


def drop_solved_gaps(ddir):
    """Remove art_gap flags and declarations that the kit atlas now covers (run after the kit branch merges).

    A placement keeps its entry name; only the `art_gap` flag goes. Gap entries whose name is now an atlas entry
    and gap state sets whose name is now an atlas animation are deleted. Returns the list of what was dropped."""
    ddir = Path(ddir)
    mpath = ddir / "map.json"
    m = json.loads(mpath.read_text(encoding="utf-8"))
    dj = json.loads((ddir / "district.json").read_text(encoding="utf-8"))
    atlas = json.loads((ROOT / dj["kit"]).read_text(encoding="utf-8"))
    names = {e["name"] for e in atlas.get("entries", [])}
    anims = set(atlas.get("animations", {}))
    dropped = []
    for p in m["placements"]:
        if p.get("art_gap") and p.get("entry") in names:
            del p["art_gap"]
            dropped.append(f"placement {p['id']} ({p['entry']})")
    for name in list(m.get("art_gap_entries", {})):
        if name in names:
            del m["art_gap_entries"][name]
            dropped.append(f"art_gap_entries {name}")
    for sname in list(m.get("art_gap_state_sets", {})):
        if sname in anims:
            del m["art_gap_state_sets"][sname]
            dropped.append(f"art_gap_state_sets {sname}")
    if not m.get("art_gap_entries"):
        m.pop("art_gap_entries", None)
    if not m.get("art_gap_state_sets"):
        m.pop("art_gap_state_sets", None)
    if dropped:
        mpath.write_text(json.dumps(m, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return dropped


# --------------------------------------------------------------------------- self-test (mutation tests)

def selftest():
    """Mutation tests for the rules added in schema 0.2. Each case copies the Orientation district to a temp dir,
    injects one fault (or one valid use of a new feature) and checks that the validator reports it (or stays quiet).
    Run: python design/levels/validate_levels.py --selftest"""
    import copy
    import shutil
    import tempfile

    def edit(dst, name, fn):
        p = dst / name
        data = json.loads(p.read_text(encoding="utf-8"))
        fn(data)
        p.write_text(json.dumps(data, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")

    def line(data, did):
        return next(x for x in data["dialogue"] if x["id"] == did)

    def scene(data, sid):
        return next(x for x in data["terminal_scenes"] if x["id"] == sid)

    def trig(data, tid):
        return next(x for x in data["triggers"] if x["id"] == tid)

    L1, L2 = "levels/01-the-lobby.json", "levels/02-badge-printer.json"

    def set_when(tid, text):
        return lambda d: trig(d, tid).__setitem__("when", text)

    cases = []  # (label, [(file, fn)], expected substring or None for "no errors")

    cases.append(("clean copy has no errors", [], None))
    # reserved keys in scene tasks
    cases.append(("backtick in a label target", [(L1, lambda d: scene(d, "o01-desk-label")["task"].__setitem__("target", "west`"))], "reserved UI keys"))
    cases.append(("question mark in an items target", [(L2, lambda d: scene(d, "o02-guided-mapped")["task"].__setitem__("items", [{"id": "x", "target": "bea?"}]))], "reserved UI keys"))
    cases.append(("Backquote in steps accepts", [(L1, lambda d: scene(d, "o01-popup")["task"]["steps"][0].__setitem__("accepts", ["Escape", "Backquote"]))], "reserved UI keys"))
    cases.append(("a question in a prompt is fine", [(L1, lambda d: scene(d, "o01-desk-label")["task"].__setitem__("prompt", "Which desk is this?"))], None))
    # dialogue modes and Hint key requests
    cases.append(("hint line marked modal", [(L1, lambda d: line(d, "o01.d.popup").__setitem__("modal", True))], "modal must be false"))
    cases.append(("on_request line without a hint", [(L1, lambda d: line(d, "o01.d.popup-again").__setitem__("hint", None))], "must carry a hint"))
    cases.append(("on_request line with a non-request when", [(L1, lambda d: line(d, "o01.d.popup-again").__setitem__("when", "step_start:o01.s.popup"))], "must be exactly request:"))
    cases.append(("request atom in a trigger", [(L1, set_when("o01.t.ivo-north", "request:o01.d.popup"))], "Hint key requests"))
    cases.append(("request atom inside any_of", [(L1, set_when("o01.t.ivo-north", "any_of:request:o01.d.popup|scene_success:o01-loop"))], "Hint key requests"))
    # any_of and count
    cases.append(("any_of with two valid alternatives", [(L1, set_when("o01.t.ivo-north", "any_of:scene_success:o01-four-stops|scene_success:o01-loop"))], None))
    cases.append(("any_of with an unknown alternative", [(L1, set_when("o01.t.ivo-north", "any_of:scene_success:o01-four-stops|scene_success:nope"))], "not found"))
    cases.append(("any_of with one alternative", [(L1, set_when("o01.t.ivo-north", "any_of:scene_success:o01-four-stops"))], "at least two"))
    cases.append(("nested groups", [(L1, set_when("o01.t.ivo-north", "any_of:count:2:scene_success:o01-loop|scene_success:o01-popup|scene_success:o01-loop"))], "do not nest"))
    cases.append(("count 2 of 3", [(L1, set_when("o01.t.ivo-north", "count:2:scene_success:o01-loop|scene_success:o01-popup|scene_success:o01-four-stops & scene_success:o01-four-stops"))], None))
    cases.append(("count above the alternatives", [(L1, set_when("o01.t.ivo-north", "count:3:scene_success:o01-loop|scene_success:o01-popup"))], "more than the 2 alternatives"))
    cases.append(("count with a zero", [(L1, set_when("o01.t.ivo-north", "count:0:scene_success:o01-loop|scene_success:o01-popup"))], "positive integer"))

    # NPC not present yet
    def absent_start(d):
        # a new background worker that exists only in the data: absent at the start, no trigger moves it yet
        n = copy.deepcopy(next(x for x in d["npcs"] if x["id"] == "worker_a"))
        n["id"] = "visitor"
        n["poses_by_state"]["absent"] = None
        n["initial_state"] = "absent"
        d["npcs"].append(n)

    def arrives(d):
        trig(d, "o02.t.printer-steady")["then"].append({"op": "npc_state", "npc": "visitor", "state": "start"})

    cases.append(("NPC starts absent and never arrives", [("map.json", absent_start)], "starts absent but no level trigger"))
    cases.append(("NPC starts absent and a trigger brings it in", [("map.json", absent_start), (L2, arrives)], None))
    cases.append(("null pose on an ordinary state", [("map.json", lambda d: next(x for x in d["npcs"] if x["id"] == "ivo")["poses_by_state"].__setitem__("tablet", None))], "only the reserved state"))
    cases.append(("initial state missing", [("map.json", lambda d: next(x for x in d["npcs"] if x["id"] == "ivo").__setitem__("initial_state", "nowhere"))], "initial state"))

    def vis_absent(d):
        n = next(x for x in d["npcs"] if x["id"] == "ivo")
        n["poses_by_state"]["absent"] = None
        next(x for x in d["interactions"] if x["id"] == "ivo_start")["visible_when"] = "npc_state:ivo=absent"

    cases.append(("interaction visible only while the NPC is absent", [("map.json", vis_absent)], "cannot be interacted with"))
    cases.append(("visible_when names a missing state", [("map.json", lambda d: next(x for x in d["interactions"] if x["id"] == "ivo_start").__setitem__("visible_when", "npc_state:ivo=nope"))], "has no state"))

    failures = 0
    for label, edits, expect in cases:
        with tempfile.TemporaryDirectory() as tmp:
            dst = Path(tmp) / "orientation"
            shutil.copytree(HERE / "orientation", dst)
            for name, fn in edits:
                edit(dst, name, fn)
            rep = Report()
            ref = Reference(rep)
            DistrictCheck(ref, dst, rep).run()
        got = [e for e in rep.errors if "gesture-inventory" not in e]
        if expect is None:
            ok = not got
        else:
            ok = any(expect in e for e in got)
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + ("" if ok else f"\n        expected {expect!r}; errors: {got[:3]}"))
    # world: panel links
    for label, mut, expect in (
        ("panel link without a cell for each district", lambda w: next(l for l in w["links"] if l["kind"] == "panel")["cells"].pop("nightshift"), "needs a cell for each"),
        ("panel link without a seal", lambda w: next(l for l in w["links"] if l["kind"] == "panel").__setitem__("seal_required", None), "names the seal"),
        ("shipped panel link is clean", lambda w: None, None),
    ):
        world = json.loads(WORLD_PATH.read_text(encoding="utf-8"))
        mut(world)
        probs = world_link_problems(world)
        ok = (not probs) if expect is None else any(expect in p for p in probs)
        failures += 0 if ok else 1
        print(f"{'PASS' if ok else 'FAIL'}  {label}" + ("" if ok else f"\n        problems: {probs}"))
    print(f"selftest: {len(cases) + 3 - failures}/{len(cases) + 3} cases behaved as expected")
    return 1 if failures else 0


# --------------------------------------------------------------------------- main

def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dirs", nargs="*", help="district directories or ids (orientation, records, ...)")
    ap.add_argument("--all", action="store_true", help="validate every district directory that exists")
    ap.add_argument("-v", "--verbose", action="store_true", help="print every warning and info line")
    ap.add_argument("--strict", action="store_true", help="treat warnings as errors")
    ap.add_argument("--selftest", action="store_true", help="run the mutation tests for the schema 0.2 rules and exit")
    ap.add_argument("--drop-solved-gaps", action="store_true", help="edit map.json of the given districts: drop art_gap flags and declarations the kit atlas now covers, then exit")
    args = ap.parse_args(argv)
    if args.selftest:
        return selftest()
    if args.drop_solved_gaps:
        for item in args.dirs:
            p = Path(item) if Path(item).exists() else HERE / item
            done = drop_solved_gaps(p)
            print(f"{p.name}: dropped {len(done)} solved art gaps" + "".join(f"\n  {d}" for d in done))
        return 0

    rep = Report()
    landed = [d for d in DISTRICTS if (HERE / d / "district.json").exists()]
    targets = []
    if args.all:
        targets = landed[:]
        for d in DISTRICTS:
            if d not in landed:
                rep.warn(f"design/levels/{d}", "district not delivered yet; skipped")
    for item in args.dirs:
        p = Path(item)
        if not p.exists():
            p = HERE / item
        if not p.exists():
            rep.err(item, "directory not found")
            continue
        targets.append(p.resolve().name)
    if not targets and not args.all and not rep.errors:
        ap.error("give a district directory or --all")

    ref = Reference(rep)
    if ref.world is None or ref.inventory is None:
        return finish(rep, args)
    seen = []
    for name in dict.fromkeys(targets):
        DistrictCheck(ref, HERE / name, rep).run()
        seen.append(name)
    inventory_linkage(ref, rep, seen, landed)
    return finish(rep, args, seen)


def finish(rep, args, seen=()):
    if args.verbose:
        for line in rep.infos:
            print(f"info:    {line}")
    shown = rep.warnings if args.verbose else rep.warnings[:0]
    for line in shown:
        print(f"warning: {line}")
    for line in rep.errors:
        print(f"ERROR:   {line}")
    gap_warn = sum(1 for w in rep.warnings if "art_gap prop" in w)
    other_warn = len(rep.warnings) - gap_warn
    print(f"{', '.join(seen) or 'no districts'}: {len(rep.errors)} errors, {len(rep.warnings)} warnings"
          f" ({gap_warn} art_gap props, {other_warn} other{'' if args.verbose else '; -v lists them'})")
    if args.strict and rep.warnings:
        return 1
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())

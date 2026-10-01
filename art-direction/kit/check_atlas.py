"""Validate every *-atlas.json in this folder (and the layouts that reference them).

Run: python3 check_atlas.py [file.json ...]   (Pillow + numpy; jsonschema is used when installed)
Checks:
  - the file validates against atlas.schema.json (built-in validator if jsonschema is missing)
  - the PNG exists; every rect is inside it and on the 16 px grid; rects do not overlap
  - size_px fits the rect and rounds up to exactly the rect (no wasted cells); content is non-empty
  - pixels outside size_px (inside the rect) are transparent; all alpha is 0 or 255 (hard pixels)
  - no UI marker colour appears in any entry (#19AFA2 #EC776D #9876D5 #E6B750)
  - collision rows match the footprint cells; anchor is the footprint's bottom-centre
  - state sets, landmark parts and layer names reference real entries and layers
  - any *-review-room.json layout points at real entries, anims and landmarks, in bounds
Exit code 1 on any failure.
"""
import glob
import json
import os
import re
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
T = 16
MARKERS = {"19AFA2", "EC776D", "9876D5", "E6B750"}
fails = []


def fail(msg):
    fails.append(msg)
    print("FAIL", msg)


# ------------------------------------------------------------------ schema

def mini_validate(inst, schema, root, path="$"):
    """Small JSON Schema subset: type, enum, required, properties, additionalProperties,
    items, min/maxItems, minProperties, minimum, pattern, $ref (#/definitions/x)."""
    errs = []
    if "$ref" in schema:
        node = root
        for part in schema["$ref"][2:].split("/"):
            node = node[part]
        return mini_validate(inst, node, root, path)
    t = schema.get("type")
    pytypes = {"object": dict, "array": list, "string": str, "integer": int, "boolean": bool, "number": (int, float)}
    if t:
        ok = isinstance(inst, pytypes[t]) and not (t in ("integer", "number") and isinstance(inst, bool))
        if not ok:
            return [f"{path}: expected {t}"]
    if "enum" in schema and inst not in schema["enum"]:
        errs.append(f"{path}: {inst!r} not in {schema['enum']}")
    if "pattern" in schema and isinstance(inst, str) and not re.search(schema["pattern"], inst):
        errs.append(f"{path}: {inst!r} does not match {schema['pattern']}")
    if "minimum" in schema and isinstance(inst, (int, float)) and inst < schema["minimum"]:
        errs.append(f"{path}: {inst} < {schema['minimum']}")
    if isinstance(inst, list):
        if "minItems" in schema and len(inst) < schema["minItems"]:
            errs.append(f"{path}: fewer than {schema['minItems']} items")
        if "maxItems" in schema and len(inst) > schema["maxItems"]:
            errs.append(f"{path}: more than {schema['maxItems']} items")
        if "items" in schema:
            for i, v in enumerate(inst):
                errs += mini_validate(v, schema["items"], root, f"{path}[{i}]")
    if isinstance(inst, dict):
        for k in schema.get("required", []):
            if k not in inst:
                errs.append(f"{path}: missing {k}")
        if "minProperties" in schema and len(inst) < schema["minProperties"]:
            errs.append(f"{path}: fewer than {schema['minProperties']} properties")
        props = schema.get("properties", {})
        extra = schema.get("additionalProperties", True)
        for k, v in inst.items():
            if k in props:
                errs += mini_validate(v, props[k], root, f"{path}.{k}")
            elif extra is False:
                errs.append(f"{path}: unexpected property {k}")
            elif isinstance(extra, dict):
                errs += mini_validate(v, extra, root, f"{path}.{k}")
    return errs


def validate_schema(meta, schema):
    try:
        import jsonschema
    except ImportError:
        return mini_validate(meta, schema, schema)
    v = jsonschema.Draft7Validator(schema)
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '$'}: {e.message}" for e in v.iter_errors(meta)]


# ------------------------------------------------------------------ one atlas

def check_atlas(path, schema):
    name = os.path.basename(path)
    with open(path) as fh:
        meta = json.load(fh)
    for e in validate_schema(meta, schema):
        fail(f"{name} schema: {e}")
    if fails:
        return None
    png = os.path.join(os.path.dirname(path), meta["image"])
    if not os.path.exists(png):
        fail(f"{name}: image {meta['image']} missing")
        return None
    img = np.array(Image.open(png).convert("RGBA"))
    H, W = img.shape[:2]
    if W % T or H % T:
        fail(f"{name}: PNG {W}x{H} is not a multiple of {T}")
    seen = set()
    taken = np.zeros((H, W), bool)
    entries = {}
    for e in meta["entries"]:
        n = e["name"]
        where = f"{name}:{n}"
        if n in seen:
            fail(f"{where}: duplicate name")
        seen.add(n)
        entries[n] = e
        x, y, w, h = e["rect"]
        if any(v % T for v in (x, y, w, h)):
            fail(f"{where}: rect {e['rect']} is not on the {T} px grid")
        if x + w > W or y + h > H:
            fail(f"{where}: rect {e['rect']} is outside the {W}x{H} PNG")
            continue
        sw, sh = e["size_px"]
        if sw > w or sh > h or -(-sw // T) * T != w or -(-sh // T) * T != h:
            fail(f"{where}: size_px {e['size_px']} does not round up to rect {w}x{h}")
            continue
        if taken[y:y + h, x:x + w].any():
            fail(f"{where}: rect overlaps another entry")
        taken[y:y + h, x:x + w] = True
        reg = img[y:y + h, x:x + w]
        content = reg[:sh, :sw]
        if not (content[:, :, 3] > 0).any():
            fail(f"{where}: empty sprite")
        if (reg[:, :, 3][sh:, :] > 0).any() or (reg[:, :, 3][:, sw:] > 0).any():
            fail(f"{where}: pixels outside size_px")
        a = reg[:, :, 3]
        if ((a != 0) & (a != 255)).any():
            fail(f"{where}: soft alpha (hard pixels only)")
        op = content[content[:, :, 3] > 0][:, :3]
        hexes = {"%02X%02X%02X" % tuple(c) for c in np.unique(op, axis=0)}
        if hexes & MARKERS:
            fail(f"{where}: marker colour {sorted(hexes & MARKERS)}")
        fw, fh = e["footprint"]["cells"]
        if len(e["collision"]) != fh or any(len(r) != fw for r in e["collision"]):
            fail(f"{where}: collision {e['collision']} does not match footprint {fw}x{fh}")
        ox, oy = e["footprint"]["origin_px"]
        if e["anchor"] != [ox + fw * T // 2, oy + fh * T]:
            fail(f"{where}: anchor {e['anchor']} is not the footprint's bottom-centre")
        comp = e.get("composite", {"mode": "over"})
        if comp["mode"] == "where_color" and "color" not in comp:
            fail(f"{where}: where_color needs a color")
        if "contact_shadow" in e:
            sx, sy, sw2, sh2 = e["contact_shadow"]
            if sx < 0 or sy < 0 or sx + sw2 > sw or sy + sh2 > sh:
                fail(f"{where}: contact_shadow outside the sprite")
        if e["layer"] not in meta["layers"]:
            fail(f"{where}: layer {e['layer']} not declared")
    for an, a in meta.get("animations", {}).items():
        if a["default"] not in a["states"]:
            fail(f"{name}:{an}: default state missing")
        for st, s in a["states"].items():
            for n in s["entries"]:
                if n not in entries:
                    fail(f"{name}:{an}.{st}: unknown entry {n}")
        for key in ("play", "loop"):
            for st in a.get(key, []):
                if st not in a["states"]:
                    fail(f"{name}:{an}.{key}: unknown state {st}")
    for ln, lm in meta.get("landmarks", {}).items():
        if lm["default_state"] not in lm["states"]:
            fail(f"{name}:{ln}: default_state missing")
        sizes = set()
        for st, s in lm["states"].items():
            for n in s["parts"]:
                if n not in entries:
                    fail(f"{name}:{ln}.{st}: unknown part {n}")
                else:
                    sizes.add(tuple(entries[n]["size_px"]))
                    if entries[n]["size_px"] != lm["size_px"]:
                        fail(f"{name}:{ln}.{st}: part {n} is {entries[n]['size_px']}, landmark is {lm['size_px']}")
            lamps = s.get("lamps")
            if lamps:
                if lamps["anim"] not in meta.get("animations", {}):
                    fail(f"{name}:{ln}.{st}: unknown lamp anim {lamps['anim']}")
                elif lamps["state"] not in meta["animations"][lamps["anim"]]["states"]:
                    fail(f"{name}:{ln}.{st}: unknown lamp state {lamps['state']}")
        # at least two visible things change between states: parts or lamp state
        names = list(lm["states"])
        base = lm["states"][names[0]]
        for st in names[1:]:
            s = lm["states"][st]
            changed = set(s["parts"]) ^ set(base["parts"])
            if (s.get("lamps") or {}).get("state") != (base.get("lamps") or {}).get("state"):
                changed.add("lamps")
            if len(changed) < 2:
                fail(f"{name}:{ln}: state {st} changes fewer than two things")
    print(f"{name}: {len(entries)} entries, {W}x{H} px, "
          f"{len(meta.get('animations', {}))} state sets, {len(meta.get('landmarks', {}))} landmarks")
    return meta


def check_layout(path, atlases):
    name = os.path.basename(path)
    with open(path) as fh:
        lay = json.load(fh)
    meta = atlases.get(lay["atlas"])
    if meta is None:
        fail(f"{name}: atlas {lay['atlas']} not checked")
        return
    ents = {e["name"] for e in meta["entries"]}
    anims, lms = meta.get("animations", {}), meta.get("landmarks", {})
    cw, ch = lay["size_cells"]
    legend = lay["floor"]["legend"]
    rows = lay["floor"]["rows"]
    if len(rows) != ch or any(len(r) != cw for r in rows):
        fail(f"{name}: floor grid is not {cw}x{ch}")
    for r in rows:
        for c in r:
            if legend.get(c) not in ents:
                fail(f"{name}: floor char {c!r} has no entry")
    for i, p in enumerate(lay["placements"]):
        key = next((k for k in ("entry", "anim", "landmark") if k in p), None)
        pool = {"entry": ents, "anim": anims, "landmark": lms}.get(key, {})
        if key is None or p[key] not in pool:
            fail(f"{name}: placement {i} {p} references nothing")
        cx, cy = p["cell"]
        if not (0 <= cx < cw and 0 <= cy < ch):
            fail(f"{name}: placement {i} cell {p['cell']} is outside the room")
        for v in p.get("offset", [0, 0]):
            if not 0 <= v < T:
                fail(f"{name}: placement {i} offset {p.get('offset')} should be 0-15 px")
    print(f"{name}: {len(rows)} floor rows, {len(lay['placements'])} placements")


def main():
    with open(os.path.join(HERE, "atlas.schema.json")) as fh:
        schema = json.load(fh)
    args = sys.argv[1:]
    paths = args or sorted(glob.glob(os.path.join(HERE, "*-atlas.json")))
    if not paths:
        fail("no *-atlas.json found")
    atlases = {}
    for p in paths:
        m = check_atlas(p, schema)
        if m:
            atlases[os.path.basename(p)] = m
    if not args:
        for p in sorted(glob.glob(os.path.join(HERE, "*-review-room.json"))):
            check_layout(p, atlases)
    print("ATLAS CHECK", "FAILED" if fails else "PASSED")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()

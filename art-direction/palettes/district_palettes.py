"""District palettes (Director decision 2026-10-02) and the new cast's skin and hair ramps.

Every district is 8 ramps x 4 steps, ordered shadow -> light:
ink, floor, wall, glass, wood, foliage, accent, violet.
`ink` and `violet` are shared verbatim by every district (glitches look the same
everywhere). `floor` step 3 is the broad fill and step 2 the slab mid tone, the
indices environment.py already uses for STONE. The darkest step of a ramp goes on
contours and joints only, as in STYLE_BIBLE section 3.

Orientation is the approved palette from STYLE_BIBLE section 3. It has no separate
wall ramp (walls reuse the stone ramp) and keeps coral as a ninth, people ramp.
Spec and derivation: PALETTES_SPEC.md. Checks: check_palettes.py.
"""
import importlib
import os
import sys

ROLES = ("ink", "floor", "wall", "glass", "wood", "foliage", "accent", "violet")
FLOOR_FILL, FLOOR_MID = 3, 2  # indices into the floor ramp (environment.py: STONE[3] fill, STONE[2] joints)

INK = ["#202337", "#343650", "#535971", "#777A8C"]
VIOLET = ["#413755", "#67547C", "#9477AF", "#C3A6D6"]  # glitches only, identical in every district

MARKERS = {"teal": "#19AFA2", "coral": "#EC776D", "violet": "#9876D5", "gold": "#E6B750"}

DISTRICTS = {
    "orientation": {
        "ink": INK,
        "floor": ["#665D65", "#968A85", "#C7B7A0", "#F0DEC0"],
        "wall": ["#665D65", "#968A85", "#C7B7A0", "#F0DEC0"],  # shares the stone ramp
        "glass": ["#203A50", "#366479", "#5AA3AE", "#A0DDD4"],
        "wood": ["#523D4C", "#85565A", "#BA785F", "#E4AA73"],
        "foliage": ["#21484A", "#326D60", "#5FA06D", "#B2CE78"],
        "accent": ["#705056", "#AC7655", "#E1AC62", "#F5D580"],  # brass / discovery
        "violet": VIOLET,
    },
    "records": {
        "ink": INK,
        "floor": ["#46606C", "#6C8996", "#92AEB8", "#BCD0D4"],
        "wall": ["#756F66", "#A09A8A", "#CDC8B4", "#EBE7D6"],
        "glass": ["#1F3745", "#31566A", "#527F94", "#8DB6C2"],
        "wood": ["#47202F", "#7B3442", "#A94C47", "#D08060"],
        "foliage": ["#2C463F", "#476B59", "#7B9E7F", "#B8CC9E"],
        "accent": ["#6B2F45", "#A9414F", "#D4606A", "#F4B1A4"],
        "violet": VIOLET,
    },
    "systems": {
        "ink": INK,
        "floor": ["#7C8996", "#A2AEB9", "#C8D1D8", "#E8EDF0"],
        "wall": ["#3C4A66", "#55698A", "#7C90B0", "#AEBDD3"],
        "glass": ["#172B66", "#2347B0", "#2F63D9", "#8CB0F2"],
        "wood": ["#4B4558", "#7E6F6A", "#B39A7E", "#DCC8A4"],
        "foliage": ["#1D3F46", "#2C7A70", "#5ED0A8", "#B4F0D6"],  # mint circuitry: a device ramp
        "accent": ["#7A2F1B", "#C2521A", "#F2842B", "#FFB36B"],  # safety orange
        "violet": VIOLET,
    },
    "nightshift": {
        "ink": INK,
        "floor": ["#12161A", "#242C34", "#364049", "#4C5865"],
        "wall": ["#1B2145", "#283063", "#38437F", "#5062A0"],
        "glass": ["#2C3560", "#4C5A8E", "#8E96B8", "#D0D4E4"],
        "wood": ["#3A2230", "#5E3A3E", "#8C5A4A", "#BC8260"],
        "foliage": ["#1C3A38", "#2A5A4E", "#3F7A63", "#7EA880"],
        "accent": ["#7A4A4A", "#B8745A", "#E8A55F", "#F9D79A"],  # warm pools of light
        "violet": VIOLET,
    },
    "executive": {
        "ink": INK,
        "floor": ["#8D8A86", "#B7B3AB", "#D9D5CB", "#F1EEE6"],
        "wall": ["#1D2B52", "#2B4079", "#3F5A9E", "#6B84BE"],
        "glass": ["#3B5F82", "#6A93B5", "#A5C8DD", "#E1F0F5"],
        "wood": ["#3A2630", "#5E3B38", "#8A5A45", "#B98862"],
        "foliage": ["#1B4A34", "#2F7A45", "#5FAF55", "#B6DB7A"],
        "accent": ["#5E2F2B", "#A4573A", "#D88149", "#F2B98A"],  # copper
        "violet": VIOLET,
    },
}
# Orientation keeps coral (people / upholstery) beside its eight ramps.
ORIENTATION_EXTRA = {"coral": ["#71394F", "#B65761", "#E67A70", "#F6B18E"]}

# Ramps that are emissive devices: they may be teal-hued above 60% saturation
# (terminals, mint circuitry) but still never come near a UI marker.
DEVICE_RAMPS = {
    "orientation": {"glass"},
    "records": {"glass"},
    "systems": {"glass", "foliage"},
    "nightshift": {"glass"},
    "executive": {"glass"},
}

NAMES = {"orientation": "Orientation", "records": "Records", "systems": "Systems",
         "nightshift": "Night Shift", "executive": "Executive"}

# Night Shift edge-light rule (documented in PALETTES_SPEC.md): the floor is too dark for the
# #202337 outline to carry a silhouette, so the renderer draws a 1 px hard rim on the lit
# (upper-left) contour of every person, in this accent step.
NIGHT_RIM = ("nightshift", "accent", 3)

ROLE_NOTES = {
    "ink": "Shared in every district: contours, cool shadows.",
    "floor": "Broad floor: step 3 fill, step 2 slab mid, steps 0-1 joints and wear.",
    "wall": "Wall faces and partition panels.",
    "glass": "Glass, metal and device screens.",
    "wood": "Desks, seating, trim.",
    "foliage": "Plants and planters.",
    "accent": "The district's accent: files, orange equipment, lamp pools, copper.",
    "violet": "Glitches only. Shared in every district.",
}

# --- Skin and hair for the four remaining cast members (task 5.2) ------------------------
# Keys follow ivo_sprites.py: hair A B C D (A only on contour), skin k l m n (k only on
# contour or occlusion). Steps run shadow -> light.
CAST_RAMPS = {
    "noor": {
        "hair": ["#121929", "#102A3E", "#29425A", "#436687"],  # blue-black, straight, precise
        "skin": ["#6F5443", "#9D7E5A", "#C1A56E", "#E8C798"],  # light olive
    },
    "hal": {
        "hair": ["#8F7344", "#C6A76F", "#DFC38B", "#F5E1AD"],  # sandy blond, cropped
        "skin": ["#5D3A24", "#754F2D", "#8F6C38", "#A8824D"],  # medium-deep golden brown
    },
    "ada": {
        "hair": ["#6A5550", "#A99281", "#D8C3AE", "#F6E9D6"],  # warm white, cropped
        "skin": ["#24120E", "#3A2018", "#5C3A28", "#80553A"],  # deepest skin, warm brown
    },
    "vale": {
        "hair": ["#1B1917", "#2B2D25", "#414339", "#606255"],  # dark graphite, slicked
        "skin": ["#947665", "#C0A78B", "#E9CDAE", "#F8E6CC"],  # pale ivory
    },
}

_CAST_MODULES = (("engineer", "gate1", "engineer_sprites"),
                 ("ivo", "cast", "ivo_sprites"),
                 ("mira", "cast", "mira_sprites"))


def existing_cast():
    """Approved cast modules (Engineer, Ivo, Mira): name -> module."""
    here = os.path.dirname(os.path.abspath(__file__))
    for _, folder, _ in _CAST_MODULES:
        p = os.path.join(here, "..", folder)
        if p not in sys.path:
            sys.path.insert(0, p)
    return {name: importlib.import_module(mod) for name, _, mod in _CAST_MODULES}


def existing_cast_ramps():
    """name -> {'hair': [4 hex], 'skin': [4 hex]} read from the approved sprite palettes."""
    out = {}
    for name, mod in existing_cast().items():
        out[name] = {slot: [mod.PAL[k] for k in mod.SLOTS[slot]] for slot in ("hair", "skin")}
    return out


def all_cast_ramps():
    r = existing_cast_ramps()
    r.update(CAST_RAMPS)
    return r


CAST_ORDER = ("engineer", "ivo", "mira", "noor", "hal", "ada", "vale")

"""Writes world-native.png: the approved Gate 1 Orientation scene with the four
baked pixel markers left out, so the DOM/SVG markers of the UI kit are the only
markers on the reference stage. Everything else is the approved scene, drawn by
the approved code (build_gate1.scene), not a fork of it.

Run: PY build_world.py     (needs Pillow + numpy)
"""
import os
import sys

import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "gate1"))
import build_gate1 as g1  # noqa: E402

# Marker centres in cells (as in build_gate1.scene) and the radius that covers them.
MARKERS = {"talk": (8.0, 1.95), "terminal": (10.6, 0.95), "route": (17.55, 4.45), "glitch": (3.6, 3.4)}


def main():
    g1.bst.marker = lambda *a, **k: None          # the UI draws markers as SVG
    c = g1.scene(g1.eng.IDLE["s"][0], g1.START_X + 32, g1.ROUTE_Y)
    out = Image.fromarray(c.img[:180, :320])
    out.save(os.path.join(HERE, "world-native.png"))

    # Verify: identical to the approved scene outside the marker boxes.
    ref = np.array(Image.open(os.path.join(HERE, "..", "gate1", "gate1-scene-native.png")).convert("RGB"))
    new = np.array(out.convert("RGB"))
    diff = np.any(ref != new, axis=2)
    mask = np.zeros_like(diff)
    for x, y in MARKERS.values():
        cx, cy = int(x * 16), int(y * 16)
        mask[max(0, cy - 16):cy + 16, max(0, cx - 16):cx + 16] = True
    outside = int((diff & ~mask).sum())
    print(f"world-native.png written; {int(diff.sum())} px differ from gate1-scene-native.png, "
          f"{outside} of them outside the four marker boxes")
    if outside:
        sys.exit(1)


if __name__ == "__main__":
    main()

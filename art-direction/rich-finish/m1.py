"""Mock 1: light and atmosphere. Today's art and palette, plus floor variation, cast shadows, lamp
glow, window light and a stepped edge falloff. Nothing is redrawn."""
import numpy as np
import base, passes
from PIL import Image
import build_scale_test as bst


def build(art=None):
    c, room = base.scene_parts()
    a = c.img
    passes.slab_variation(a)
    if art:
        art(c, room)
    objects = ~passes.floor_mask(a)
    objects[:, 292:] = False                                   # the wall mass casts nothing
    rug = np.zeros_like(objects); rug[76:106, 260:292] = True
    objects &= ~rug
    passes.cast_shadows(a, objects)
    greens = np.zeros(a.shape[:2], bool)
    for i in range(4):
        greens |= np.all(a == np.array(bst.GREEN[i], np.uint8), axis=2)
    canopy = np.zeros_like(greens); canopy[56:136, 90:182] = True
    passes.cast_shadows(a, greens & canopy, dx=10, dy=8, mul=(0.84, 0.84, 0.90))
    passes.lamp_glow(a, [(92, 71), (180, 71), (180, 129), (284, 51), (284, 125)])
    passes.light_shafts(a, [(38, 26), (212, 26), (244, 26)])
    passes.vignette_steps(a)
    base.add_markers(c)
    return c.img


if __name__ == "__main__":
    base.save_x4(build(), "m1_light.png")

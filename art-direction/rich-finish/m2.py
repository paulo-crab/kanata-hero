"""Mock 2 and its descendants.

build()                          Mock 2: Mock 1's light plus the vivid palette and leaf-fan foliage.
build(dense=True)                Mock 3: adds set-piece density (superseded: the board does not want density).
build(organic=True)              Mock 2.1: richer foliage, bark, pond, rocks, moss, planters.
build(materials=True)            Mock 2.2: bevelled slabs, wood grain, brick joints, monitor content, lamp housings.
build(organic=True, materials=True)   Mock 2.3: both.
No objects are added in 2.1 to 2.3; they only draw more on what the room already holds.
"""
import numpy as np

import base
import passes
import art_v2
import art_v4

LAMPS = [(92, 72), (180, 72), (180, 130), (284, 52), (284, 126)]


def build(dense=False, organic=False, materials=False):
    import environment as env
    saved = (env.leaves, env.pot_plant)
    env.leaves = art_v4.leaves_v4 if organic else art_v2.leaves_v2
    env.pot_plant = art_v4.pot_v4 if organic else art_v2.pot_v2
    try:
        c, room = base.scene_parts()
    finally:
        env.leaves, env.pot_plant = saved
    a = c.img
    art_v2.finish_art(c, room)
    if dense:
        import art_v3
        art_v3.extras(c, room)
    if organic:
        art_v4.tree_detail(room)
        art_v4.pond_detail(room)
        art_v4.rock_detail(room)
        art_v4.grass_tufts(room, _bed(a))
        art_v4.flowers_v4(room, [(104, 112), (106, 120), (168, 110), (124, 121), (162, 121), (146, 90)])
    if materials:
        art_v4.monitors_and_keys(room)
        art_v4.rim_bricks(room)
        art_v4.wall_detail(room)
    a[:] = art_v2.remap(a)
    if materials:
        art_v4.lamp_detail(room, LAMPS)
        late = art_v4.late_masks(a)
    passes.slab_variation(a)
    objects = ~passes.floor_mask(a)
    objects[:, 292:] = False
    rug = np.zeros_like(objects); rug[76:106, 260:292] = True; rug[118:150, 8:76] = dense
    objects &= ~rug
    passes.cast_shadows(a, objects)
    greens = np.zeros(a.shape[:2], bool)
    for col in art_v2.FOL[1:]:
        greens |= np.all(a == col, axis=2)
    canopy = np.zeros_like(greens); canopy[56:136, 90:182] = True
    passes.cast_shadows(a, greens & canopy, dx=10, dy=8, mul=(0.84, 0.84, 0.90))
    passes.lamp_glow(a, [(x, y - 1) for x, y in LAMPS])
    passes.light_shafts(a, [(38, 26), (212, 26), (244, 26)])
    if materials:
        art_v4.apply_late(a, late)
    base.add_markers(c)
    return c.img


def _bed(a):
    m = np.zeros(a.shape[:2], bool)
    m[84:127, 102:171] = True
    return m


if __name__ == "__main__":
    base.save_x4(build(), "m2_colour.png")
    base.save_x4(build(organic=True), "m2_1_organic.png")
    base.save_x4(build(materials=True), "m2_2_materials.png")
    base.save_x4(build(organic=True, materials=True), "m2_3_both.png")

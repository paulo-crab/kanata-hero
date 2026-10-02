// Data and atlas file names the engine loads. Contract: game/CONTRACTS.md section 3.1.
export const DATA_FILES = {
  district: '/design/levels/orientation/district.json',
  map: '/design/levels/orientation/map.json',
  level: '/design/levels/orientation/levels/01-the-lobby.json',
  world: '/design/levels/world.json',
  gestureInventory: '/design/levels/gesture-inventory.json',
  layoutManifest: '/design/layout/layout-manifest.json',
};

export const ATLAS_FILES = {
  kit: { json: '/art-direction/kit/orientation-atlas.json', png: '/art-direction/kit/orientation-atlas.png' },
  engineer: { json: '/art-direction/gate1/engineer-full-atlas.json', png: '/art-direction/gate1/engineer-full-atlas.png' },
  ivo: { json: '/art-direction/cast/ivo-atlas.json', png: '/art-direction/cast/ivo-atlas.png' },
  mira: { json: '/art-direction/cast/mira-atlas.json', png: '/art-direction/cast/mira-atlas.png' },
  bgworker_a: { json: '/art-direction/cast/bgworker_a-atlas.json', png: '/art-direction/cast/bgworker_a-atlas.png' },
  bgworker_b: { json: '/art-direction/cast/bgworker_b-atlas.json', png: '/art-direction/cast/bgworker_b-atlas.png' },
  glitches: { json: '/art-direction/glitches/glitches-atlas.json', png: '/art-direction/glitches/glitches-atlas.png' },
  pace: { json: '/art-direction/pace/pace-atlas.json', png: '/art-direction/pace/pace-atlas.png' },
  portraits: { json: '/art-direction/portraits/portraits-atlas.json', png: '/art-direction/portraits/portraits-atlas.png' },
};

/** Atlas ids that hold 16x24 person frames. */
export const PERSON_ATLASES = ['engineer', 'ivo', 'mira', 'bgworker_a', 'bgworker_b'];

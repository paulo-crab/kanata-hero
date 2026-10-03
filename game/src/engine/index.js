// Engine module public surface. Contract: game/CONTRACTS.md section 3.
export { DATA_FILES, ATLAS_FILES } from './files.js';
export { loadGameData, loadJson } from './loader.js';
export { loadAtlasSet, AtlasSet, validateMapAgainstAtlases } from './atlas.js';
export { AnimationPlayer, frameForSteps } from './animation.js';
export { World, personShadow, glitchShadow } from './world.js';
export { Avatar, DIRS } from './avatar.js';
export { computeCamera, worldToStage, chooseZoom } from './camera.js';
export { GameLoop, MAX_STEPS_PER_TICK } from './loop.js';
export { Renderer, orderLayer, orderWorld, LAYER_ORDER } from './renderer.js';
export { lookAhead, avatarStageRect, AVATAR_SPRITE, FADED_OPACITY, CLEARANCE } from './look-ahead.js';

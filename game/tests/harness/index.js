// Shared test harness for every Kanata Hero game test. Import from here:
//   import { FakeClock, ScriptedInput, loadRealData, diskFetch, insetViolations } from '../harness/index.js';
export { FakeClock, EventBus, STEP_MS, CELL_STEPS } from '../../src/shared/index.js';
export * from './paths.js';
export * from './fixtures.js';
export * from './input-player.js';
export * from './level-model.js';
export * from './bus-recorder.js';
export * from './game-factory.js';

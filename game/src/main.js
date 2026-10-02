// Boot. Skeleton only: wires the shared pieces and touches every module's public surface
// so a broken import fails loudly. Integration (group 7) fills this in. Contract section 8.
import { EventBus, RealClock } from './shared/index.js';
import * as engine from './engine/index.js';
import * as input from './input/index.js';
import * as runtime from './runtime/index.js';
import * as ui from './ui/index.js';

export const bus = new EventBus();
export const clock = new RealClock();
export const modules = { engine, input, runtime, ui };

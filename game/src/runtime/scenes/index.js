// Scene factories for the SceneMachine.
import { HubScene, WalkScene } from './world.js';
import { FormScene, LabelScene, EditorScene } from './terminal.js';
import {
  DialogueScene, LayoutHelpScene, JournalScene, ControlsScene, SettingsScene, ErrorScene,
} from './overlays.js';
import { SetupScene, CalibrationScene, ArrivalScene } from './flow.js';

export {
  HubScene, WalkScene, FormScene, LabelScene, EditorScene, DialogueScene, LayoutHelpScene,
  JournalScene, ControlsScene, SettingsScene, ErrorScene, SetupScene, CalibrationScene, ArrivalScene,
};

/** @param {object} ctx SceneContext (with level data in ctx.data.level) */
export function createSceneFactories(ctx) {
  const def = (id) => {
    const d = ctx.data.level.terminal_scenes.find((s) => s.id === id);
    if (!d) throw new Error(`Unknown scene ${id}`);
    return d;
  };
  return {
    setup: () => new SetupScene(),
    calibration: () => new CalibrationScene(),
    arrival: () => new ArrivalScene(),
    hub: () => new HubScene(),
    dialogue: () => new DialogueScene(),
    walk: (p) => new WalkScene(def(p.sceneId), ctx),
    label: (p) => new LabelScene(def(p.sceneId), ctx),
    form: (p) => new FormScene(def(p.sceneId), ctx),
    editor: (p) => new EditorScene(def(p.sceneId), ctx),
    'layout-help': () => new LayoutHelpScene(),
    journal: () => new JournalScene(),
    controls: () => new ControlsScene(),
    settings: () => new SettingsScene(),
    error: () => new ErrorScene(),
  };
}

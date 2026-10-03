// View control: joins the engine's camera look-ahead and the UI's panel rectangles. It listens to the same vm:* topics
// the UI draws, computes where the camera must be so the avatar is never under an open panel, hands that camera to the
// world and tells the UI which panels to fade when the camera cannot clear them. Works headless (tests) and in the page.
import { lookAhead } from './engine/index.js';
import { panelRects, PANEL_TOPICS } from './ui/panels.js';

export class ViewControl {
  /** @param {{bus:object, world:object, zoom?:number}} p */
  constructor({ bus, world, zoom = 4 }) {
    this.bus = bus;
    this.world = world;
    this.zoom = zoom;
    this.vms = {};
    this.last = { camera: world.baseCamera(), offset: { x: 0, y: 0 }, faded: [], panels: [], covered: false };
    this._fadedKey = '';
    this.offs = PANEL_TOPICS.map((t) => bus.on(t, (vm) => { this.vms[t] = vm ?? null; }));
  }

  /** Recompute the camera for the avatar's current position and the panels now open. */
  update() {
    const { covered, panels } = panelRects(this.vms);
    const bounds = this.world.data.district.camera_bounds;
    const r = covered
      ? { camera: this.world.baseCamera(), offset: { x: 0, y: 0 }, faded: [] }
      : lookAhead({ feetPx: this.world.avatar.feetPx, bounds, panels, zoom: this.zoom });
    this.world.setCameraOverride(r.offset.x || r.offset.y ? r.camera : null);
    this.last = { ...r, panels, covered };
    const key = r.faded.join(' ');
    if (key !== this._fadedKey) {
      this._fadedKey = key;
      this.bus.emit('ui:faded', { ids: [...r.faded] });
    }
    return this.last;
  }

  destroy() {
    for (const off of this.offs) off();
    this.world.setCameraOverride(null);
  }
}

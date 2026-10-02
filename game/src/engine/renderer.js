// Canvas 2D renderer. Contract section 3.4. Draws a WorldView into a 320x180 logical buffer and
// scales it with whole-number zoom, nearest neighbour. Takes the canvas and a canvas factory as
// parameters so tests can pass recording fakes.
import { VIEW_H, VIEW_W } from '../shared/index.js';
import { chooseZoom } from './camera.js';

export const LAYER_ORDER = ['rear_wall', 'floor_marking', 'rear_prop', 'shadow', 'actor', 'front_prop', 'light'];
const Y_SORTED = new Set(['rear_prop', 'actor', 'front_prop']);
export const BACKGROUND = '#0E1020';

function hexToRgb(hex) {
  const n = parseInt(hex.slice(1), 16);
  return [(n >> 16) & 255, (n >> 8) & 255, n & 255];
}

/** Stable order: unsorted draws keep list order, then y-sorted draws by anchor y. Pure. */
export function orderLayer(name, draws) {
  if (!Y_SORTED.has(name)) return draws;
  const flat = draws.filter((d) => !d.ySort);
  const sorted = draws
    .map((d, i) => [d, i])
    .filter(([d]) => d.ySort)
    .sort((a, b) => a[0].anchorY - b[0].anchorY || a[1] - b[1])
    .map(([d]) => d);
  return [...flat, ...sorted];
}

function defaultCreateCanvas(w, h) {
  if (typeof OffscreenCanvas !== 'undefined') return new OffscreenCanvas(w, h);
  const c = document.createElement('canvas');
  c.width = w;
  c.height = h;
  return c;
}

export class Renderer {
  /** @param {{canvas:any, atlases:object, stageEl?:any, createCanvas?:(w:number,h:number)=>any}} p */
  constructor({ canvas, atlases, stageEl = null, createCanvas = defaultCreateCanvas }) {
    this.canvas = canvas;
    this.atlases = atlases;
    this.stageEl = stageEl;
    this._create = createCanvas;
    this.ctx = canvas.getContext('2d');
    this._buffer = createCanvas(VIEW_W, VIEW_H);
    this.bctx = this._buffer.getContext('2d', { willReadFrequently: true });
    this.zoom = 1;
    this.reducedMotion = false;
    this.letterbox = { x: 0, y: 0, w: VIEW_W, h: VIEW_H };
    this._pixels = new Map();
    this.resize(VIEW_W, VIEW_H);
  }

  /** Integer zoom and a centred letterbox. Holds no game state, so resizing never loses any. */
  resize(winW, winH) {
    const zoom = chooseZoom(winW, winH);
    const w = VIEW_W * zoom;
    const h = VIEW_H * zoom;
    this.zoom = zoom;
    this.letterbox = { x: Math.floor((winW - w) / 2), y: Math.floor((winH - h) / 2), w, h };
    this.canvas.width = w;
    this.canvas.height = h;
    const st = this.canvas.style;
    if (st) {
      st.width = `${w}px`;
      st.height = `${h}px`;
      st.imageRendering = 'pixelated';
    }
    if (this.stageEl?.style) this.stageEl.style.setProperty('--world-zoom', String(zoom));
    return { zoom, letterbox: { ...this.letterbox } };
  }

  setReducedMotion(on) {
    this.reducedMotion = !!on;
  }

  _atlasPixels(atlasId) {
    if (this._pixels.has(atlasId)) return this._pixels.get(atlasId);
    const img = this.atlases.image(atlasId);
    let data = null;
    try {
      const c = this._create(img.width, img.height);
      const cx = c.getContext('2d', { willReadFrequently: true });
      cx.drawImage(img, 0, 0);
      data = cx.getImageData(0, 0, img.width, img.height);
    } catch {
      data = null;
    }
    this._pixels.set(atlasId, data);
    return data;
  }

  _drawWhereColor(d, dx, dy) {
    const src = this._atlasPixels(d.atlas);
    const { w, h } = d.rect;
    if (!src || typeof this.bctx.getImageData !== 'function') return false;
    const x0 = Math.max(0, dx);
    const y0 = Math.max(0, dy);
    const x1 = Math.min(VIEW_W, dx + w);
    const y1 = Math.min(VIEW_H, dy + h);
    if (x0 >= x1 || y0 >= y1) return true;
    const dst = this.bctx.getImageData(x0, y0, x1 - x0, y1 - y0);
    const [r, g, b] = hexToRgb(d.composite.color);
    for (let y = y0; y < y1; y += 1) {
      for (let x = x0; x < x1; x += 1) {
        const si = ((d.rect.y + (y - dy)) * src.width + d.rect.x + (x - dx)) * 4;
        if (src.data[si + 3] === 0) continue;
        const di = ((y - y0) * (x1 - x0) + (x - x0)) * 4;
        if (dst.data[di] === r && dst.data[di + 1] === g && dst.data[di + 2] === b) {
          dst.data[di] = src.data[si];
          dst.data[di + 1] = src.data[si + 1];
          dst.data[di + 2] = src.data[si + 2];
          dst.data[di + 3] = 255;
        }
      }
    }
    this.bctx.putImageData(dst, x0, y0);
    return true;
  }

  _drawOne(d, camera) {
    const ctx = this.bctx;
    if (d.rects) {
      for (const r of d.rects) {
        ctx.fillStyle = r.color;
        ctx.fillRect(Math.round(r.x - camera.x), Math.round(r.y - camera.y), r.w, r.h);
      }
      return;
    }
    const dx = Math.round(d.x - camera.x);
    const dy = Math.round(d.y - camera.y);
    const { x, y, w, h } = d.rect;
    if (dx >= VIEW_W || dy >= VIEW_H || dx + w <= 0 || dy + h <= 0) return;
    if (d.composite && d.composite.mode === 'where_color' && this._drawWhereColor(d, dx, dy)) return;
    ctx.drawImage(this.atlases.image(d.atlas), x, y, w, h, dx, dy, w, h);
  }

  /** Draw one WorldView with the camera top-left in map px. Layer order is the style bible's. */
  draw(view, camera = view.camera) {
    const cam = { x: Math.round(camera.x), y: Math.round(camera.y) };
    const b = this.bctx;
    b.imageSmoothingEnabled = false;
    b.fillStyle = BACKGROUND;
    b.fillRect(0, 0, VIEW_W, VIEW_H);
    for (const d of view.floor) this._drawOne(d, cam);
    for (const name of LAYER_ORDER) {
      for (const d of orderLayer(name, view.layers[name] ?? [])) this._drawOne(d, cam);
    }
    const m = this.ctx;
    m.imageSmoothingEnabled = false;
    m.clearRect(0, 0, this.canvas.width, this.canvas.height);
    m.drawImage(this._buffer, 0, 0, VIEW_W, VIEW_H, 0, 0, VIEW_W * this.zoom, VIEW_H * this.zoom);
  }
}

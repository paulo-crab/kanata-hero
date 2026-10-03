// Output feedback policy (playtest 1, item 5). The confidence card ("Output observed") teaches in scenes only:
//  - calibration and the terminal, editor and label scenes show the card, and it is cleared (vm:feedback null) when the
//    scene exits;
//  - in the open world (walking, dialogue) a step is a short toast, at most WORLD_TOAST_MS long, for the first
//    WORLD_TOAST_USES uses, and then nothing;
//  - the Settings option "Show output feedback" is 'scenes' (default), 'always' (the card also stays in the world) or 'off'.
// A use is one burst of walking: the toast is replaced while the player keeps walking, and a new use starts when the
// toast has been gone for a moment. The count is saved with the progress.

export const WORLD_TOAST_MS = 2500;
export const WORLD_TOAST_USES = 3;
export const FEEDBACK_MODES = ['scenes', 'always', 'off'];

export class FeedbackPolicy {
  /** @param {{bus:object, clock:object, progress:object}} p */
  constructor({ bus, clock, progress }) {
    this.bus = bus;
    this.clock = clock;
    this.progress = progress;
    this.cardOpen = false;
    this._lastToastAt = -Infinity;
    bus.on('scene:exit', () => this.clear());
  }

  mode() {
    const m = this.progress.doc.settings.feedback;
    return FEEDBACK_MODES.includes(m) ? m : 'scenes';
  }

  uses() {
    return (this.progress.doc.counters && this.progress.doc.counters.feedbackToasts) || 0;
  }

  /** The card of a teaching scene (calibration, terminal, editor, label). */
  scene(card) {
    if (this.mode() === 'off') return;
    this.cardOpen = true;
    this.bus.emit('vm:feedback', card);
  }

  /** One step of walking in the open world. */
  world(card, text) {
    const mode = this.mode();
    if (mode === 'off') return;
    if (mode === 'always') {
      this.cardOpen = true;
      this.bus.emit('vm:feedback', card);
      return;
    }
    const now = this.clock.now();
    const burst = now - this._lastToastAt <= WORLD_TOAST_MS;
    if (!burst) {
      if (this.uses() >= WORLD_TOAST_USES) return;
      this.progress.update((d) => {
        d.counters = { ...(d.counters || {}), feedbackToasts: this.uses() + 1 };
      });
    }
    this._lastToastAt = now;
    this.bus.emit('vm:toast', { key: 'feedback', text, tone: 'feedback', ms: WORLD_TOAST_MS });
  }

  /** Remove the card, if one is showing. */
  clear() {
    if (!this.cardOpen) return;
    this.cardOpen = false;
    this.bus.emit('vm:feedback', null);
  }

  /** The option changed: a card that the new mode no longer allows goes away. */
  onSettings() {
    if (this.mode() === 'off') this.clear();
  }
}

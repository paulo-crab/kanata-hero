// Playtest 1, item 5 (UI side): the keyed feedback toast replaces itself and expires after its own time; the Settings
// screen offers Show output feedback.
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { settingsView } from '../../src/ui/index.js';
import { Toast } from '../../src/ui/misc.js';
import { textOf } from '../../src/ui/html.js';
import { FakeClock, EventBus } from '../../src/shared/index.js';
import { makeDom } from './dom-stub.js';
import * as F from './fixtures.js';

test('a keyed toast replaces the one with the same key and expires after its own 2.5 s', () => {
  const doc = makeDom();
  const host = doc.createElement('div');
  const clock = new FakeClock();
  const toast = new Toast(host, new EventBus(), { clock });
  toast.render({ key: 'feedback', text: 'Left Arrow observed: step west', tone: 'feedback', ms: 2500 });
  clock.advance(1000);
  toast.render({ key: 'feedback', text: 'Left Arrow observed: step west', tone: 'feedback', ms: 2500 });
  assert.equal(toast.toasts.length, 1, 'one toast, replaced');
  clock.advance(2400);
  assert.equal(toast.toasts.length, 1, 'the timer restarted with the replacement');
  clock.advance(200);
  assert.equal(toast.toasts.length, 0, 'gone 2.5 s after the last update');
  toast.render({ text: 'Progress will not be saved', tone: 'warn' });
  clock.advance(5000);
  assert.equal(toast.toasts.length, 1, 'an ordinary toast keeps its six seconds');
  toast.destroy();
});

test('settings: Show output feedback offers in scenes only, always and off, and marks the current one', () => {
  const m = String(settingsView(F.settingsVm({ feedback: 'always' })));
  assert.match(textOf(m), /Show output feedback/);
  assert.match(m, /data-fid="set-feedback-scenes"[^>]*aria-pressed="false"/);
  assert.match(m, /data-fid="set-feedback-always"[^>]*aria-pressed="true"/);
  assert.match(m, /data-fid="set-feedback-off"/);
  assert.match(textOf(m), /In scenes only/);
  const dflt = String(settingsView(F.settingsVm()));
  assert.match(dflt, /data-fid="set-feedback-scenes"[^>]*aria-pressed="true"/, 'in scenes only is the default');
});

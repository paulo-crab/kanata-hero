// Evidence and stars. Contract: game/CONTRACTS.md section 5.6. No durations are ever stored.

const IGNORED = new Set(['Shift', 'Alt', 'Control', 'Meta', 'CapsLock']);

/** Phase and gesture ids of a scene, from level.gestures[] (the only source of phase). */
export function phaseInfo(levelDef, sceneId) {
  const rows = ((levelDef && levelDef.gestures) || []).filter((g) => g.scene_id === sceneId);
  if (!rows.length) return { phase: 'guided', gestureIds: [] };
  return { phase: rows[0].phases[0], gestureIds: [...new Set(rows.map((g) => g.id))] };
}

export class EvidenceLog {
  /** @param {{level?:object}} [opts] level gives phase and gestureIds when a scene is first seen */
  constructor(opts = {}) {
    this._level = opts.level || null;
    this._scenes = new Map();
    this._hints = [];
  }

  _get(sceneId) {
    if (!this._scenes.has(sceneId)) {
      const { phase, gestureIds } = phaseInfo(this._level, sceneId);
      this._scenes.set(sceneId, {
        sceneId, phase, gestureIds, result: 'incomplete',
        actions: { total: 0, correct: 0 }, criticalOk: true, observed: [],
        hintUsed: false, hintForfeit: false, confidence: 'observed',
      });
    }
    return this._scenes.get(sceneId);
  }

  /** @param {{output:string, correct:boolean, critical:boolean, confidence?:string}} action */
  record(sceneId, action) {
    if (IGNORED.has(action.output)) return;
    const e = this._get(sceneId);
    e.actions.total += 1;
    if (action.correct) e.actions.correct += 1;
    if (action.critical && !action.correct) e.criticalOk = false;
    if (!e.observed.includes(action.output)) e.observed.push(action.output);
    if (action.confidence) e.confidence = action.confidence;
  }

  hint(use) {
    const e = this._get(use.sceneId);
    e.hintUsed = true;
    if (use.forfeitsStar) e.hintForfeit = true;
    this._hints.push({ ...use });
  }

  finish(sceneId, success) {
    const e = this._get(sceneId);
    if (success) e.result = 'success';
  }

  scene(sceneId) {
    const e = this._scenes.get(sceneId);
    return e ? structuredClone(e) : null;
  }

  all() {
    return Object.fromEntries([...this._scenes].map(([k, v]) => [k, structuredClone(v)]));
  }

  hints() {
    return this._hints.map((h) => ({ ...h }));
  }

  toJSON() {
    return { scenes: this.all(), hints: this.hints() };
  }

  static fromJSON(j, opts = {}) {
    const log = new EvidenceLog(opts);
    for (const [k, v] of Object.entries((j && j.scenes) || {})) log._scenes.set(k, structuredClone(v));
    log._hints = ((j && j.hints) || []).map((h) => ({ ...h }));
    return log;
  }
}

/** Clean run: every task-critical output correct and at least 95 percent of all actions correct. */
export function isClean(ev) {
  if (!ev || !ev.criticalOk) return false;
  const { total, correct } = ev.actions;
  return total === 0 || correct / total >= 0.95;
}

/** 1 complete; 2 all scenes clean; 3 clean and the recall scene clean with no hint used. */
export function computeStars(levelId, evidenceMap, levelDef) {
  const reasons = [];
  const ids = [...new Set((levelDef.gestures || []).map((g) => g.scene_id))];
  const evs = ids.map((id) => evidenceMap[id]);
  if (!ids.length || evs.some((e) => !e || e.result !== 'success')) {
    const missing = ids.filter((id) => !evidenceMap[id] || evidenceMap[id].result !== 'success');
    return { stars: 0, reasons: [`${levelId}: not complete (${missing.join(', ')})`] };
  }
  let stars = 1;
  reasons.push('1: every scene completed');
  const unclean = ids.filter((id) => !isClean(evidenceMap[id]));
  if (unclean.length) {
    reasons.push(`not 2: unclean scenes ${unclean.join(', ')}`);
    return { stars, reasons };
  }
  stars = 2;
  reasons.push('2: every scene clean');
  const recall = ids.filter((id) => phaseInfo(levelDef, id).phase === 'recall');
  const hinted = recall.filter((id) => evidenceMap[id].hintUsed);
  if (!recall.length || hinted.length) {
    reasons.push(recall.length ? `not 3: hint used in recall ${hinted.join(', ')}` : 'not 3: no recall scene');
    return { stars, reasons };
  }
  stars = 3;
  reasons.push('3: recall clean without a hint');
  return { stars, reasons };
}

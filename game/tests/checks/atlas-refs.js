// Independent check that every art name the level data uses exists in the atlas JSON files.
// This is the data-side twin of the engine's loadAtlasSet validation (CONTRACTS 3.1): the engine must
// refuse to load when one of these names is missing; this file proves which names matter.

/** @returns {string[]} problems, each "<kind>: <name> (<where>)"; empty when every reference resolves. */
export function missingAtlasRefs({ map, level }, atlases) {
  const problems = [];
  const entryNames = new Set([...atlases.kit.entries.map((e) => e.name), ...Object.keys(atlases.pace.entries)]);
  const stateSets = Object.keys(atlases.kit.animations || {});
  const landmarks = Object.keys(atlases.kit.landmarks || {});

  for (const p of map.placements) {
    if (p.entry && !entryNames.has(p.entry)) problems.push(`entry: ${p.entry} (placement ${p.id})`);
    if (p.state_set && !stateSets.includes(p.state_set)) problems.push(`state_set: ${p.state_set} (placement ${p.id})`);
    if (p.landmark && !landmarks.includes(p.landmark)) problems.push(`landmark: ${p.landmark} (placement ${p.id})`);
    if (p.state_set && stateSets.includes(p.state_set)) {
      const set = atlases.kit.animations[p.state_set];
      if (p.state && !set.states[p.state]) problems.push(`state: ${p.state} (state set ${p.state_set})`);
      for (const st of Object.values(set.states)) {
        for (const e of st.entries) if (!entryNames.has(e)) problems.push(`entry: ${e} (state set ${p.state_set})`);
      }
    }
  }
  const people = { ivo: atlases.ivo, mira: atlases.mira, bgworker_a: atlases.bgworker_a, bgworker_b: atlases.bgworker_b, engineer: atlases.engineer };
  for (const n of map.npcs) {
    const atlas = people[n.character];
    if (!atlas) { problems.push(`character atlas: ${n.character} (npc ${n.id})`); continue; }
    for (const pose of Object.values(n.poses_by_state || {})) {
      if (!atlas.animations[pose]) problems.push(`pose: ${pose} (npc ${n.id})`);
    }
  }
  // Avatar walk and idle in all four directions.
  for (const kind of ['idle', 'walk']) {
    for (const d of 'nsew') if (!atlases.engineer.animations[`engineer_${kind}_${d}`]) problems.push(`pose: engineer_${kind}_${d} (avatar)`);
  }
  // Optional glitch: archetype record and its three animations.
  const g = level.glitch;
  if (g) {
    if (!atlases.glitches.archetypes[g.archetype]) problems.push(`glitch archetype: ${g.archetype}`);
    for (const suffix of ['roam', 'repaired', 'ordinary']) {
      if (!atlases.glitches.animations[`${g.archetype}_${suffix}`]) problems.push(`glitch animation: ${g.archetype}_${suffix}`);
    }
  }
  // Portraits named by dialogue (object speakers have none).
  const objectSpeakers = new Set(['popup', 'pace_sign', 'form_card']);
  for (const d of level.dialogue) {
    if (objectSpeakers.has(d.speaker) || !d.portrait) continue;
    const key = `${d.speaker}_${d.portrait}`;
    if (!atlases.portraits.portraits[key]) problems.push(`portrait: ${key} (dialogue ${d.id})`);
  }
  return problems;
}

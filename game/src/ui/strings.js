// Fixed interface copy that is not level data. Every line is taken from art-direction/ui-kit/COMPONENTS.md
// or design/ui-key-bindings.md. Hint-grammar lines for lessons never live here: they arrive in view-models.

/** The keyboard exit that every overlay shows. */
export const CLOSE = { key: { key: 'Escape', label: 'Esc' }, gesture: 'tap Caps' };
export const CONTINUE = { key: { key: 'Enter', label: 'Return' }, gesture: 'tap-hold Caps + N' };

export const STATUS_LABELS = Object.freeze({
  not_started: 'Not started',
  observed: 'Observed output',
  skipped: 'Skipped',
});

export const CONFIDENCE_ICON = Object.freeze({
  observed: 'eye',
  player_confirmed: 'person-check',
  external_only: 'shield-key',
});

export const CONFIDENCE_WHY = Object.freeze({
  observed: 'The page saw a key event it can score.',
  player_confirmed: 'You said you did this gesture. The page cannot see which key you used.',
  external_only: 'The system keeps this shortcut. Confirm it, or skip: no penalty.',
});

export const SETUP_COPY = Object.freeze({
  title: 'Setup',
  sub: 'About two minutes. Nothing here blocks the story.',
  skip: 'Skip setup',
  keyboardHeading: 'Keyboard',
  footnote: 'The number row gives the same 1 and ! as Space + A and Space + Q, so observed output never proves which key you used.',
});

export const LAYOUT_HELP_COPY = Object.freeze({
  title: 'Layout help',
  how: 'Switch tab with Left or Right (tap-hold Caps + H / L). Tab moves between keys, and the card follows the focused key. Esc closes.',
  keyboard: 'Keyboard',
  toggleOut: 'Toggle out of practice',
  emergency: 'Emergency exit',
  emergencyNote: 'Shown after its runtime behaviour is verified.',
  also: 'Silent keys are drawn XX: the practice layer sends nothing for them.',
});

export const JOURNAL_COPY = Object.freeze({
  title: 'Journal',
  choose: 'To choose a row, you need to press Up Arrow or Down Arrow. Hint: Up Arrow is tap-hold Caps + K, Down Arrow is tap-hold Caps + J. Return opens the row.',
  also: 'Also from here',
  empty: 'Nothing selected.',
});

export const CONTROLS_COPY = Object.freeze({
  title: 'Controls',
  lede: 'Six keys run the game. Every one is a key the browser can see.',
  example: 'To open the journal, you need to press Q. Hint: Q is tap Q.',
  practiceTitle: 'Practice layer: all of these still work',
  practiceText: 'Physical Return, Esc and the arrows are silent on the practice layer, so the Caps gestures are the way.',
  neverTitle: 'Never game keys',
  neverText: 'Tab outside a Tab region, Space, Command or Control combinations, F1 to F12. Only ? and Backtick are commands in typing scenes. Esc does nothing in the open world.',
});

export const SETTINGS_COPY = Object.freeze({
  title: 'Settings',
  accessibility: 'Accessibility',
  largerText: { name: 'Larger text', desc: 'Body text from 18 px to 22 px.' },
  highContrast: { name: 'High contrast', desc: 'White borders and plain panels.' },
  reducedMotion: { name: 'Reduced motion', desc: 'Holds idle frames and drops fades. System follows your device setting.' },
  keyboard: { name: 'Keyboard type', desc: 'Changes the Layout help diagram and the setup steps.' },
  reset: { name: 'Reset progress', desc: 'Erases seals, stars, patches, artifacts and best scores. Settings stay.' },
  resetQuestion: 'Reset all progress?',
  resetBody: 'Seals, stars, patches, artifacts and best scores are erased. Your settings stay.',
  keep: 'Keep my progress',
  doReset: 'Reset progress',
  runSetup: 'Run setup again',
  controls: 'Controls',
});

export const ERROR_COPY = Object.freeze({
  title: 'The game could not load',
  help: 'Check that the game is served from the repository root (python3 game/tools/serve.py), then reload.',
  reload: 'Reload',
});

export const KEYBOARD_LABELS = Object.freeze({ macbook: 'MacBook', microsoft: 'Microsoft' });

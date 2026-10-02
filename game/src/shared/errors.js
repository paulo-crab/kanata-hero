// Named-file load errors. See game/CONTRACTS.md section 2.3.
export class DataLoadError extends Error {
  constructor({ file, kind, detail }) {
    super(`Cannot load ${file}: ${detail}`);
    this.name = 'DataLoadError';
    this.file = file;
    this.kind = kind;
    this.detail = detail;
  }
}

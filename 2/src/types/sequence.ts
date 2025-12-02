import type { NoteKey } from "./noteKey";

export interface Sequence {
  items: SequenceItem[];
}

export interface SequenceItem {
  br: boolean;
  notes: NoteKey[];
}

export interface SequenceCorrection {
  noteCount: number;
  sequenceLength: number;
}
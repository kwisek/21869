export type NoteKey = {
  standard: string;
  numeric: string;
  letter: string;
};

export const Notes17: Record<string, NoteKey> = {
    C4: {standard: "C4", numeric: "1", letter: "C"},
    D4: {standard: "D4", numeric: "2", letter: "D"},
    E4: {standard: "E4", numeric: "3", letter: "E"},
    F4: {standard: "F4", numeric: "4", letter: "F"},
    G4: {standard: "G4", numeric: "5", letter: "G"},
    A4: {standard: "A4", numeric: "6", letter: "A"},
    B4: {standard: "B4", numeric: "7", letter: "B"},
    C5: {standard: "C5", numeric: "1°", letter: "C°"},
    D5: {standard: "D5", numeric: "2°", letter: "D°"},
    E5: {standard: "E5", numeric: "3°", letter: "E°"},
    F5: {standard: "F5", numeric: "4°", letter: "F°"},
    G5: {standard: "G5", numeric: "5°", letter: "G°"},
    A5: {standard: "A5", numeric: "6°", letter: "A°"},
    B5: {standard: "B5", numeric: "7°", letter: "B°"},
    C6: {standard: "C6", numeric: "1°°", letter: "C°°"},
    D6: {standard: "D6", numeric: "2°°", letter: "D°°"},
    E6: {standard: "E6", numeric: "3°°", letter: "E°°"}
};

export function noteKeyOfStandard(standardNotation: string): NoteKey | null {
    return Object.values(Notes17).find(note => note.standard === standardNotation) || null;
}
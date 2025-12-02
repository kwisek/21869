import type Notation from "../enums/Notation";
import type { Sequence, SequenceItem } from "../types/sequence"

const API_URL = import.meta.env.VITE_API_URL;

const serialize_sequence = (sequence: Sequence) => {
  return JSON.stringify({
    items: sequence.items.map((item: SequenceItem) => ({
      br: item.br,
      notes: item.notes.map((note) => ({
        pitch: note.standard.charAt(0),
        octave: Number(note.standard.charAt(1))
      }))
    })),
  });
}

export const toPdf = async (sequence: Sequence, notation: Notation): Promise<void> => {

  const response = await fetch(`${API_URL}/export/pdf?notation=${notation}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: serialize_sequence(sequence)
  });

  if (!response.ok) {
    throw new Error(`Failed to export PDF: ${response.statusText}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "kalimba_notes.pdf";
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
};

export const toImage = async (sequence: Sequence, notation: Notation): Promise<void> => {

  console.log(sequence);

  const response = await fetch(`${API_URL}/export/img?notation=${notation}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: serialize_sequence(sequence)
  });


  if (!response.ok) {
    throw new Error(`Failed to export PNG: ${response.statusText}`);
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "kalimba_notes.png";
  document.body.appendChild(link);
  link.click();
  link.remove();
  window.URL.revokeObjectURL(url);
}
import type { Sequence, SequenceCorrection } from "../types/sequence";
import { noteKeyOfStandard } from "../types/noteKey";

const API_URL = import.meta.env.VITE_API_URL;

export const submitBlob = async (blob: Blob, sequenceCorrection: SequenceCorrection) => {
  const formData = new FormData();
  formData.append('blob', blob);


  const requestUrl = new URL(`${API_URL}/convert`);
  requestUrl.searchParams.append("corrNoteCount", String(sequenceCorrection.noteCount));
  requestUrl.searchParams.append("corrSequenceLength", String(sequenceCorrection.sequenceLength));

  const response = await fetch(requestUrl.toString(), {
    method: "POST",
    body: formData
  });
  const responseJson = await response.json();
  
  const sequence: Sequence = {
    items: responseJson.items.map((item: any) => ({
      br: false,
      notes: item.notes.map((note: any) => noteKeyOfStandard(note.pitch + note.octave))
    }))
  };

  return sequence;
}
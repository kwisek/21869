import type { NoteKey } from '../types/noteKey';

const audioModules = import.meta.glob('../assets/sounds/*.wav', { eager: true });

export const AUDIO_MAP: Record<string, HTMLAudioElement> = {};

for (const path in audioModules) {
  const fileModule = audioModules[path] as { default: string };
  const fileName = path.split('/').pop()?.replace('.wav', '');
  if (fileName) {
    AUDIO_MAP[fileName] = new Audio(fileModule.default);
    AUDIO_MAP[fileName].load();
  }
}

export function playNote(note: NoteKey) {
  const audio = AUDIO_MAP[note.standard];
  if (audio) {
    audio.currentTime = 0;
    audio.play();
  }
}

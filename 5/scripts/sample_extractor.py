import os
import librosa
import numpy as np
import soundfile as sf

NOTE = "E6"
FIRST_INDEX = 0
INPUT_PATH = "./data_raw/" + NOTE + ".wav"
OUTPUT_DIR = "./data_seq_base/" + NOTE
SAMPLE_RATE = 44100
NOTE_DURATION = 3.0
THRESHOLD = 0.0015
MIN_GAP = 1.5

def rms(y, frame_size):
  return np.sqrt(np.convolve(y**2, np.ones(frame_size)/frame_size, mode="same"))

def main():
  os.makedirs(OUTPUT_DIR, exist_ok=True)

  y, sr = librosa.load(INPUT_PATH, sr=SAMPLE_RATE, mono=True)
  duration_samples = int(NOTE_DURATION * sr)
  min_gap_samples = int(MIN_GAP * sr)

  envelope = rms(y, frame_size=2048)
  attack_indices = []
  last_attack = -min_gap_samples

  for i in range(len(envelope)):
    if envelope[i] > THRESHOLD and (i - last_attack > min_gap_samples):
      attack_indices.append(i)
      last_attack = i

  print(f"Found {len(attack_indices)} note(s).")

  for idx, start_sample in enumerate(attack_indices):
    end_sample = min(start_sample + duration_samples, len(y))
    note_audio = y[start_sample:end_sample]

    if len(note_audio) < duration_samples:
      note_audio = np.pad(note_audio, (0, duration_samples - len(note_audio)))

    out_path = os.path.join(OUTPUT_DIR, f"{NOTE}_{FIRST_INDEX+idx:02d}.wav")
    sf.write(out_path, note_audio, sr)
    print(f"Saved {out_path}")

if __name__ == "__main__":
  main()

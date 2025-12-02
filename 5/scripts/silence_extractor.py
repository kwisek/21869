import os
import random
from pydub import AudioSegment

def main():
  source_wav_path = "./REC.wav"
  output_dir = "./single_notes/SILENCE"
  num_clips = 50
  clip_duration_ms = 1000

  os.makedirs(output_dir, exist_ok=True)

  audio = AudioSegment.from_wav(source_wav_path)
  total_duration_ms = len(audio)

  if total_duration_ms < clip_duration_ms * num_clips:
    raise ValueError("Input file is too short.")

  max_start = total_duration_ms - clip_duration_ms
  possible_starts = list(range(0, max_start))
  random_starts = random.sample(possible_starts, num_clips)

  for i, start_ms in enumerate(random_starts):
    clip = audio[start_ms:start_ms + clip_duration_ms]
    output_path = os.path.join(output_dir, f"SILENCE_{i+1:02d}.wav")
    clip.export(output_path, format="wav")

  print(f"Saved {num_clips} silence fragments to {output_dir}")

if __name__ == "__main__":
  main()
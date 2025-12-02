import os
import sys
import re
from playsound import playsound

def play_audio(file_path):
  try:
    safe_path = os.path.abspath(file_path)
    print(f"Playing: {file_path}")
    playsound(safe_path)
    print("Done playing.")
  except Exception as e:
    print(f"Error: {e}")

def main():
  if len(sys.argv) != 2:
    print("Usage: python process_notes.py NOTE")
    sys.exit(1)

  note_dir = f"./data/{sys.argv[1]}"
  if not os.path.isdir(note_dir):
    print(f"Directory {note_dir} not found.")
    sys.exit(1)

  files =  os.listdir(note_dir)
  if not files:
    print(f"No {sys.argv[1]}_nnn.wav files found.")
    sys.exit(0)

  kept_files = []

  for fname in files:
    file_path = os.path.join(note_dir, fname)
    while True:
      print(f"\nPlaying: {fname}")
      play_audio(file_path)
      action = input("Action? [d] delete, [k] okay, [r] replay (default: okay): ").strip().lower()
      if action == "d":
        os.remove(file_path)
        print(f"Deleted {fname}")
        break
      elif action == "r":
        continue
      else:
        kept_files.append(file_path)
        print(f"Kept {fname}")
        break

  print("\nRenaming files to eliminate gaps...")
  for i, old_path in enumerate(kept_files, start=1):
    new_name = f"{sys.argv[1]}_{i:03d}.wav"
    new_path = os.path.join(note_dir, new_name)
    if os.path.basename(old_path) != new_name:
      os.rename(old_path, new_path)
      print(f"Renamed to {new_name}")
    else:
      print(f"Already correctly named: {new_name}")

  print("All done.")

if __name__ == "__main__":
  main()

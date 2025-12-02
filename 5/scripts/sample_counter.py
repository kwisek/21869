import os
import sys

def main(path):
  if not os.path.isdir(path):
    print(f"Invalid directory: {path}")
    return
  
  total_files = 0

  for entry in os.listdir(path):
    subdir_path = os.path.join(path, entry)
    if os.path.isdir(subdir_path):
      file_count = sum(1 for f in os.listdir(subdir_path) if os.path.isfile(os.path.join(subdir_path, f)))
      total_files += file_count
      print(f"{entry}: {file_count} file(s)")

  print(total_files)
    
if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python count_files.py <path>")
    sys.exit(1)
  main(sys.argv[1])

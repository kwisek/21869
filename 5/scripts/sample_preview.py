import sys
import matplotlib.pyplot as plt
from scipy.io import wavfile

def main(path):
  sample_rate, data = wavfile.read(path)

  if data.ndim > 1:
    data = data[:, 0]

  time = [i / sample_rate for i in range(len(data))]

  plt.figure(figsize=(12, 4))
  plt.plot(time, data)
  plt.title("Waveform")
  plt.xlabel("Time [s]")
  plt.ylabel("Amplitude")
  plt.tight_layout()
  plt.show()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python count_files.py <path>")
    sys.exit(1)
  main(sys.argv[1])
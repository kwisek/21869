import numpy as np
import matplotlib.pyplot as plt
import sys
from scipy.io import wavfile

def main(path):
  sample_rate, data = wavfile.read(path)
  
  if data.ndim > 1:
    data = data[:, 0]
    
  N = len(data)
  
  fft_values = np.fft.fft(data)
  fft_freq = np.fft.fftfreq(N, 1 / sample_rate)
  
  positive_freqs = fft_freq[:N // 2]
  magnitude = np.abs(fft_values[:N // 2])
  
  plt.figure(figsize=(12, 4))
  plt.plot(positive_freqs, magnitude)
  plt.title("FFT Frequency Spectrum")
  plt.xlabel("Frequency (Hz)")
  plt.ylabel("Magnitude")
  plt.xlim(0, 1500)
  plt.tight_layout()
  plt.show()

if __name__ == "__main__":
  if len(sys.argv) != 2:
    print("Usage: python count_files.py <path>")
    sys.exit(1)
  main(sys.argv[1])

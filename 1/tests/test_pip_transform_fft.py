import unittest
import numpy as np
from app.cogs.transform import linear_spectrum

class TestLinearSpectrum(unittest.TestCase):

  def test_basic_sine_peak(self):
    sr = 8000
    f = 440
    t = np.arange(0, 1.0, 1/sr)
    frame = np.sin(2 * np.pi * f * t[:4096]).astype(np.float32)

    win = np.hanning(len(frame)).astype(np.float32)

    freqs, mags = linear_spectrum(frame, sr, win)

    peak_index = np.argmax(mags)
    peak_freq = freqs[peak_index]

    self.assertAlmostEqual(peak_freq, f, delta=2.0)

  def test_fft_length_power_of_two(self):
    sr = 1000
    frame = np.random.randn(1500).astype(np.float32)
    win = np.hanning(len(frame)).astype(np.float32)

    freqs, _ = linear_spectrum(frame, sr, win)

    fft_len = len(freqs) * 2 - 2

    self.assertEqual(fft_len, 2 ** int(np.ceil(np.log2(len(frame)))))

  def test_zero_frame_returns_zero_mags(self):
    sr = 44100
    frame = np.zeros(2048, dtype=np.float32)
    win = np.ones_like(frame, dtype=np.float32)

    _, mags = linear_spectrum(frame, sr, win)

    self.assertTrue(np.allclose(mags, 0.0))

  def test_single_sample_frame(self):
    sr = 8000
    frame = np.array([1.0], dtype=np.float32)
    win = np.array([1.0], dtype=np.float32)

    freqs, mags = linear_spectrum(frame, sr, win)

    self.assertEqual(freqs.shape[0], 1)
    self.assertEqual(mags.shape[0], 1)
    self.assertEqual(freqs[0], 0.0)

  def test_window_with_zero_sum(self):
    sr = 44100
    frame = np.random.randn(1024).astype(np.float32)
    win = np.zeros(1024, dtype=np.float32)

    _, mags = linear_spectrum(frame, sr, win)

    self.assertTrue(np.any(np.isnan(mags)) or np.any(np.isinf(mags)))

  def test_shape_and_types(self):
    sr = 16000
    frame = np.random.randn(4096).astype(np.float64)
    win = np.hanning(len(frame)).astype(np.float32)

    freqs, mags = linear_spectrum(frame, sr, win)

    self.assertEqual(freqs.dtype, np.float32)
    self.assertEqual(mags.dtype, np.float32)
    self.assertEqual(freqs.shape[0], mags.shape[0])

  def test_correct_freq_resolution(self):
    sr = 48000
    frame = np.random.randn(3000).astype(np.float32)
    win = np.hanning(len(frame)).astype(np.float32)

    freqs, _ = linear_spectrum(frame, sr, win)

    df = freqs[1] - freqs[0]
    fft_len = 2 ** int(np.ceil(np.log2(len(frame))))
    expected_df = sr / fft_len

    self.assertAlmostEqual(df, expected_df, places=6)

  def test_magnitude_scaling_factor(self):
    sr = 8000
    frame = np.random.randn(1024).astype(np.float32)
    win = np.hanning(len(frame)).astype(np.float32)

    _, mags = linear_spectrum(frame, sr, win)

    fft_len = 2 ** int(np.ceil(np.log2(len(frame))))
    raw = np.abs(np.fft.rfft(frame, n=fft_len))

    scale = (np.sum(win) / 2)
    raw_scaled = raw / scale
    raw_scaled[1:-1] *= 2

    np.testing.assert_allclose(mags, raw_scaled.astype(np.float32), rtol=1e-5, atol=1e-5)

  def test_different_frame_sizes(self):
    sr = 22050
    for size in [100, 256, 1023, 2048, 5000]:
      with self.subTest(size=size):
        frame = np.random.randn(size).astype(np.float32)
        win = np.hanning(size).astype(np.float32)

        freqs, mags = linear_spectrum(frame, sr, win)

        self.assertEqual(freqs.shape[0], mags.shape[0])
        self.assertEqual(freqs.shape[0], int(np.floor((2 ** int(np.ceil(np.log2(size)))) / 2)) + 1)

  def test_constant_signal(self):
    sr = 48000
    frame = np.ones(4096, dtype=np.float32)
    win = np.hanning(len(frame)).astype(np.float32)

    _, mags = linear_spectrum(frame, sr, win)

    dc = mags[0]
    self.assertTrue(dc > 0)
    self.assertTrue(np.all(mags[1:] < dc * 0.01))


if __name__ == "__main__":
  unittest.main()

import unittest
import numpy as np
from app.cogs.transform import gaussian_smoothing

class TestGaussianSmoothing(unittest.TestCase):

  def test_constant_signal_stays_constant(self):
    freqs = np.linspace(0, 2000, 500)
    mags = np.ones(500, dtype=np.float32)

    smoothed = gaussian_smoothing(freqs, mags, gauss_sigma_hz=50, gauss_smoothing_factor=1)

    self.assertTrue(np.allclose(smoothed[50:-50], 1.0, atol=1e-5))

  def test_kernel_normalization(self):
    freqs = np.array([0, 1], dtype=np.float32)
    mags = np.ones(2, dtype=np.float32)

    smoothed = gaussian_smoothing(freqs, mags, gauss_sigma_hz=10, gauss_smoothing_factor=2)

    self.assertTrue(np.mean(smoothed) <= 1.0)

  def test_smoothing_effect(self):
    freqs = np.linspace(0, 1000, 200)
    mags = np.zeros(200, dtype=np.float32)
    mags[100:] = 1.0

    smoothed = gaussian_smoothing(freqs, mags, gauss_sigma_hz=50, gauss_smoothing_factor=1)

    self.assertTrue(smoothed[90] < smoothed[95] < smoothed[100] < smoothed[105] < smoothed[110])

  def test_large_sigma_heavily_smooths(self):
    freqs = np.linspace(0, 2000, 1000)
    mags = np.zeros(1000, dtype=np.float32)
    mags[500] = 10.0

    smoothed = gaussian_smoothing(freqs, mags, gauss_sigma_hz=2000, gauss_smoothing_factor=3)

    self.assertTrue(np.max(smoothed) < 5.0)

  def test_output_length_matches_input(self):
    freqs = np.linspace(0, 1000, 300)
    mags = np.random.rand(300).astype(np.float32)

    smoothed = gaussian_smoothing(freqs, mags, gauss_sigma_hz=10, gauss_smoothing_factor=1)

    self.assertEqual(len(smoothed), len(mags))

if __name__ == "__main__":
  unittest.main()

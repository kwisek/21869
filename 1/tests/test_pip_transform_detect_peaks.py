import unittest
import numpy as np
from app.cogs.transform import detect_peaks

class TestDetectPeaks(unittest.TestCase):

  def setUp(self):
    self.freqs = np.linspace(0, 1000, 1001)
    self.mags = np.zeros_like(self.freqs)
    self.mags[100] = 1.0
    self.mags[400] = 0.5
    self.mags[800] = 0.8

    self.freq_range_hz = (0, 1000)
    self.min_prominence = 0.1
    self.min_distance_hz = 50
    self.parabolic_denom_tol = 1e-6
    self.parabolic_delta_clip = 0.5

  def test_detect_three_peaks(self):
    peak_freqs, peak_mags = detect_peaks(
      self.freqs, self.mags,
      self.freq_range_hz,
      self.min_prominence,
      self.min_distance_hz,
      self.parabolic_denom_tol,
      self.parabolic_delta_clip
    )
    
    self.assertEqual(len(peak_freqs), 3)
    self.assertEqual(len(peak_mags), 3)
    
    np.testing.assert_allclose(peak_freqs, [self.freqs[100], self.freqs[400], self.freqs[800]], rtol=1e-2)
    np.testing.assert_allclose(peak_mags, [1.0, 0.5, 0.8], rtol=1e-5)

  def test_no_peaks_below_min_prominence(self):
    peak_freqs, peak_mags = detect_peaks(
      self.freqs, self.mags,
      self.freq_range_hz,
      min_prominence=2.0,
      min_distance_hz=50,
      parabolic_denom_tol=1e-6,
      parabolic_delta_clip=0.5
    )
    self.assertEqual(len(peak_freqs), 0)
    self.assertEqual(len(peak_mags), 0)

  def test_frequency_range_limits(self):
    peak_freqs, _ = detect_peaks(
      self.freqs, self.mags,
      freq_range_hz=(300, 900),
      min_prominence=0.1,
      min_distance_hz=50,
      parabolic_denom_tol=1e-6,
      parabolic_delta_clip=0.5
    )
    self.assertEqual(len(peak_freqs), 2)
    self.assertTrue(all(f >= 300 and f <= 900 for f in peak_freqs))

  def test_min_distance_hz_filtering(self):
    mags = np.zeros_like(self.freqs)
    mags[100] = 1.0
    mags[105] = 0.8
    peak_freqs, peak_mags = detect_peaks(
      self.freqs, mags,
      self.freq_range_hz,
      min_prominence=0.1,
      min_distance_hz=(self.freqs[105]-self.freqs[100]) * 1.5,
      parabolic_denom_tol=1e-6,
      parabolic_delta_clip=0.5
    )
    
    self.assertEqual(len(peak_freqs), 1)
    self.assertAlmostEqual(peak_mags[0], 1.0)

  def test_empty_input(self):
    freqs = np.array([])
    mags = np.array([])
    peak_freqs, peak_mags = detect_peaks(
      freqs, mags,
      self.freq_range_hz,
      self.min_prominence,
      self.min_distance_hz,
      self.parabolic_denom_tol,
      self.parabolic_delta_clip
    )
    self.assertEqual(len(peak_freqs), 0)
    self.assertEqual(len(peak_mags), 0)

  def test_single_peak(self):
    mags = np.zeros_like(self.freqs)
    mags[500] = 1.0
    peak_freqs, peak_mags = detect_peaks(
      self.freqs, mags,
      self.freq_range_hz,
      self.min_prominence,
      self.min_distance_hz,
      self.parabolic_denom_tol,
      self.parabolic_delta_clip
    )
    self.assertEqual(len(peak_freqs), 1)
    self.assertAlmostEqual(peak_freqs[0], self.freqs[500])
    self.assertAlmostEqual(peak_mags[0], 1.0)

if __name__ == "__main__":
  unittest.main()

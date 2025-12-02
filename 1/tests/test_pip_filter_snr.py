import unittest
import numpy as np
from app.cogs.filter import filter_by_snr

class TestFilterBySNR(unittest.TestCase):

  def setUp(self):
    self.freqs = np.linspace(0, 1000, 101)
    self.mags_db = np.zeros_like(self.freqs)
    self.mags_db[10] = 10.0
    self.mags_db[50] = 5.0
    self.mags_db[90] = 1.0

    self.peak_freqs = [self.freqs[10], self.freqs[50], self.freqs[90]]
    self.peak_mags_db = [10.0, 5.0, 1.0]

    self.snr_db_threshold = 3.0
    self.snr_noise_window_hz = 50
    self.snr_noise_percentile = 25

  def test_filter_peaks_above_threshold(self):
    keep_freqs, _ = filter_by_snr(
      self.freqs, self.mags_db,
      self.peak_freqs, self.peak_mags_db,
      self.snr_db_threshold,
      self.snr_noise_window_hz,
      self.snr_noise_percentile
    )
    self.assertIn(self.freqs[10], keep_freqs)
    self.assertIn(self.freqs[50], keep_freqs)
    self.assertNotIn(self.freqs[90], keep_freqs)

  def test_empty_input(self):
    keep_freqs, keep_mags = filter_by_snr(
      np.array([]), np.array([]),
      [], [],
      self.snr_db_threshold,
      self.snr_noise_window_hz,
      self.snr_noise_percentile
    )
    self.assertEqual(len(keep_freqs), 0)
    self.assertEqual(len(keep_mags), 0)

  def test_single_peak_pass(self):
    keep_freqs, keep_mags = filter_by_snr(
      self.freqs, self.mags_db,
      [self.freqs[10]], [10.0],
      3.0, 50, 25
    )
    self.assertEqual(len(keep_freqs), 1)
    self.assertEqual(keep_freqs[0], self.freqs[10])
    self.assertEqual(keep_mags[0], 10.0)

  def test_single_peak_fail(self):
    keep_freqs, keep_mags = filter_by_snr(
      self.freqs, self.mags_db,
      [self.freqs[90]], [1.0],
      3.0, 50, 25
    )
    self.assertEqual(len(keep_freqs), 0)
    self.assertEqual(len(keep_mags), 0)

  def test_noise_window_edge(self):
    peak_freqs = [self.freqs[0]]
    peak_mags = [10.0]
    keep_freqs, _ = filter_by_snr(
      self.freqs, self.mags_db,
      peak_freqs, peak_mags,
      3.0, 50, 25
    )
    self.assertEqual(len(keep_freqs), 1)
    self.assertEqual(keep_freqs[0], self.freqs[0])

  def test_output_types(self):
    keep_freqs, keep_mags = filter_by_snr(
      self.freqs, self.mags_db,
      self.peak_freqs, self.peak_mags_db,
      self.snr_db_threshold,
      self.snr_noise_window_hz,
      self.snr_noise_percentile
    )
    self.assertIsInstance(keep_freqs, np.ndarray)
    self.assertIsInstance(keep_mags, np.ndarray)

  def test_all_peaks_below_threshold(self):
    keep_freqs, keep_mags = filter_by_snr(
      self.freqs, self.mags_db,
      self.peak_freqs, self.peak_mags_db,
      snr_db_threshold=20.0,
      snr_noise_window_hz=50,
      snr_noise_percentile=25
    )
    self.assertEqual(len(keep_freqs), 0)
    self.assertEqual(len(keep_mags), 0)

  def test_partial_peaks_kept(self):
    keep_freqs, _ = filter_by_snr(
      self.freqs, self.mags_db,
      self.peak_freqs, self.peak_mags_db,
      snr_db_threshold=4.0,
      snr_noise_window_hz=50,
      snr_noise_percentile=25
    )
    self.assertEqual(len(keep_freqs), 2)
    self.assertIn(self.freqs[10], keep_freqs)
    self.assertIn(self.freqs[50], keep_freqs)
    self.assertNotIn(self.freqs[90], keep_freqs)

if __name__ == "__main__":
  unittest.main()

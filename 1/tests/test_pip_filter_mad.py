import numpy as np
import unittest
from app.cogs.models import NoteDetection
from app.cogs.filter import filter_by_mad
from app.cogs.filter.filter import _compute_mad_threshold

class TestFilterByMAD(unittest.TestCase):

  def test_empty_list_returns_empty(self):
    dets = []
    threshold = _compute_mad_threshold(dets, mad_k=2.0, mad_min_th=0.5)
    self.assertEqual(threshold, {})
    filtered = filter_by_mad(dets, mad_k=2.0, mad_min_th=0.5)
    self.assertEqual(filtered, [])

  def test_all_same_magnitude(self):
    dets = [NoteDetection("C4",0,1.0,261.63) for _ in range(5)]
    mad_k = 2.0
    mad_min_th = 0.5
    threshold = _compute_mad_threshold(dets, mad_k, mad_min_th)
    self.assertEqual(threshold.mad, 0.0)
    self.assertEqual(threshold.median, 1.0)
    self.assertEqual(threshold.threshold, max(threshold.raw_threshold, mad_min_th))
    filtered = filter_by_mad(dets, mad_k, mad_min_th)
    self.assertEqual(len(filtered), 5)

  def test_mad_threshold_calculation(self):
    mags = [1.0, 2.0, 3.0, 10.0]
    dets = [NoteDetection("N", i, mag, 100+i) for i, mag in enumerate(mags)]
    mad_k = 1.0
    mad_min_th = 0.0
    threshold = _compute_mad_threshold(dets, mad_k, mad_min_th)
    expected_median = np.median(mags)
    expected_mad = np.median(np.abs(np.array(mags)-expected_median))
    self.assertAlmostEqual(threshold.median, expected_median)
    self.assertAlmostEqual(threshold.mad, expected_mad)
    self.assertAlmostEqual(threshold.raw_threshold, expected_median + mad_k * expected_mad)

  def test_filter_by_mad_keeps_only_above_threshold(self):
    mags = [1.0, 2.0, 3.0, 10.0]
    dets = [NoteDetection("N", i, mag, 100+i) for i, mag in enumerate(mags)]
    mad_k = 1.0
    mad_min_th = 5.0  # wymusza threshold >= 5
    filtered = filter_by_mad(dets, mad_k, mad_min_th)
    self.assertEqual(len(filtered), 1)
    self.assertEqual(filtered[0].detected_mag, 10.0)

  def test_threshold_respects_mad_min_th(self):
    mags = [1.0, 1.1, 0.9]
    dets = [NoteDetection("N", i, mag, 100+i) for i, mag in enumerate(mags)]
    mad_k = 1.0
    mad_min_th = 1.05
    threshold = _compute_mad_threshold(dets, mad_k, mad_min_th)
    self.assertGreaterEqual(threshold.threshold, mad_min_th)

  def test_filtered_list_type(self):
    mags = [1.0, 2.0, 3.0]
    dets = [NoteDetection("N", i, mag, 100+i) for i, mag in enumerate(mags)]
    filtered = filter_by_mad(dets, mad_k=0.5, mad_min_th=0.0)
    self.assertIsInstance(filtered, list)
    self.assertTrue(all(isinstance(d, NoteDetection) for d in filtered))

if __name__ == "__main__":
  unittest.main()
import unittest
import numpy as np
from app.cogs.transform import convert_peaks_to_detections
from app.cogs.utils.const import KALIMBA_NOTES_17

class TestConvertPeaksToDetections(unittest.TestCase):

  def test_no_peaks_returns_empty(self):
    detections = convert_peaks_to_detections(0, np.array([]), np.array([]), 50.0)
    self.assertEqual(detections, [])

  def test_single_peak_within_tolerance(self):
    peak_freqs = np.array([KALIMBA_NOTES_17["C4"]])
    peak_mags = np.array([1.0])
    detections = convert_peaks_to_detections(1, peak_freqs, peak_mags, octave_tol_cents=50)
    self.assertEqual(len(detections), 1)
    self.assertEqual(detections[0].note_key, "C4")
    self.assertEqual(detections[0].frame_index, 1)
    self.assertEqual(detections[0].detected_mag, 1.0)
    self.assertEqual(detections[0].detected_freq, KALIMBA_NOTES_17["C4"])

  def test_peak_outside_tolerance_is_ignored(self):
    peak_freqs = np.array([300.0])
    peak_mags = np.array([1.0])
    detections = convert_peaks_to_detections(0, peak_freqs, peak_mags, octave_tol_cents=10)
    self.assertEqual(detections, [])

  def test_multiple_peaks_same_note_choose_strongest(self):
    peak_freqs = np.array([KALIMBA_NOTES_17["C4"] + 0.2, KALIMBA_NOTES_17["C4"] - 0.1])
    peak_mags = np.array([0.5, 1.2])
    detections = convert_peaks_to_detections(0, peak_freqs, peak_mags, octave_tol_cents=50)
    self.assertEqual(len(detections), 1)
    self.assertEqual(detections[0].detected_mag, 1.2)

  def test_multiple_peaks_different_notes(self):
    peak_freqs = np.array([KALIMBA_NOTES_17["C4"], KALIMBA_NOTES_17["A4"]])
    peak_mags = np.array([1.0, 0.8])
    detections = convert_peaks_to_detections(0, peak_freqs, peak_mags, octave_tol_cents=50)
    self.assertEqual(len(detections), 2)
    notes = [d.note_key for d in detections]
    self.assertIn("C4", notes)
    self.assertIn("A4", notes)

if __name__ == "__main__":
  unittest.main()
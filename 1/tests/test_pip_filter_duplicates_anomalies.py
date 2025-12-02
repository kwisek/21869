import numpy as np
import unittest
from app.cogs.filter import postprocess
from app.cogs.models import NoteDetection

class TestFilterAnomaliesAndDuplicates(unittest.TestCase):

  def test_no_detections_returns_empty(self):
    result = postprocess([], np.array([]), allowed_gap=1, min_consecutive_frames=0, growing_trend_threshold=10, conflict_cents_tol=5,
      chord_frame_tol=1, onset_snap_tol=0)
    self.assertEqual(result, [])

  def test_single_detection_passes_through(self):
    det = NoteDetection("C4", 5, 1.0, 261.63)
    result = postprocess([det], np.array([]), allowed_gap=1, min_consecutive_frames=0, growing_trend_threshold=10, conflict_cents_tol=5,
      chord_frame_tol=1, onset_snap_tol=0)
    self.assertEqual(len(result), 1)
    self.assertIs(result[0], det)

  def test_growing_trend_resets_runs(self):
    dets = [NoteDetection("C4", i, mag, 261.63) for i, mag in enumerate([1,2,3,4,5])]
    result = postprocess(dets, np.array([]), allowed_gap=1, min_consecutive_frames=0, growing_trend_threshold=2, conflict_cents_tol=5,
      chord_frame_tol=1, onset_snap_tol=0)
    self.assertTrue(len(result) > 0)

  def test_conflict_keeps_stronger_detection(self):
    d1 = NoteDetection("C4", 0, 1.0, 261.63)
    d2 = NoteDetection("D4", 0, 2.0, 261.63*(2**(1/1200)))
    result = postprocess([d1,d2], np.array([]), allowed_gap=1, min_consecutive_frames=0, growing_trend_threshold=10, conflict_cents_tol=5,
      chord_frame_tol=1, onset_snap_tol=0)
    self.assertEqual(len(result), 1)
    self.assertEqual(result[0].detected_mag, 2.0)

  def test_chord_grouping_snaps_frame(self):
    onsets = np.array([10,20,30])
    dets = [
        NoteDetection("C4", 11, 1.0, 261.63),
        NoteDetection("E4", 12, 1.0, 329.63)
    ]
    result = postprocess(dets, onsets, allowed_gap=1, min_consecutive_frames=0, growing_trend_threshold=10, conflict_cents_tol=5,
      chord_frame_tol=5, onset_snap_tol=5)
    for d in result:
      self.assertIn(d.frame_index, onsets)

  def test_multiple_notes_no_conflict(self):
    dets = [
      NoteDetection("C4", 0, 1.0, 261.63),
      NoteDetection("E4", 1, 1.0, 329.63),
      NoteDetection("G4", 2, 1.0, 392.0)
    ]
    result = postprocess(dets, np.array([]), allowed_gap=1, min_consecutive_frames=0, growing_trend_threshold=10, conflict_cents_tol=5,
      chord_frame_tol=1, onset_snap_tol=0)
    self.assertEqual(len(result), 3)

if __name__ == "__main__":
  unittest.main()
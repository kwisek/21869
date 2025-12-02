import unittest
import numpy as np
from app.cogs.transform import hanning_window

class TestHanningWindow(unittest.TestCase):

  def test_basic_hanning(self):
    sr = 100
    frame_length = 0.02
    frames = np.array([[1.0, 2.0], [3.0, 4.0]], dtype=np.float32)
    out_frames, window = hanning_window(frames.copy(), sr, frame_length)
    expected_window = np.hanning(2).astype(np.float32)
    expected_frames = frames * expected_window

    np.testing.assert_allclose(window, expected_window)
    np.testing.assert_allclose(out_frames, expected_frames)

  def test_window_shape_matches_frames(self):
    sr = 50
    frame_length = 0.1

    frames = np.ones((3, 5), dtype=np.float32)
    out_frames, window = hanning_window(frames.copy(), sr, frame_length)

    self.assertEqual(window.shape[0], 5)
    self.assertEqual(out_frames.shape, (3, 5))

  def test_inplace_modification(self):
    sr = 10
    frame_length = 0.3

    frames = np.ones((2, 3), dtype=np.float32)
    frames_copy = frames.copy()

    out_frames, _ = hanning_window(frames, sr, frame_length)

    self.assertFalse(np.array_equal(frames_copy, frames))
    np.testing.assert_allclose(out_frames, frames)

  def test_single_frame(self):
    sr = 100
    frame_length = 0.03

    frames = np.array([[1.0, 2.0, 3.0]], dtype=np.float32)
    out_frames, window = hanning_window(frames.copy(), sr, frame_length)

    expected_window = np.hanning(3).astype(np.float32)
    expected_frames = frames * expected_window

    np.testing.assert_allclose(out_frames, expected_frames)
    np.testing.assert_allclose(window, expected_window)

  def test_empty_frames_input(self):
    sr = 100
    frame_length = 0.02

    frames = np.zeros((0, 2), dtype=np.float32)
    out_frames, window = hanning_window(frames.copy(), sr, frame_length)

    self.assertEqual(out_frames.shape, (0, 2))
    self.assertEqual(window.shape, (2,))

  def test_window_values_hanning_properties(self):
    sr = 100
    frame_length = 0.04

    frames = np.ones((1, 4), dtype=np.float32)
    _, window = hanning_window(frames.copy(), sr, frame_length)

    self.assertAlmostEqual(window[0], 0.0)
    self.assertAlmostEqual(window[-1], 0.0)
    self.assertTrue(np.all(window[1:-1] > 0))


if __name__ == "__main__":
  unittest.main()

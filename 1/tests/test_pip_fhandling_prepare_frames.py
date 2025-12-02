import unittest
import numpy as np
from app.cogs.filehandling import prepare_frames

class TestPrepareFrames(unittest.TestCase):

  def test_too_short_raises(self):
    samples = np.zeros(5)
    sr = 100
    frame_length = 0.02
    hop_length = 0.5

    with self.assertRaises(AttributeError):
      prepare_frames(samples[:1], sr, frame_length, hop_length)

  def test_exactly_equal_to_frame_size_raises(self):
    sr = 1000
    frame_length = 0.01
    hop_length = 0.5
    samples = np.arange(10)

    with self.assertRaises(AttributeError):
      prepare_frames(samples, sr, frame_length, hop_length)

  def test_basic_frame_extraction_no_padding(self):
    sr = 10
    frame_length = 0.2
    hop_length = 0.5

    samples = np.array([1, 2, 3, 4, 5])
    frames = prepare_frames(samples, sr, frame_length, hop_length)
    expected = np.array([[1, 2],[2, 3],[3, 4],[4, 5]], dtype=np.float32)

    np.testing.assert_array_equal(frames, expected)

  def test_padding_occurs_correctly(self):
    sr = 10
    frame_length = 0.3
    hop_length = 1.0

    samples = np.array([10, 20, 30, 40])
    frames = prepare_frames(samples, sr, frame_length, hop_length)
    expected = np.array([[10, 20, 30],[40, 0, 0]], dtype=np.float32)

    np.testing.assert_array_equal(frames, expected)

  def test_non_integer_hop_values_zero_division(self):
    sr = 100
    frame_length = 0.015
    hop_length = 0.33

    samples = np.arange(10)

    with self.assertRaises(ZeroDivisionError):
      prepare_frames(samples, sr, frame_length, hop_length)

  def test_output_dtype_is_float32(self):
    sr = 100
    frame_length = 0.02
    hop_length = 0.5
    samples = np.arange(100, dtype=np.int16)

    frames = prepare_frames(samples, sr, frame_length, hop_length)
    self.assertEqual(frames.dtype, np.float32)

  def test_frames_are_copied_not_shared(self):
    sr = 10
    frame_length = 0.2
    hop_length = 1.0

    samples = np.array([1, 2, 3, 4], dtype=np.float32)
    frames = prepare_frames(samples, sr, frame_length, hop_length)
    frames[0, 0] = 999.0

    self.assertEqual(samples[0], 1.0)
    self.assertEqual(frames[0, 0], 999.0)

  def test_frame_count_is_correct(self):
    sr = 10
    frame_length = 0.3
    hop_length = 0.5

    samples = np.arange(10)
    frames = prepare_frames(samples, sr, frame_length, hop_length)

    self.assertEqual(frames.shape[0], 5)
    self.assertEqual(frames.shape[1], 3)

  def test_multiple_input_dtypes(self):
    sr = 20
    frame_length = 0.1
    hop_length = 0.5

    for dtype in (np.int16, np.int32, np.float32):
      samples = np.arange(10, dtype=dtype)
      frames = prepare_frames(samples, sr, frame_length, hop_length)

      self.assertEqual(frames.dtype, np.float32)
      self.assertEqual(frames.shape, (9, 2))

  def test_large_input_sanity(self):
    sr = 44100
    frame_length = 0.01
    hop_length = 0.5

    samples = np.arange(10000, dtype=np.float32)
    frames = prepare_frames(samples, sr, frame_length, hop_length)

    self.assertEqual(frames.shape[1], 441)
    self.assertGreater(frames.shape[0], 1)

if __name__ == "__main__":
  unittest.main()

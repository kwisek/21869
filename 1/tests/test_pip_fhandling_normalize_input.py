import unittest
import numpy as np
from pydub import AudioSegment
from app.cogs.filehandling import normalize_input


def make_audio(samples, channels=1):
  raw = np.array(samples, dtype=np.int16).tobytes()
  return AudioSegment(data=raw, sample_width=2, frame_rate=44100, channels=channels)

class TestNormalizeInput(unittest.TestCase):

  def test_mono_normalization_basic(self):
    audio = make_audio([1000, -1000, 500, -500], channels=1)
    arr, sr = normalize_input(audio)

    self.assertEqual(sr, 44100)
    self.assertAlmostEqual(np.max(np.abs(arr)), 1.0, places=5)

  def test_mono_all_zero(self):
    audio = make_audio([0, 0, 0, 0], channels=1)
    arr, _ = normalize_input(audio)

    self.assertTrue(np.all(arr == 0.0))

  def test_mono_single_sample(self):
    audio = make_audio([3000], channels=1)
    arr, _ = normalize_input(audio)

    self.assertEqual(len(arr), 1)
    self.assertAlmostEqual(arr[0], 1.0)

  def test_stereo_mixes_down_to_mono(self):
    audio = make_audio([1000, 3000, 2000, 4000], channels=2)
    arr, _ = normalize_input(audio)
    expected = np.array([2000, 3000], dtype=np.float32)
    expected = expected / np.max(np.abs(expected))

    np.testing.assert_allclose(arr, expected, rtol=1e-5)

  def test_stereo_with_negative_values(self):
    audio = make_audio([1000, -2000, -5000, 4000], channels=2)
    arr, _ = normalize_input(audio)
    expected = np.array([-500, -500], dtype=np.float32)
    expected = expected / np.max(np.abs(expected))

    np.testing.assert_allclose(arr, expected, rtol=1e-5)

  def test_large_values(self):
    audio = make_audio([32767, -32768, 10000, -12345], channels=1)
    arr, _ = normalize_input(audio)

    self.assertAlmostEqual(np.max(np.abs(arr)), 1.0, places=6)

  def test_peak_is_the_absolute_max(self):
    audio = make_audio([100, -300, 200, -150], channels=1)
    arr, _ = normalize_input(audio)
    
    self.assertAlmostEqual(arr[1], -1.0)

  def test_output_type_and_shape(self):
    audio = make_audio([100, 200, -50], channels=1)
    arr, _ = normalize_input(audio)

    self.assertIsInstance(arr, np.ndarray)
    self.assertEqual(arr.dtype, np.float32)
    self.assertEqual(len(arr), 3)

  def test_no_modification_if_peak_zero(self):
    audio = make_audio([0, 0, 0], channels=1)
    arr, _ = normalize_input(audio)

    self.assertTrue(np.all(arr == 0))
    self.assertEqual(arr.dtype, np.float32)

if __name__ == "__main__":
  unittest.main()

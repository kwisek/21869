import unittest
import numpy as np
from app.cogs.transform import map_to_db
from app.cogs.utils.const import EPS

class TestMapToDB(unittest.TestCase):

  def test_basic_conversion(self):
    mags = np.array([1.0, 0.5, 0.1], dtype=np.float32)
    ref = 1.0
    db = map_to_db(mags, ref)
    expected = 20 * np.log10(np.array([1.0, 0.5, 0.1], dtype=np.float32) / ref)
    np.testing.assert_allclose(db, expected, rtol=1e-5)
    self.assertEqual(db.dtype, np.float32)

  def test_custom_min_db(self):
    mags = np.array([1e-10, 1e-5, 0.1], dtype=np.float32)
    ref = 1.0
    db = map_to_db(mags, ref, min_db=-60.0)
    self.assertTrue(np.all(db >= -60.0))

  def test_ref_less_than_eps(self):
    mags = np.array([1.0, 0.5, 0.1], dtype=np.float32)
    ref = 0.0
    db = map_to_db(mags, ref)
    expected = 20 * np.log10(np.maximum(mags, EPS) / EPS)
    np.testing.assert_allclose(db, expected, rtol=1e-5)

  def test_output_type(self):
    mags = np.array([1.0, 0.5, 0.1], dtype=np.float32)
    db = map_to_db(mags, ref=1.0)
    self.assertEqual(db.dtype, np.float32)

if __name__ == "__main__":
  unittest.main()

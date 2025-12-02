import unittest
import numpy as np
from app.cogs.models import PipelineConfig
from gen.main import denormalize_param, vector_to_param_dict, vector_to_pipeline_config, SEARCH_SPACE

class TestGenParamsHandling(unittest.TestCase):

  def test_denormalize_param_linear_float(self):
    spec = {'type': 'float', 'bounds': [0.0, 10.0], 'scale': 'linear'}
    # lower bound
    self.assertAlmostEqual(denormalize_param(0.0, spec), 0.0)
    # upper bound
    self.assertAlmostEqual(denormalize_param(1.0, spec), 10.0)
    # normalized 0.5 -> middle
    self.assertAlmostEqual(denormalize_param(0.5, spec), 5.0)
    # clamping
    self.assertAlmostEqual(denormalize_param(-0.5, spec), 0.0)
    self.assertAlmostEqual(denormalize_param(1.5, spec), 10.0)

  def test_denormalize_param_linear_int(self):
    spec = {'type': 'int', 'bounds': [0, 5], 'scale': 'linear'}
    # lower bound
    self.assertEqual(denormalize_param(0.0, spec), 0)
    # upper bound
    self.assertEqual(denormalize_param(1.0, spec), 5)
    # normalized 0.5 -> rounds to nearest int
    self.assertEqual(denormalize_param(0.5, spec), 2)
  
  def test_denormalize_param_log_float(self):
    spec = {'type': 'float', 'bounds': [1.0, 100.0], 'scale': 'log'}
    # normalized 0 -> low bound
    self.assertAlmostEqual(denormalize_param(0.0, spec), 1.0)
    # normalized 1 -> high bound
    self.assertAlmostEqual(denormalize_param(1.0, spec), 100.0)
    # normalized 0.5 -> midpoint should be geometric mean ~10
    self.assertAlmostEqual(denormalize_param(0.5, spec), 10.0, delta=0.1)

  def test_vector_to_param_dict_length_mismatch(self):
    vec = np.array([0.1, 0.2])
    search_space_small = {'a': {'type': 'float', 'bounds':[0,1]}}
    with self.assertRaises(ValueError):
      vector_to_param_dict(vec, search_space_small)

  def test_vector_to_param_dict_keys_and_values(self):
    vec = np.ones(len(SEARCH_SPACE))
    param_dict = vector_to_param_dict(vec, SEARCH_SPACE)
    self.assertEqual(set(param_dict.keys()), set(SEARCH_SPACE.keys()))

    for k, spec in SEARCH_SPACE.items():
      val = param_dict[k]
      if spec['type'] == 'int':
        self.assertEqual(val, spec['bounds'][1])
      else:
        self.assertAlmostEqual(val, spec['bounds'][1])
      
  def test_vector_to_pipeline_config_instance(self):
    vec = np.ones(len(SEARCH_SPACE))
    cfg = vector_to_pipeline_config(vec, SEARCH_SPACE)
    self.assertIsInstance(cfg, PipelineConfig)
    self.assertEqual(cfg.mad_factor, SEARCH_SPACE['MAD_K']['bounds'][1])
    self.assertEqual(cfg.postproc_min_consecutive_fr, SEARCH_SPACE['MIN_CONSECUTIVE_FRAMES']['bounds'][1])

if __name__ == '__main__':
    unittest.main()
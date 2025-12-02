import random
import numpy as np

def initialize_default_population(pop_size: int, vec_len: int, rng: random.Random) -> np.ndarray:
  return [get_random_individual(rng, vec_len) for _ in range(pop_size)]

def get_random_individual(rng: random.Random, dim: int) -> np.ndarray:
  return np.array([rng.random() for _ in range(dim)], dtype=float)

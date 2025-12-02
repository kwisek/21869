import random
import os
from typing import List

def select_random_samples(n_samples: int) -> List[str]:
  data_path = os.path.join("gen", "dataset", "samples")
  output: List[str] = []

  for _ in range(n_samples):
    sample_dir = random.choice(os.listdir(data_path))
    sample_file = random.choice(os.listdir(os.path.join(data_path, sample_dir)))
    output.append(os.path.join(data_path, sample_dir, sample_file))

  return output

def select_random_sequences(n_sequences: int) -> List[str]:
  data_path = os.path.join("gen", "dataset", "sequences")
  output: List[str] = []

  for _ in range(n_sequences):
    sequence_file = random.choice(os.listdir(data_path))
    output.append(os.path.join(data_path, sequence_file))

  return output
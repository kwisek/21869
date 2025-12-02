import os
import re
import logging
import numpy as np
import math
import time
from app.logger import setup_logging
from app.cogs.models import Sequence, PipelineConfig
from random import Random
from typing import Any, Dict, List, Tuple
from .cogs.sample_picker import select_random_samples, select_random_sequences
from .cogs.population import initialize_default_population, get_random_individual
from .cogs.params import SEARCH_SPACE
from app.cogs import run_pipeline

SAVE_PATH = os.path.join("data", "population.npy")

log = logging.getLogger(__name__)

time_buf = np.zeros(500, dtype=float)
time_idx = 0
time_cnt = 0

def time_register(val: float) -> None:
  global time_idx, time_cnt
  time_buf[time_idx] = val
  time_idx = (time_idx + 1) % 500
  time_cnt += 1

def time_mean() -> float:
  return np.mean(time_buf[:time_cnt]) if time_cnt < 500 else np.mean(time_buf)

def denormalize_param(norm_value: float, spec: Dict[str, Any]) -> Any:
  low, high = spec['bounds']
  scale = spec.get('scale', 'linear')
  typ = spec['type']

  low_t, high_t = math.log(low), math.log(high) if scale == 'log' else float(low), float(high)

  nv = min(max(norm_value, 0.0), 1.0)
  val_t = low_t + nv * (high_t - low_t)
  real_val = math.exp(val_t) if scale == 'log' else val_t

  return int(min(max(round(real_val), int(low)), int(high))) if typ == 'int' else float(min(max(real_val, low), high))

def vector_to_param_dict(vec: np.ndarray, search_space: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
  result = {}
  vec_i = 0

  for key, spec in search_space.items():
    if spec["type"] == "const":
      result[key] = spec["value"]
    else:
      result[key] = denormalize_param(float(vec[vec_i]), spec)
      vec_i += 1

  if vec_i != len(vec):
    raise ValueError(f"Vector length {len(vec)} does not match non-const parameters {vec_i}")

  return result


def vector_to_pipeline_config(vec: np.ndarray, search_space: Dict[str, Dict[str, Any]]) -> PipelineConfig:
  param_dict = vector_to_param_dict(vec, search_space)
  return PipelineConfig(**param_dict)

def call_fn(file_path: str, individual: np.ndarray, search_space: Dict[str, Dict[str, Any]]) -> Sequence:

  cfg = vector_to_pipeline_config(individual, search_space)
  audio_bytes = open(file_path, "rb").read()
  return run_pipeline(audio_bytes, cfg)

def _lcs_length(a: List[str], b: List[str]) -> int:

  if not a or not b:
    return 0
  
  if len(b) < len(a):
    a, b = b, a
  prev = [0] * (len(b) + 1)
  for x in a:
    curr = [0] * (len(b) + 1)
    for j, y in enumerate(b, start=1):
      curr[j] = prev[j-1] + 1 if x == y else prev[j] if prev[j] >= curr[j-1] else curr[j-1]
    prev = curr
  return prev[-1]

def _parse_tokens_from_seq(seq: Sequence) -> List[str]:
  parts = []
  for item in seq.items:
    note_str = " ".join(f"{n.pitch}{n.octave}" for n in item.notes)
    parts.append(f"({note_str})" if len(item.notes) > 1 else note_str)
  return parts
   
def _parse_tokens_from_str(seq: str) -> List[str]:
  return [] if not seq or not seq.strip() else re.findall(r"\([^)]*\)|[^ ]+", seq)

def _chord_to_notes(token: str) -> List[str]:
  if token.startswith("(") and token.endswith(")"):
    inner = token[1:-1]
    notes = [t.strip() for t in re.findall(r"[^() ]+", inner) if t.strip()]
    return sorted(notes)
  else:
    return [token.strip()]

def _flatten_chords(chord_tokens: List[str]) -> List[str]:
  flat = []
  for tok in chord_tokens:
    notes = sorted(_chord_to_notes(tok))
    flat.extend(notes)
  return flat

def score_sequence(expected: str, actual: str) -> Tuple[float, float]:
  SEQ_LEN_WEIGHT = 1.0
  CHORD_SIZE_WEIGHT = 0.3
  CHORD_NOTE_F1_WEIGHT = 1.0
  ORDER_NOTE_WEIGHT = 2.0
  EXTRA_NOTE_PENALTY = 0.5

  exp_tokens = _parse_tokens_from_str(expected)
  act_tokens = _parse_tokens_from_str(actual)

  n_exp = len(exp_tokens)
  n_act = len(act_tokens)

  exp_chords = [_chord_to_notes(t) for t in exp_tokens]
  act_chords = [_chord_to_notes(t) for t in act_tokens]

  total_expected_notes = sum(len(c) for c in exp_chords)
  total_actual_notes = sum(len(c) for c in act_chords)

  if total_expected_notes == 0 and total_actual_notes == 0:
    return (1.0, 1.0)
  if total_expected_notes == 0:
    return (0.0, 1.0)

  seq_len_score = 0.0
  if max(n_exp, n_act) > 0:
      seq_len_score = SEQ_LEN_WEIGHT * max(0.0, 1.0 - abs(n_exp - n_act) / max(n_exp, n_act))

  chord_size_score = 0.0
  for i in range(min(n_exp, n_act)):
    le = len(exp_chords[i])
    la = len(act_chords[i])
    if max(le, la) == 0:
      chord_size_norm = 1.0
    else:
      chord_size_norm = max(0.0, 1.0 - abs(le - la) / max(le, la))
    chord_size_score += CHORD_SIZE_WEIGHT * chord_size_norm

  chord_note_score = 0.0
  for i in range(min(n_exp, n_act)):
    exp_set = set(exp_chords[i])
    act_set = set(act_chords[i])
    if not exp_set and not act_set:
      f1 = 1.0
    else:
      overlap = len(exp_set & act_set)
      denom = len(exp_set) + len(act_set)
      f1 = 0.0 if denom == 0 else (2.0 * overlap) / denom
    chord_note_score += CHORD_NOTE_F1_WEIGHT * f1

  exp_flat = _flatten_chords(exp_tokens)
  act_flat = _flatten_chords(act_tokens)
  lcs_len = _lcs_length(exp_flat, act_flat)
  order_score = ORDER_NOTE_WEIGHT * lcs_len

  unmatched_actual = max(0, total_actual_notes - lcs_len)
  penalty = EXTRA_NOTE_PENALTY * unmatched_actual

  score = seq_len_score + chord_size_score + chord_note_score + order_score - penalty

  max_score = (
      SEQ_LEN_WEIGHT
      + CHORD_SIZE_WEIGHT * n_exp
      + CHORD_NOTE_F1_WEIGHT * n_exp
      + ORDER_NOTE_WEIGHT * total_expected_notes
  )

  score = 0.0 if score < 0.0 else max_score if score > max_score else score
  return (float(score), float(max_score))

def mutate(ind: np.ndarray, rng: Random, mutation_rate: float = 0.1, mutation_strength: float = 0.1) -> np.ndarray:
  child = ind.copy()
  for i in range(len(child)):
    if rng.random() < mutation_rate:
      delta = rng.uniform(-mutation_strength, mutation_strength)
      child[i] = np.clip(child[i] + delta, 0.0, 1.0)
  return child

def crossover(parent1: np.ndarray, parent2: np.ndarray, rng: Random) -> np.ndarray:
  child = np.array([p1 if rng.random() < 0.5 else p2 for p1, p2 in zip(parent1, parent2)], dtype=float)
  return child

def tournament_selection(population: List[np.ndarray], fitnesses: List[float], rng: Random, k: int = 3) -> np.ndarray:
  assert len(population) == len(fitnesses)
  indices = rng.sample(range(len(population)), k)
  best_idx = max(indices, key=lambda idx: fitnesses[idx])
  return population[best_idx]

def search_space_vector_length(search_space: Dict[str, Dict[str, Any]]) -> int:
  return sum(1 for spec in search_space.values() if spec["type"] != "const")

def _parse_sequence_filename(file_name: str) -> str:
  output: List[str] = []
  for item in file_name[4:-4].split("__"):
    item_notes = item.split("_")
    output.append("(" + " ".join(item_notes) + ")" if len(item_notes) > 1 else item_notes[0])
  return " ".join(output)

def _parse_sample_filename(file_name: str) -> str:
  notes = file_name[:-8].split("_")
  return "" if notes[0] == "SILENCE" else notes[0] if len(notes) == 1 else f"({' '.join(notes)})" 

def _file_name_to_expected_result(file_name: str) -> str:
  return _parse_sequence_filename(file_name) if file_name[0].isdigit() else _parse_sample_filename(file_name)

def run_ga(pop_size: int, generations: int, search_space: Dict[str, Dict[str, Any]], survival_ratio: float, samples_per_generation: int, sequences_per_generation: int):
  log.info(f"GA parameters are: pop_size={pop_size}, generations={generations}, samples_per_generation={samples_per_generation}, sequences_per_generation={sequences_per_generation}")
  log.info(f"Search space is {search_space}")
  rng = Random()
  vec_len = search_space_vector_length(search_space)
  population = (
    np.load(SAVE_PATH)
    if os.path.isfile(SAVE_PATH)
    else initialize_default_population(pop_size, vec_len, rng)
  )
  log.info(f"Initialized the default population of {len(population)} individuals.")
  log.info(f"After each generation, {math.ceil(pop_size * survival_ratio)} individuals will survive, and {math.ceil(pop_size * (1 - survival_ratio))} random ones will join the population.")

  np.save(SAVE_PATH, population)
    
  best_individual_globally = None
  best_fitness_globally = -np.inf
  
  for i in range(generations):
    log.info(f"=== GENERATION {i} ===")

    random_samples = select_random_samples(samples_per_generation)
    random_sequences = select_random_sequences(sequences_per_generation)

    random_sound_samples = random_samples + random_sequences
    log.info(f"Selected {len(random_samples)} random simple samples: {random_samples}")
    log.info(f"Selected {len(random_sequences)} random complex samples: {random_sequences}")

    fitnesses = []
    for idx, individual in enumerate(population):

      timestamp_begin = time.time()

      total_score = 0.0
      total_max   = 0.0
      
      skipped_empty_results = 0

      for file_path in random_sound_samples:
        result = call_fn(file_path, individual, search_space)
        result_str = ' '.join(_parse_tokens_from_seq(result))
        
        log.debug(f"Result str is '{result_str}'")
        
        expected_result = _file_name_to_expected_result(os.path.basename(file_path))
        
        score, max_score = score_sequence(expected_result, result_str)
        total_score += score
        total_max   += max_score
        
        if result_str:
          log.info(f"Gen: {i} -- Individual: {idx+1}/{pop_size} -- PROGRESSING -- Sample: '{file_path}' -- Result: '{result_str}' -- Expected result: '{expected_result}' -- Score {score:.1f}/{max_score}")
        else:
          skipped_empty_results += 1
      fitness = total_score / total_max if total_max > 0 else 0.0
      fitnesses.append(fitness)

      elapsed_time = time.time() - timestamp_begin
      time_register(elapsed_time)

      log.info(f"Gen: {i} -- Individual: {idx+1}/{pop_size} -- COMPLETED -- Total fitness: {fitness:.3f} -- Skipped empty results: {skipped_empty_results} -- Time: {elapsed_time:.3f}s")

    best_idx, _ = max(enumerate(fitnesses), key=lambda x: x[1])

    if fitnesses[best_idx] > best_fitness_globally:
      best_individual_globally = population[best_idx].copy()
      best_fitness_globally = fitnesses[best_idx]

    np.save(SAVE_PATH, population)
    log.info(f"Saved population for generation {i} to {os.path.abspath(SAVE_PATH)}")

    new_population = [best_individual_globally]
    while len(new_population) < pop_size * survival_ratio:
      parent1 = tournament_selection(population, fitnesses, rng, k=3)
      parent2 = tournament_selection(population, fitnesses, rng, k=3)
      
      child = crossover(parent1, parent2, rng)
      child = mutate(child, rng, mutation_rate=0.2, mutation_strength=0.5)

      new_population.append(child)

    while len(new_population) < pop_size:
      new_population.append(get_random_individual(rng, vec_len))

      
    time_minutes, time_seconds = divmod(int(time_mean() * pop_size), 60)

    population = new_population
    log.info(f"================================")
    log.info(f"=== GENERATION {i} COMPLETED ===")
    log.info(f"================================")
    log.info(f"Three best fitness scores in generation {i}: {sorted(fitnesses, reverse=True)[:3]}")
    log.info(f"Best individual in generation {i}: {vector_to_param_dict(best_individual_globally, SEARCH_SPACE)}")
    log.info(f"Best global fitness: {best_fitness_globally}")
    log.info(f"Estimated time per generation: {time_minutes:02d}:{time_seconds:02d}")
    log.info(f"================================")

  log.info(f"Run completed.")
  log.info(f"Best individual (fitness={best_fitness_globally}): {vector_to_param_dict(best_individual_globally, SEARCH_SPACE)}")

def setup_ga():
  run_ga(pop_size=150, generations=9999, search_space=SEARCH_SPACE, survival_ratio=0.9, samples_per_generation=5, sequences_per_generation=2)

if __name__ == "__main__":
  setup_logging(logging.INFO)
  setup_ga()
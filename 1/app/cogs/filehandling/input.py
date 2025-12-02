import logging
import io
import numpy as np
from typing import Tuple
from pydub import AudioSegment

log = logging.getLogger(__name__)

def read_file(path: str) -> AudioSegment:
  return AudioSegment.from_file(path)

def read_bytes(blob: bytes) -> AudioSegment:
  return AudioSegment.from_file(io.BytesIO(blob))

def normalize_input(audio: AudioSegment) -> Tuple[np.ndarray, int]:
  data = np.array(audio.get_array_of_samples()).astype(np.float32)

  if audio.channels > 1:
    data = data.reshape((-1, audio.channels))
    data = np.mean(data, axis=1)

  peak = np.max(np.abs(data))
  if peak > 0:
    data = data / peak

  return data.astype(np.float32), audio.frame_rate

def prepare_frames(samples: np.ndarray, sr: int, frame_length: int, hop_length: float) -> np.ndarray:
  frame_size = int(round(frame_length * sr))
  hop_size = int(round(frame_length * hop_length * sr))

  if len(samples) <= frame_size:
    raise AttributeError("Input is too short")

  n_frames = 1 + int(np.ceil((len(samples) - frame_size) / hop_size))
  pad_len = (n_frames - 1) * hop_size + frame_size - len(samples)
  if pad_len > 0:
    samples = np.concatenate([samples, np.zeros(pad_len, dtype=samples.dtype)])

  strides = (samples.strides[0] * hop_size, samples.strides[0])
  frames = np.lib.stride_tricks.as_strided(samples, shape=(n_frames, frame_size), strides=strides)
  frames = frames.copy()
  
  log.debug(f"total_samples='{samples.shape[0]}' sr='{sr}', frame_size='{frame_size}', hop_size='{hop_size}', frame_count='{frames.shape[0]}'")

  return frames.astype(np.float32)
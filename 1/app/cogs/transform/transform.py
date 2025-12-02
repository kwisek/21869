import logging
import numpy as np
from collections import defaultdict
from typing import Dict, List, Tuple
from app.cogs.models import NoteDetection
from app.cogs.utils.const import EPS, KALIMBA_NOTES_17
from scipy.signal import peak_prominences, find_peaks
from app.cogs.models import Sequence, SequenceItem, SequenceItemNote
from scipy.ndimage import uniform_filter1d

log = logging.getLogger(__name__)

def hanning_window(frames: np.ndarray, sr: int, frame_length: float) -> Tuple[np.ndarray, np.ndarray]:
  frame_size = int(round(frame_length * sr))
  window = np.hanning(frame_size).astype(np.float32)
  frames *= window
  return frames, window

def linear_spectrum(frame: np.ndarray, sr: int, win: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
  fft_len = 2**int(np.ceil(np.log2(len(frame))))
  mags = np.abs(np.fft.rfft(frame, n=fft_len)) / (np.sum(win) / 2)
  mags[1:-1] *= 2
  freqs = np.fft.rfftfreq(fft_len, d=1/sr)
  return freqs.astype(np.float32), mags.astype(np.float32)

def map_to_db(mags: np.ndarray, ref: float, min_db: float = -120.0) -> np.ndarray:
  ref = float(max(ref, EPS))
  mags_safe = np.maximum(mags, EPS)
  db = 20.0 * np.log10(mags_safe / ref)
  return np.maximum(db, min_db).astype(np.float32)

def gaussian_smoothing(freqs: np.ndarray, mags: np.ndarray, gauss_sigma_hz: float, gauss_smoothing_factor: float) -> np.ndarray:
  df = freqs[1] - freqs[0]
  sigma_bins = max(0.5, gauss_sigma_hz / df)
  half = int(np.ceil(gauss_smoothing_factor * sigma_bins))
  x = np.arange(-half, half + 1)
  kern = np.exp(-0.5 * (x / sigma_bins) ** 2)
  kern /= kern.sum()
  return np.convolve(mags.astype(np.float32), kern, mode='same')

def construct_output_string(detections: List[NoteDetection]) -> str:
  if not detections:
    return ""

  frame_map = defaultdict(list)
  for det in detections:
    log.debug(det)
    frame_map[det.frame_index].append(det)

  sorted_frames = sorted(frame_map.items())

  note_sequence: List[str] = []
  for _, dets in sorted_frames:
    if len(dets) == 1:
      note_sequence.append(dets[0].note_key)
    else:
      note_sequence.append(f"({', '.join(map(lambda x: x.note_key, dets))})")

  return " ".join(note_sequence)


def construct_output_sequence(detections: List[NoteDetection]) -> Sequence:
  frame_map = defaultdict(list)
  for det in detections:
    frame_map[det.frame_index].append(det)

  sorted_frames = sorted(frame_map.items())
  note_order = list(KALIMBA_NOTES_17.keys())
  note_order_index = {note: idx for idx, note in enumerate(note_order)}

  items: List[SequenceItem] = []

  for _, dets in sorted_frames:
    dets_sorted = sorted(dets, key=lambda d: note_order_index[d.note_key])
    
    items.append(SequenceItem(
      br=False,
      notes=[SequenceItemNote(pitch=det.note_key[0], octave=str(det.note_key[1])) for det in dets_sorted]
    ))

  return Sequence(items=items)


def convert_peaks_to_detections(frame_index: int, peak_freqs: np.ndarray, peak_mags: np.ndarray, octave_tol_cents: float) -> List[NoteDetection]:
  result: Dict[str, NoteDetection] = {}
  
  if len(peak_freqs) == 0:
    return []
  
  note_keys = list(KALIMBA_NOTES_17.keys())
  note_freqs = np.array([KALIMBA_NOTES_17[k] for k in note_keys])

  for index, freq in enumerate(peak_freqs):
    cents_diffs = 1200.0 * np.abs(np.log2(freq / note_freqs + EPS))
    closest_index = cents_diffs.argmin()
    closest_note = note_keys[closest_index]

    if cents_diffs[closest_index] <= octave_tol_cents:
      detection = NoteDetection(closest_note, frame_index, peak_mags[index], peak_freqs[index])
      existing = result.get(closest_note)
      if existing is None or detection.detected_mag > existing.detected_mag:
        result[closest_note] = detection

  return list(result.values())

def _filter_peaks(freqs: np.ndarray, peaks: np.ndarray, prominences: np.ndarray, freq_range_hz: Tuple[int, int], min_prominence: float, min_distance_hz: float) -> np.ndarray:
  
  mask = (freqs >= freq_range_hz[0]) & (freqs <= freq_range_hz[1])

  if peaks.size == 0:
    return np.array([], dtype=int)

  keep = prominences >= min_prominence
  peaks = peaks[keep]
  prominences = prominences[keep]

  global_bins = np.where(mask)[0][peaks]

  if len(global_bins) <= 1:
    return global_bins

  df = freqs[1] - freqs[0]
  min_bins = max(1, int(round(min_distance_hz / df)))

  order = np.argsort(-prominences)
  chosen = np.zeros(len(global_bins), dtype=bool)
  final = []
  for o in order:
    if chosen[o]:
      continue
    b = global_bins[o]
    final.append(b)
    
    for j_idx, b2 in enumerate(global_bins):
      if not chosen[j_idx] and abs(b2 - b) <= min_bins:
        chosen[j_idx] = True
  final = np.array(sorted(final))
  
  return final

def _find_peaks_and_prominences(freqs: np.ndarray, mags: np.ndarray, freq_range_hz: Tuple[int, int], *, height=None, distance=None, prominence=None, width=None) -> Tuple[np.ndarray, np.ndarray]:
  mask = (freqs >= freq_range_hz[0]) & (freqs <= freq_range_hz[1])
  if not np.any(mask):
    return np.array([], dtype=int), np.array([], dtype=float)

  mags_masked = np.asarray(mags)[mask]

  if len(mags_masked) < 3:
    return np.array([], dtype=int), np.array([], dtype=float)
  
  peaks, _ = find_peaks(mags_masked, height=height, distance=distance, prominence=prominence, width=width)

  if peaks.size == 0:
    return peaks, np.array([], dtype=float)

  prominences, _, _ = peak_prominences(mags_masked, peaks)

  return peaks, prominences

def parabolic_peak(freqs: np.ndarray, mags: np.ndarray, bin_idx: int, parabolic_denom_tol: float, parabolic_delta_clip: float) -> float:        
  N = len(mags)

  if bin_idx <= 0 or bin_idx >= N - 1:
    return freqs[bin_idx]
  
  y0 = mags[bin_idx-1]
  y1 = mags[bin_idx]
  y2 = mags[bin_idx+1]

  denom = (y0 - 2.0 * y1 + y2)

  delta = 0.0 if abs(denom) < parabolic_denom_tol else float(np.clip(0.5 * (y0 - y2) / denom, -parabolic_delta_clip, parabolic_delta_clip))
  df = freqs[1] - freqs[0]

  return freqs[bin_idx] + delta * df

def detect_peaks(freqs: np.ndarray, mags: np.ndarray, freq_range_hz: Tuple[int, int], min_prominence: float, min_distance_hz: float, parabolic_denom_tol: float, parabolic_delta_clip: float) -> Tuple[np.ndarray, np.ndarray]:
  peaks, prominences = _find_peaks_and_prominences(freqs, mags, freq_range_hz)
  peak_bins = _filter_peaks(freqs, peaks, prominences, freq_range_hz, min_prominence, min_distance_hz)

  peak_freqs: List[float] = []
  peak_mags: List[float] = []
  for bin_idx in peak_bins:
    f_est = parabolic_peak(freqs, mags, bin_idx, parabolic_denom_tol, parabolic_delta_clip)
    peak_freqs.append(f_est)
    peak_mags.append(mags[bin_idx])

  return peak_freqs, peak_mags

def detect_onsets(all_mags: np.ndarray, flux_percentile: int, flux_scale: float, flux_smooth: int) -> np.ndarray:
  diff = np.diff(all_mags, axis=0)
  diff_pos = np.maximum(0.0, diff)
  flux = np.sqrt(np.sum(diff_pos**2, axis=1))
  flux = np.concatenate(([0.0], flux))
  
  if flux_smooth > 1:
    flux = uniform_filter1d(flux, size=flux_smooth)
  
  flux_thr = max(1e-6, np.percentile(flux, flux_percentile) * flux_scale)
  onsets = np.where(flux > flux_thr)[0]
  return onsets

def snap_to_onset(frame_idx: int, onsets: np.ndarray, onset_snap_tol: float) -> float:
  if len(onsets) == 0:
    return frame_idx
  pos = np.searchsorted(onsets, frame_idx)
  candidates = []
  if pos < len(onsets):
    candidates.append(onsets[pos])
  if pos > 0:
    candidates.append(onsets[pos-1])
  nearest = min(candidates, key=lambda x: abs(x - frame_idx))
  return nearest if abs(nearest - frame_idx) <= onset_snap_tol else frame_idx

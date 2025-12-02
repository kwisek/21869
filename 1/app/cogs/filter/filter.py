import logging
from collections import defaultdict
from dataclasses import dataclass
import numpy as np
from typing import Dict, List, Tuple
from app.cogs.models import NoteDetection
from app.cogs.transform import snap_to_onset

log = logging.getLogger(__name__)

@dataclass
class MadThreshold:
  median: float
  mad: float
  raw_threshold: float
  threshold: float
  n: int

def _compute_mad_threshold(dets: List[NoteDetection], mad_k: float, mad_min_th: float) -> MadThreshold:

  all_mag = [det.detected_mag for det in dets]

  if len(all_mag) == 0:
    return {}
  
  global_arr = np.asarray(all_mag, dtype=float)
  global_median = float(np.median(global_arr))
  global_mad = float(np.median(np.abs(global_arr - global_median)))
  global_raw_threshold = global_median + mad_k * global_mad
  global_threshold = max(global_raw_threshold, mad_min_th)

  log.debug(f"MAD threshold: median={global_median:.5f}, MAD={global_mad:.5f}, threshold={global_threshold:.5f}, raw_threshold={global_raw_threshold:.5f}, n={len(global_arr)}")

  return MadThreshold(global_median, global_mad, global_raw_threshold, global_threshold, len(global_arr))

def filter_by_mad(dets: List[NoteDetection], mad_k: float, mad_min_th: float) -> List[NoteDetection]:
  mad_threshold = _compute_mad_threshold(dets, mad_k, mad_min_th)
  return list(filter(lambda det: det.detected_mag >= mad_threshold.threshold, dets))


def _cents_diff(f1: float, f2: float) -> float:
    if f1 <= 0 or f2 <= 0:
        return float('inf')
    return 1200.0 * abs(np.log2(f1 / f2))

def postprocess(detections: List[NoteDetection], onsets: np.ndarray, allowed_gap: int, min_consecutive_frames: int, growing_trend_threshold: int, conflict_cents_tol: float, chord_frame_tol: int, onset_snap_tol: int) -> List[NoteDetection]:
    
  if not detections:
    return []

  detections = sorted(detections, key=lambda d: (d.note_key, d.frame_index))

  grouped_detections: Dict[str, List[NoteDetection]] = defaultdict(list)
  for d in detections:
    grouped_detections[d.note_key].append(d)

  all_mags = np.array([d.detected_mag for d in detections])
  runs_by_note: Dict[str, List[List[NoteDetection]]] = defaultdict(list)
  for note_key, det_list in grouped_detections.items():
    curr_run = [det_list[0]]
    growing_count = 0
    for d in det_list[1:]:
      prev = curr_run[-1]
      growing_count = growing_count + 1 if d.detected_mag > prev.detected_mag else 0

      if growing_count > growing_trend_threshold:
        if len(curr_run) > min_consecutive_frames:
          runs_by_note[note_key].append(curr_run)
        curr_run = [d]
        growing_count = 0
        continue

      if d.frame_index <= prev.frame_index + 1 + allowed_gap:
        curr_run.append(d)
      else:
        if len(curr_run) > min_consecutive_frames or max(d.detected_mag for d in curr_run) > np.percentile(all_mags, 75):
          runs_by_note[note_key].append(curr_run)

        curr_run = [d]
        growing_count = 0
    if curr_run:
      runs_by_note[note_key].append(curr_run)

  merged_runs = []
  for runs in runs_by_note.values():
    merged = [runs[0]]
    for r in runs[1:]:
      prev = merged[-1]
      if r[0].frame_index - prev[-1].frame_index <= allowed_gap:
        merged[-1].extend(r)
      else:
        merged.append(r)
    merged_runs.extend(merged)

  final_dets: List[NoteDetection] = []
  for run in merged_runs:
    strongest = max(run, key=lambda d: d.detected_mag)
    final_dets.append(strongest)

  grouped_chords = []
  curr_group = [final_dets[0]]

  for d in final_dets[1:]:
    prev = curr_group[-1]
    if abs(d.frame_index - prev.frame_index) <= chord_frame_tol:
      curr_group.append(d)
    else:
      grouped_chords.append(curr_group)
      curr_group = [d]

  if curr_group:
    grouped_chords.append(curr_group)

  for g in grouped_chords:
    mean_frame = int(np.median([d.frame_index for d in g]))
    mean_frame = snap_to_onset(mean_frame, onsets, onset_snap_tol=onset_snap_tol)
    for d in g:
      d.frame_index = mean_frame

  filtered_dets: List[NoteDetection] = []
  for d in final_dets:
    conflicts = [other for other in filtered_dets if _cents_diff(d.detected_freq, other.detected_freq) < conflict_cents_tol]
    if not conflicts:
      filtered_dets.append(d)
    else:
      if d.detected_mag > max(c.detected_mag for c in conflicts):
        for c in conflicts:
          filtered_dets.remove(c)
        filtered_dets.append(d)

  final_dets = filtered_dets

  return final_dets

def filter_by_snr(freqs: np.ndarray, mags_db: np.ndarray, peak_freqs: np.ndarray, peak_mags_db: np.ndarray, snr_db_threshold: float, snr_noise_window_hz, snr_noise_percentile) -> Tuple[np.ndarray, np.ndarray]: 
  keep_freqs = [] 
  keep_mags = [] 
  df = freqs[1] - freqs[0] if len(freqs) > 1 else 1.0 
  half_window_bins = int(round(snr_noise_window_hz / df)) 

  for pf, pm in zip(peak_freqs, peak_mags_db): 
    idx = np.argmin(np.abs(freqs - pf)) 

    lo = max(0, idx - half_window_bins)
    hi = min(len(freqs), idx + half_window_bins + 1)
    neighborhood = np.delete(mags_db[lo:hi], idx - lo)
    
    if neighborhood.size == 0: continue 
    noise_floor = np.percentile(neighborhood, snr_noise_percentile) 
    snr_db = pm - noise_floor
    
    if snr_db >= snr_db_threshold: 
      keep_freqs.append(pf) 
      keep_mags.append(pm) 

  return np.array(keep_freqs), np.array(keep_mags)

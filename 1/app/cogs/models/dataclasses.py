from typing import Tuple
from dataclasses import dataclass

@dataclass
class NoteDetection:
  note_key: str
  frame_index: int
  detected_mag: float
  detected_freq: float
  
@dataclass
class PipelineConfig:
  frame_length_sec: float
  frame_hop_length_factor: float
  onset_flux_perc: int
  onset_flux_scale_factor: float
  onset_flux_smooth: int
  gauss_sigma_hz: float
  gauss_smoothing_factor: float
  peaks_freq_range_hz: Tuple[int, int]
  peaks_min_prominence_th: float
  peaks_min_distance_hz: float
  peaks_parabolic_denom_tol: float
  peaks_parabolic_delta_clip: float
  snr_threshold_db: float
  snr_noise_window_hz: float
  snr_noise_perc: float
  dets_octave_tol_cents: float
  mad_factor: float
  mad_min_th: float
  postproc_allowed_gap_fr: int
  postproc_min_consecutive_fr: int
  postproc_growing_trend_th_fr: int
  postproc_conflict_cents_tol_fr: float
  postproc_chord_tol_fr: float
  postproc_onset_snap_tol_fr: int

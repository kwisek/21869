from typing import Dict, Any

FREQ_RANGE_HZ = (200, 1500)
FRAME_LENGTH_SEC = 0.186

SEARCH_SPACE: Dict[str, Dict[str, Any]] = {
  'frame_length_sec': {'type': 'const', 'value': FRAME_LENGTH_SEC},
  'frame_hop_length_factor': {'type': 'float', 'bounds': [0.5, 0.8], 'scale': 'linear'},
  'onset_flux_perc': {'type': 'int', 'bounds': [70, 95], 'scale': 'linear'},
  'onset_flux_scale_factor': {'type': 'float', 'bounds': [0.25, 3.0], 'scale': 'linear'},
  'onset_flux_smooth': {'type': 'int', 'bounds': [1, 8], 'scale': 'linear'},
  'peaks_freq_range_hz': {'type': 'const', 'value': FREQ_RANGE_HZ},
  'peaks_min_prominence_th': {'type': 'float', 'bounds': [-100, 0], 'scale': 'linear'},
  'peaks_min_distance_hz': {'type': 'float', 'bounds': [4.0, 50.0], 'scale': 'linear'},
  'peaks_parabolic_denom_tol': {'type': 'float', 'bounds': [1e-6, 1e-1], 'scale': 'log'},
  'peaks_parabolic_delta_clip': {'type': 'float', 'bounds': [0.0, 1.0], 'scale': 'linear'},
  'snr_threshold_db': {'type': 'float', 'bounds': [0.0, 20.0], 'scale': 'linear'},
  'snr_noise_window_hz': {'type': 'float', 'bounds': [0.0, 200.0], 'scale': 'linear'},
  'snr_noise_perc': {'type': 'float', 'bounds': [0.0, 75.0], 'scale': 'linear'},
  'dets_octave_tol_cents': {'type': 'int', 'bounds': [0, 100], 'scale': 'linear'},
  'mad_factor': {'type': 'float', 'bounds': [0.0, 10.0], 'scale': 'linear'},
  'mad_min_th': {'type': 'float', 'bounds': [-100, 0], 'scale': 'linear'},
  'postproc_allowed_gap_fr': {'type': 'int', 'bounds': [0, 10], 'scale': 'linear'},
  'postproc_min_consecutive_fr': {'type': 'int', 'bounds': [0, 10], 'scale': 'linear'},
  'postproc_growing_trend_th_fr': {'type': 'int', 'bounds': [0, 5], 'scale': 'linear'},
  'postproc_conflict_cents_tol_fr': {'type': 'float', 'bounds': [0.0, 100.0], 'scale': 'linear'},
  'postproc_chord_tol_fr': {'type': 'int', 'bounds': [0, 2], 'scale': 'linear'},
  'postproc_onset_snap_tol_fr': {'type': 'int', 'bounds': [1, 5], 'scale': 'linear'}
}

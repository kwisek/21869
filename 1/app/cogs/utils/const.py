from app.cogs.models import PipelineConfig

# pipeline constants
FRAME_LENGTH_SEC: float = 0.186
FREQ_RANGE_HZ = (250.0, 1400.0)
EPS = 1e-12

# base config
DEFAULT_CONFIG = PipelineConfig(
  frame_length_sec = FRAME_LENGTH_SEC,
  frame_hop_length_factor = 0.592402107229099,
  onset_flux_perc = 70,
  onset_flux_scale_factor = 0.25,
  onset_flux_smooth = 1,
  peaks_freq_range_hz = FREQ_RANGE_HZ,
  peaks_min_prominence_th = -42.757162831353355,
  peaks_min_distance_hz = 4.0,
  peaks_parabolic_denom_tol = 0.005783229806408026,
  peaks_parabolic_delta_clip = 0.5143849665051664,
  snr_threshold_db = 19.208951944838326,
  snr_noise_window_hz = 60.33439223402952,
  snr_noise_perc = 64.94926109393921,
  dets_octave_tol_cents = 46,
  mad_factor = 0.0,
  mad_min_th = -99.34504425647737,
  postproc_allowed_gap_fr = 1,
  postproc_min_consecutive_fr = 1,
  postproc_growing_trend_th_fr = 0,
  postproc_conflict_cents_tol_fr = 0.0,
  postproc_chord_tol_fr = 2,
  postproc_onset_snap_tol_fr=5
)

KALIMBA_NOTES_17 = {
  'C4': 261.63, 'D4': 293.66, 'E4': 329.63, 'F4': 349.23, 'G4': 392.00, 'A4': 440.00, 
  'B4': 493.88, 'C5': 523.25, 'D5': 587.33, 'E5': 659.25, 'F5': 698.46, 'G5': 783.99, 
  'A5': 880.00, 'B5': 987.77, 'C6': 1046.50, 'D6': 1174.66, 'E6': 1318.51
}

NOTATION_LETTERS = {
  'C4': 'C', 'D4': 'D', 'E4': 'E', 'F4': 'F', 'G4': 'G', 'A4': 'A', 'B4': 'B', 
  'C5': 'C°', 'D5': 'D°', 'E5': 'E°', 'F5': 'F°', 'G5': 'G°', 'A5': 'A°', 'B5': 'B°', 
  'C6': 'C°°', 'D6': 'D°°', 'E6': 'E°°'
}

NOTATION_NUMBERS = {
  'C4': '1', 'D4': '2', 'E4': '3', 'F4': '4', 'G4': '5', 'A4': '6', 'B4': '7', 
  'C5': '1°', 'D5': '2°', 'E5': '3°', 'F5': '4°', 'G5': '5°', 'A5': '6°', 'B5': '7°', 
  'C6': '1°°', 'D6': '2°°', 'E6': '3°°'
}
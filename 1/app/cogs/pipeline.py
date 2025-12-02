import logging
import numpy as np
from typing import List
from app.cogs.filehandling import read_bytes
from app.cogs.models import NoteDetection, PipelineConfig
from app.cogs.filehandling import normalize_input, prepare_frames
from app.cogs.transform import hanning_window, linear_spectrum, convert_peaks_to_detections, detect_peaks, map_to_db, construct_output_sequence, detect_onsets
from app.cogs.utils.const import *
from app.cogs.filter import filter_by_mad, postprocess, filter_by_snr
from app.cogs.models.sequence import Sequence

log = logging.getLogger(__name__)

def run_pipeline(bytes: bytes, config: PipelineConfig = DEFAULT_CONFIG) -> Sequence:
  
  # Step 1: load data and normalize input
  samples, sr = normalize_input(read_bytes(bytes))

  # Step 2: convert samples to frames
  frames = prepare_frames(samples, sr, frame_length=config.frame_length_sec, hop_length=config.frame_hop_length_factor)

  # Step 3: apply window
  frames, window = hanning_window(frames, sr, frame_length=config.frame_length_sec)

  # Step 4: pre-compute FFT for all frames
  all_freqs, all_mags = [], []

  for frame in frames:
    freqs, mags = linear_spectrum(frame, sr, window)
    all_freqs.append(freqs)
    all_mags.append(mags)

  all_freqs = np.array(all_freqs)
  all_mags = np.array(all_mags)
  ref_mag = max(EPS, float(np.max(all_mags)))

  # Step 5: detect onsets
  onsets = detect_onsets(all_mags, config.onset_flux_perc, config.onset_flux_scale_factor, config.onset_flux_smooth)

  # Step 6: analyze all frames to look for note detections
  detections: List[NoteDetection] = []
  
  for index, (freqs, mags) in enumerate(zip(all_freqs, all_mags)):
    log.debug(f"Processing frame: {index + 1}/{len(frames)}")
    
    # Step 6.1: map to dB
    mags = map_to_db(mags, ref_mag)

    # Step 6.2: detect peaks
    peak_freqs, peak_mags = detect_peaks(freqs, mags, freq_range_hz=config.peaks_freq_range_hz, min_prominence=config.peaks_min_prominence_th, min_distance_hz=config.peaks_min_distance_hz, parabolic_denom_tol=config.peaks_parabolic_denom_tol, parabolic_delta_clip=config.peaks_parabolic_delta_clip)
    log.debug(f"There are {len(peak_freqs)} initial peak freqs in this frame")

    # Step 6.3: filter by SNR
    peak_freqs, peak_mags = filter_by_snr(freqs, mags, peak_freqs, peak_mags, config.snr_threshold_db, config.snr_noise_window_hz, config.snr_noise_perc)
    log.debug(f"There are {len(peak_freqs)} peak freqs in this frame after SNR filtering")
    
    # Step 6.4: map peaks to detections
    local_detections = convert_peaks_to_detections(index, peak_freqs, peak_mags, octave_tol_cents=config.dets_octave_tol_cents)

    # Step 6.5: append results
    detections.extend(local_detections)
    
  log.debug(f"There are {len(detections)} total detections")
    
  # Step 7: filter by MAD
  detections = filter_by_mad(detections, mad_k=config.mad_factor, mad_min_th=config.mad_min_th)

  # Step 8: post-processing and additional filters
  detections = postprocess(detections, onsets, config.postproc_allowed_gap_fr, config.postproc_min_consecutive_fr, config.postproc_growing_trend_th_fr, config.postproc_conflict_cents_tol_fr, config.postproc_chord_tol_fr, config.postproc_onset_snap_tol_fr)

  # Step 9: constructing output DTO based sequence
  result = construct_output_sequence(detections)

  log.debug(f"Pipeline result is: {result}")
  return result
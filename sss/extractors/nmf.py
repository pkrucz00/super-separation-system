import os
import warnings
from pathlib import Path

import soundfile as sf
import librosa

import numpy as np

from sklearn.decomposition import NMF
from sklearn.exceptions import ConvergenceWarning

from sss.dataclasses import ExtractParams, AudioWave, ExtractionType


def perform_nmf(params: ExtractParams) -> AudioWave:
    RANK = 96
    warnings.filterwarnings(action="ignore", category=ConvergenceWarning)
    
    def load_train_matrix(instrument: str):
        base_dir = Path("train/wage_matrices")
        w_rel_path = f"{instrument}.npy"
        w_path = os.path.join(base_dir, w_rel_path)
        return np.load(w_path)
    
    def nmf(V, max_iter):
        model = NMF(n_components=RANK,
            solver="mu",
            max_iter=max_iter,
            beta_loss="kullback-leibler")
        W = model.fit_transform(V)
        H = model.components_
        return W, H
    
    def get_spectrogram_from_mono_wave(wave):
        return np.abs(librosa.stft(y=wave, n_fft=2048, hop_length=512))
    
    def get_mono_wave_from_spectrogram(spectrogram):
        return librosa.istft(stft_matrix=spectrogram, n_fft=2048, hop_length=512)
    
    
    def compute_one_channel(input_wave, W_train, max_iter):
        spectrogram = get_spectrogram_from_mono_wave(input_wave)
        _, H = nmf(spectrogram, max_iter)
        output_spectrogram = W_train @ H
        rest_spectrogram = spectrogram - output_spectrogram
        return get_mono_wave_from_spectrogram(output_spectrogram),\
               get_mono_wave_from_spectrogram(rest_spectrogram)
    
    def compute_result_wave(W_train, params: ExtractParams):
        input_wave, _ = sf.read(params.input_path)
                
        left_output_audio, left_rest_audio = \
            compute_one_channel(input_wave[:, 0], W_train, params.max_iter)
        right_output_audio, right_rest_audio = \
            compute_one_channel(input_wave[:, 1], W_train, params.max_iter)
            
        result_wave, _rest_wave = \
                np.vstack((left_output_audio, right_output_audio)).T,\
                np.vstack((left_rest_audio, right_rest_audio)).T
        return result_wave
    
    
    W_t = load_train_matrix(params.instrument)
    return compute_result_wave(W_t, params)
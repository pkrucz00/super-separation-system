import os
import warnings
from pathlib import Path

import soundfile as sf
import librosa

import numpy as np

from sklearn.decomposition import NMF
from sklearn.exceptions import ConvergenceWarning

from sss.dataclasses import ResultWaves, ExtractParams, AudioWave, MonoWave, Spectrogram, Instrument



def perform_nmf(params: ExtractParams) -> ResultWaves:
    RANK = 96    
    warnings.filterwarnings(action="ignore", category=ConvergenceWarning)
    
    def load_train_matrix(instrument: Instrument) -> Spectrogram:
        base_dir = Path("train/wage_matrices")
        w_rel_path = f"{instrument.value}.npy"
        w_path = os.path.join(base_dir, w_rel_path)
        return np.load(w_path)
    
    def compute_max_iter(params: ExtractParams):
        quality_to_max_iter = {"fast": 20, "normal": 200, "high": 1000}
        return params.max_iter if params.max_iter else quality_to_max_iter[params.quality]
    
    def nmf(V, max_iter):
        model = NMF(n_components=RANK,
            solver="mu",
            max_iter=max_iter,
            beta_loss="kullback-leibler")
        W = model.fit_transform(V)
        H = model.components_
        return W, H
    
    def left_channel(wave: AudioWave) -> MonoWave:
        return wave[:, 0]
    
    def right_channel(wave: AudioWave) -> MonoWave:
        return wave[:, 1]
    
    def combine_monowaves(left: MonoWave, right: MonoWave) -> AudioWave:
        return np.vstack([left, right]).T 
    
    def get_spectrogram_from_mono_wave(wave: MonoWave) -> Spectrogram:
        return np.abs(librosa.stft(y=wave, n_fft=2048, hop_length=256))
    
    def get_mono_wave_from_spectrogram(spectrogram: Spectrogram) -> MonoWave:
        return librosa.istft(stft_matrix=spectrogram, n_fft=2048, hop_length=512)     
    
    def compute_one_channel(input_wave, W_train, max_iter):
        spectrogram = get_spectrogram_from_mono_wave(input_wave)
        _, H = nmf(spectrogram, max_iter)
        output_spectrogram = W_train @ H
        return get_mono_wave_from_spectrogram(output_spectrogram)
    
    def compute_result_wave(input_wave: AudioWave, W_train: np.ndarray, max_iter: int) -> AudioWave:
        left_output_audio = \
            compute_one_channel(left_channel(input_wave), W_train, max_iter)
        right_output_audio = \
            compute_one_channel(right_channel(input_wave), W_train, max_iter)
            
        return combine_monowaves(left_output_audio, right_output_audio)
    
    
    def compute_reversed_monowave(wave: MonoWave, separated_instrument_waves: list[MonoWave]) -> MonoWave:
        input_spectrogram = get_spectrogram_from_mono_wave(wave)
        instrument_spectrograms = np.array([get_spectrogram_from_mono_wave(wave) for wave in separated_instrument_waves])
        cum_instr_spectrogram = np.sum(instrument_spectrograms, axis=0)
        reversed_spectrogram = np.abs(input_spectrogram - cum_instr_spectrogram)
        
        return get_mono_wave_from_spectrogram(reversed_spectrogram)
    
    def compute_reversed_wave(input_wave: AudioWave, separated_instrument_waves: list[AudioWave]) -> AudioWave:
        left_waves, right_waves = [left_channel(wave) for wave in separated_instrument_waves], [right_channel(wave) for wave in separated_instrument_waves]
        left = compute_reversed_monowave(left_channel(input_wave), left_waves)        
        right = compute_reversed_monowave(right_channel(input_wave), right_waves)
        
        return combine_monowaves(left, right)
    
    
    input_wave, _ = sf.read(params.input_path)
    wage_matrices = [load_train_matrix(instr) for instr in params.instruments]
    
    max_iter = compute_max_iter(params)
    separated_instrument_waves = [compute_result_wave(input_wave, W_t, max_iter) for W_t in wage_matrices]
    if params.reverse:
        reversed_wave = compute_reversed_wave(input_wave, separated_instrument_waves)
        params.instruments.append(Instrument.other)
        separated_instrument_waves.append(reversed_wave)
    return list(zip(params.instruments, separated_instrument_waves))
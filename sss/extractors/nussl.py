import nussl
import numpy as np

from sss.dataclasses import ExtractParams, ResultWaves, Instrument, AudioWave
from pathlib import Path
import pickle

from functools import reduce


def perform_nussl(extract_params: ExtractParams) -> ResultWaves:
    def load_model(instrument: Instrument):
        folder = Path("train/nmf_models")
        model_path = folder / f"{instrument.value}.pk1"
        with open(model_path, 'rb') as file:
            NMF, _, _ = pickle.load(file)
            return NMF
    
    def compute_audio_wave(W, H) -> AudioWave:
        reconstructed_spectrogram = nussl.separation.NMFMixin.inverse_transform(W, H)
        return nussl.AudioSignal(stft=reconstructed_spectrogram).istft().T
    
    def results_to_signals(results: ResultWaves, duration: float) -> list[nussl.AudioSignal]:
        return [nussl.AudioSignal(audio_data_array=wave).truncate_seconds(duration).peak_normalize() for _instr, wave in results]
        
    def compute_reversed_wave(original: nussl.AudioSignal, result_signals: list[nussl.AudioSignal]) -> AudioWave:
        original.peak_normalize()
        subtraction = reduce(lambda as1, as2: as1 - as2, result_signals, original)
        return subtraction.audio_data.T
    
    sig = nussl.AudioSignal(extract_params.input_path)
    models = [load_model(instr) for instr in extract_params.instruments]
    matrices = [nussl.separation.NMFMixin.transform(sig, model) for model in models]
    results = [ (instr, compute_audio_wave(W, H)) for instr, (W, H) in zip(extract_params.instruments, matrices)]
    if extract_params.reverse:
        results.append((Instrument("other"), compute_reversed_wave(sig, results_to_signals(results, sig.signal_duration))))
    return results
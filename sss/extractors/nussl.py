import nussl
import numpy as np
import librosa

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
        compute_one_channel = lambda n: librosa.istft(W.T @ H[:, :, n], n_fft=2048, hop_length=1024)  #TODO debug weird sound artifacts and double length
        result_array = np.array([compute_one_channel(0), compute_one_channel(1)], dtype=np.float64)
        return nussl.AudioSignal(audio_data_array=result_array).peak_normalize().apply_gain(2).audio_data.T
    
    def results_to_signals(results: ResultWaves, duration: float) -> list[nussl.AudioSignal]:
        return [nussl.AudioSignal(audio_data_array=wave).truncate_seconds(duration).peak_normalize() for _instr, wave in results]
        
    def compute_reversed_wave(original: nussl.AudioSignal, result_signals: list[nussl.AudioSignal]) -> AudioWave:
        original.peak_normalize()
        subtraction = reduce(lambda as1, as2: as1 - as2, result_signals, original)
        return subtraction.audio_data.T   #TODO add reversal
    
    sig = nussl.AudioSignal(extract_params.input_path)
    models = [load_model(instr) for instr in extract_params.instruments]
    matrices = [nussl.separation.NMFMixin.transform(sig, model) for model in models]
    results = [ (instr, compute_audio_wave(W, H)) for instr, (W, H) in zip(extract_params.instruments, matrices)]
    if extract_params.reverse:
        results.append((Instrument("other"), compute_reversed_wave(sig, results_to_signals(results, sig.signal_duration))))
    return results

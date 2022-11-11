import nussl
import numpy as np
import librosa

from sss.dataclasses import ExtractParams, ResultWaves, Instrument
from pathlib import Path
import pickle


def perform_nussl(extract_params: ExtractParams) -> ResultWaves:
    def load_model(instrument: Instrument):
        folder = Path("train/nmf_models")
        model_path = folder / f"{instrument.value}.pk1"
        with open(model_path, 'rb') as file:
            NMF, _, _ = pickle.load(file)
            return NMF
    
    def compute_audio_wave(W, H):
        compute_one_channel = lambda n: librosa.istft(W.T @ H[:, :, n], n_fft=2048, hop_length=1024)  #TODO debug weird sound artifacts and double length
        return np.array([1000*compute_one_channel(0), 1000*compute_one_channel(1)], dtype=np.float64).T
    
    def compute_reversed_wave(original: nussl.AudioSignal, result_waves):
        return np.array([[],[]])   #TODO add reversal
    
    sig = nussl.AudioSignal(extract_params.input_path)
    models = [load_model(instr) for instr in extract_params.instruments]
    matrices = [nussl.separation.NMFMixin.transform(sig, model) for model in models]
    results = [ (instr, compute_audio_wave(W, H)) for instr, (W, H) in zip(extract_params.instruments, matrices)]
    # if extract_params.reverse:
    #     results.append({Instrument("other"): compute_reversed_wave()})
    return results
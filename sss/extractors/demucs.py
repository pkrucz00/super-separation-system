from sss.dataclasses import ExtractParams, AudioWave
import numpy as np

def perform_demucs(params: ExtractParams) -> AudioWave:
    print(f"Beep bop, demucs demucs {params.input_path} demucs demucs demucs, beep bop boop")
    return np.array([[2, 1], [3, 7]])
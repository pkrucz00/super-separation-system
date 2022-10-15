import json

from sss.persistance import save_results, move_demucs

from sss.extractors.nmf import perform_nmf
from sss.extractors.demucs import perform_demucs

from sss.dataclasses import ExtractParams, SaveParams, EvalParams, AudioWave, Path


def perform_extraction(method: str, params: ExtractParams) -> AudioWave:
    methods = {"nmf": perform_nmf, "demucs": perform_demucs}
    return methods[method](params)
    
    
def evaluate_results(result_wave: AudioWave, eval_params: EvalParams):  #TODO add result type hint
    print("Evaluating: beep bop boop")
    

def save(result_wave, method, save_params: SaveParams) -> Path:
    if method == "demucs":
        move_demucs(save_params)
    else:
        save_results(result_wave, save_params)
 
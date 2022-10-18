import json

from sss.extractors.nmf import perform_nmf
from sss.extractors.demucs import perform_demucs

from sss.persistance import save_results, move_demucs, save_evaluation
from sss.evaluation import evaluate_results

from sss.dataclasses import ExtractParams, SaveWavParams, EvalParams, SaveEvalParams, AudioWave, Pathname


def extract(method: str, params: ExtractParams) -> AudioWave:
    methods = {"nmf": perform_nmf, "demucs": perform_demucs}
    return methods[method](params)
    

def save(result_wave: AudioWave, method: str, save_params: SaveWavParams) -> Pathname:
    if method == "demucs":
        move_demucs(save_params)
    else:
        save_results(result_wave, save_params)
 
 
def evaluate(result_wave: AudioWave,
             eval_params: EvalParams):
    return evaluate_results(result_wave, eval_params)


def save_eval(eval_results, save_eval_params: SaveEvalParams):
    return save_evaluation(eval_results, save_eval_params)
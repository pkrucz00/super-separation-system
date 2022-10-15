import json

from sss.extractors.nmf import perform_nmf
from sss.extractors.demucs import perform_demucs

from sss.persistance import save_results, move_demucs, save_evaluation
from sss.evaluation import evaluate_results

from sss.dataclasses import ExtractParams, SaveWavParams, EvalParams, SaveEvalParams, AudioWave, Pathname


def extract(method: str, params: ExtractParams) -> AudioWave:
    methods = {"nmf": perform_nmf, "demucs": perform_demucs}
    return methods[method](params)
    
    
def evaluate(result_wave: AudioWave,
             eval_params: EvalParams,
             save_eval_params: SaveEvalParams = None):  #TODO add result type hint
    eval_results = evaluate_results(result_wave, eval_params)
    if save_eval_params:
        save_evaluation(eval_results, save_eval_params)
    

def save(result_wave: AudioWave, method: str, save_params: SaveWavParams) -> Pathname:
    if method == "demucs":
        move_demucs(save_params)
    else:
        save_results(result_wave, save_params)
 
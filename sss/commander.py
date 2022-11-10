from sss.extractors.nmf import perform_nmf
from sss.extractors.demucs import perform_demucs

from sss.persistance import save_results, save_evaluation
from sss.evaluation import evaluate_results

from sss.dataclasses import ResultWaves, ExtractParams, SaveWavParams, EvalParams, SaveEvalParams, AudioWave, Pathname, Instrument


def extract(method: str, params: ExtractParams) -> ResultWaves:
    methods = {"nmf": perform_nmf, "demucs": perform_demucs}
    return methods[method](params)
    

def save(result_wave: AudioWave, instrument: Instrument, save_params: SaveWavParams) -> Pathname:
    return save_results(result_wave, instrument, save_params)
 
 
def evaluate(result_wave: AudioWave,
             eval_params: EvalParams):
    return evaluate_results(result_wave, eval_params)


def save_eval(eval_results, save_eval_params: SaveEvalParams):
    return save_evaluation(eval_results, save_eval_params)
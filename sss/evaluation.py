import museval
import soundfile as sf

from sss.dataclasses import EvalParams, AudioWave


def evaluate_results(result_wave: AudioWave, eval_params: EvalParams) -> tuple:
    def evaluate_single(reference):
        results = museval.evaluate([reference], [result_wave])
        return tuple([res.flatten() for res in results])
    
    print(f"Starting result evaluation...")
    reference, _ = sf.read(eval_params.ref_path)
    return evaluate_single(reference)
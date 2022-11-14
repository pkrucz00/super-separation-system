import museval
import soundfile as sf

from sss.dataclasses import EvalParams, AudioWave


def evaluate_results(result_wave: AudioWave, eval_params: EvalParams) -> dict:  # todo: correct type
    def evaluate_single(output_wave, reference):
        results = museval.evaluate([reference], [output_wave])
        return tuple([res.flatten() for res in results])
    
    # (f"Starting result evaluation...")  # todo: delete or print
    reference, _ = sf.read(eval_params.ref_path)
    return evaluate_single(result_wave, reference)

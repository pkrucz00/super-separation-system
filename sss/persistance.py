import os
import json
from pathlib import Path

import numpy as np
import soundfile as sf


from sss.dataclasses import SaveWavParams, SaveEvalParams, AudioWave, Pathname, Instrument


def save_results(result_wave: AudioWave, instrument: Instrument, save_params: SaveWavParams) -> Pathname:
    def save_to_wmv(output_audio, path, sr):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        sf.write(path + '.wav', np.array(output_audio), sr, "PCM_24")
        print(f"File saved to {path}.wav")
        return path
    
    output_path = os.path.join(save_params.output_path, f"{save_params.input_track}-{instrument.value}")
    saved_path = save_to_wmv(result_wave, output_path, save_params.sample_rate)

    return saved_path
       

def save_evaluation(eval_results, save_params: SaveEvalParams) -> Pathname:
    def get_unit_score(sdr, sir, sar, isr, second):
        metrics = {"SDR": sdr, "SIR": sir, "SAR": sar, "ISR": isr}
        return {"time": second, "metrics": metrics}    

    def save_dict_as_json(eval_dict, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="UTF-8") as file:
            file.write(json.dumps(eval_dict, indent=4))
            print(f"Evaluation scores saved to {path}")
            return path
    
    sdrs, sirs, sars, idrs = eval_results
    targets = [get_unit_score(sdr, sir, sar, idr, second)
            for second, (sdr, sir, sar, idr)
            in enumerate(zip(sdrs, sirs, sars, idrs))]
    eval_dict = {"targets": targets}
    return save_dict_as_json(eval_dict, save_params.output_path)

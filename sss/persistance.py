import os
import json
from pathlib import Path

import numpy as np
import soundfile as sf


from sss.dataclasses import SaveWavParams, AudioWave, Pathname


def save_results(result_wave: AudioWave, save_params: SaveWavParams) -> Pathname:
    def save_to_wmv(output_audio, path, sr):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        sf.write(path + '.wav', np.array(output_audio), sr, "PCM_24")
        print(f"File saved to {path}")
        return path
    
    output_file = f'{save_params.output_path}-{save_params.extraction_type.value}'
    saved_path = save_to_wmv(result_wave, output_file, save_params.sample_rate)

    # TODO implement with multiple items
    # if reverse:
    #     output_file += '-reversed'
    #     self.save_to_wmv(self.output_reversed_audio, output_file, self.sr)
    
    return saved_path

    
    
def move_demucs(out_path: Pathname) -> Pathname:
    print(f"Moving and renaming files from demucs default folder to {out_path}")
   

def save_evaluation(eval_results, save_params: SaveWavParams) -> Pathname:
    def get_unit_score(sdr, sir, sar, isr, second):
        metrics = {"SDR": sdr, "SIR": sir, "SAR": sar, "ISR": isr}
        return {"time": second, "metrics": metrics}    

    def save_dict_as_json(eval_dict, path):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="UTF-8") as file:
            file.write(json.dumps(eval_dict, indent=4))
            print(f"Evaluation scores saved to {path}")
            return path
    
    print(eval_results)
    sdrs, sirs, sars, idrs = eval_results
    targets = [get_unit_score(sdr, sir, sar, idr, second)
            for second, (sdr, sir, sar, idr)
            in enumerate(zip(sdrs, sirs, sars, idrs))]
    eval_dict = {"targets": targets}
    return save_dict_as_json(eval_dict, save_params.output_path)
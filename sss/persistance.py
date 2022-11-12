import os
import json
from pathlib import Path

import numpy as np
import soundfile as sf


from sss.dataclasses import SaveWavParams, AudioWave, Pathname, SaveEvalParams


def save_results(result_wave: AudioWave, save_params: SaveWavParams) -> Pathname:
    def save_to_wmv(output_audio, path, sr):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        sf.write(path + '.wav', np.array(output_audio), sr, "PCM_24")
        print(f"File saved to {path}")
        return path

    output_file = f'{save_params.output_path}/{save_params.input_track}-{save_params.instrument}'
    saved_path = save_to_wmv(result_wave, output_file, save_params.sample_rate)

    # TODO implement with multiple items
    # if reverse:
    #     output_file += '-reversed'
    #     self.save_to_wmv(self.output_reversed_audio, output_file, self.sr)
    
    return saved_path


def move_demucs(save_params: SaveWavParams) -> Pathname:
    curr_folder = os.path.join("separated", "mdx_extra_q", save_params.input_track)
    file_to_move = f"{save_params.instrument}.wav"
    
    sep_track_filenames = os.listdir(curr_folder)
    if file_to_move not in sep_track_filenames:
        raise f"File {file_to_move} cannot be found in directory {curr_folder}"
    
    curr_path = os.path.join(curr_folder, file_to_move)
    dest_path = os.path.join(save_params.output_path,
                             f"{save_params.input_track}-{save_params.instrument}.wav")

    Path(dest_path).parent.mkdir(parents=True, exist_ok=True)
    if os.path.exists(dest_path):
        os.remove(dest_path)
    os.rename(curr_path, dest_path)
    
    return dest_path
       

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
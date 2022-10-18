import os
from pathlib import Path

import numpy as np
import soundfile as sf

from sss.dataclasses import ExtractParams, AudioWave

TEMPORARY_OUTPUT_FOLDER = "mdx_extra_q"

def perform_demucs(params: ExtractParams) -> AudioWave:
    demucs_exec_res = os.system(f"demucs {params.input_path}")
    if demucs_exec_res != 0:
        raise f"Demucs did not exec succesfully. Error {demucs_exec_res}"
    
    print(f"Beep bop, demucs demucs {params.input_path} demucs demucs demucs, beep bop boop")
    
    input_filename = Path(params.input_path).stem
    result_path = os.path.join("separated", "mdx_extra_q", input_filename, f"{params.instrument.value}.wav")
    result_wave, _ = sf.read(result_path)
    return result_wave
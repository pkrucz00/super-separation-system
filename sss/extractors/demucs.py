from __future__ import annotations

import os
from pathlib import Path

import numpy as np
import soundfile as sf

from sss.dataclasses import ExtractParams, AudioWave, Pathname, ExtractionType

class DemucsCommandBuilder:
    def __init__(self):
        self.command_parts = ["demucs"]
    
    def add_command_part(self, command_part: str) -> type[DemucsCommandBuilder]:
        self.command_parts.append(command_part)
        return self
        
    def construct_command(self):
        return " ". join(self.command_parts)

    def add_input_part(self, input_path: str):
        return self.add_command_part(input_path)
    
    def add_instrument_part(self, instrument: str):
        cmd_part = f"--two-stems {instrument}" if instrument else ""
        return self.add_command_part(cmd_part)

    def __str__(self):
        return f"Demucs builder with command: {self.construct_command()}"


def perform_demucs(params: ExtractParams) -> AudioWave:
    def build_from_extract_params(params: ExtractParams) -> str:
        return DemucsCommandBuilder()\
            .add_instrument_part(params.instrument)\
            .add_input_part(params.input_path)\
            .construct_command()


    def run_demucs(command: str):
        demucs_exec_res = os.system(command)
        if demucs_exec_res != 0:
            raise f"Demucs did not exec successfully. Error {demucs_exec_res}"
        
    # In future - change this to a default demucs folder
    def find_output_path(params: ExtractParams) -> Pathname:
        def potential_directory():
            input_filename = Path(params.input_path).stem
            return os.path.join("separated", "mdx_extra_q", input_filename, f"{params.instrument}.wav")
    
        return potential_directory() if os.path.exists(potential_directory()) else None
    
    command = build_from_extract_params(params)
    run_demucs(command)
    
    result_path = find_output_path(params)
    result_wave, _ = sf.read(result_path)
    return result_wave
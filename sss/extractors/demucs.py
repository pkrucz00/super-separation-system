from __future__ import annotations

import os
import shutil
from pathlib import Path

import numpy as np
import soundfile as sf

from sss.dataclasses import ExtractParams, ResultWaves, Pathname, Instrument

class DemucsCommandBuilder:
    def __init__(self):
        self.command_parts = ["demucs"]
    
    def add_command_part(self, command_part: str) -> DemucsCommandBuilder:
        self.command_parts.append(command_part)
        return self
        
    def construct_command(self):
        return " ". join(self.command_parts)

    def add_input_part(self, input_path: str):
        return self.add_command_part(f'"{input_path}"')
    
    def add_instrument_part(self, instruments: list[Instrument]):
        cmd_part = f"--two-stems {instruments[0].value}" if len(instruments) == 1 else ""
        return self.add_command_part(cmd_part)
    
    def add_output_part(self, output_path: str):
        return self.add_command_part(f"-o {output_path}")

    def __str__(self):
        return f"Demucs builder with command: {self.construct_command()}"


def perform_demucs(params: ExtractParams) -> ResultWaves:
    def build_from_extract_params(params: ExtractParams) -> str:
        return DemucsCommandBuilder()\
            .add_instrument_part(params.instruments)\
            .add_input_part(params.input_path)\
            .construct_command()


    def run_demucs(command: str):
        demucs_exec_res = os.system(command)
        if demucs_exec_res != 0:
            raise Exception(f"Demucs did not exec successfully. Error {demucs_exec_res}")
        
        
    def potential_directory():
        input_filename = Path(params.input_path).stem
        return os.path.join("separated", "mdx_extra_q", input_filename)
    
    # In future - change this to a default demucs folder
    def find_output_files(params: ExtractParams) -> dict:
        directory = potential_directory()
        if not os.path.exists(directory):
            raise Exception("Can't find demucs extraction folder")
             
        return {instrument: os.path.join(directory, f"{instrument.value}.wav")
                for instrument in params.instruments}    
    
    command = build_from_extract_params(params)
    run_demucs(command)
    
    result_paths = find_output_files(params)
    result_waves = [(instr, sf.read(result_path)[0]) for instr, result_path in result_paths.items()]
    shutil.rmtree(potential_directory())
    
    return result_waves
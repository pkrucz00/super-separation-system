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
        
    def construct_command(self) -> str:
        return " ". join(self.command_parts)

    def add_input_part(self, input_path: str) -> DemucsCommandBuilder:
        return self.add_command_part(f'"{input_path}"')
    
    def add_instrument_part(self, instruments: list[Instrument]) -> DemucsCommandBuilder:
        cmd_part = f"--two-stems {instruments[0].value}" \
            if DemucsCommandBuilder.should_be_two_stems(instruments) \
            else ""
        return self.add_command_part(cmd_part)
    
    def add_quality_part(self, quality: str) -> DemucsCommandBuilder:
        quality_to_shifts = {"fast": 1, "normal": 10, "high": 20}
        cmd_part = f"--shifts {quality_to_shifts[quality]}"
        return self.add_command_part(cmd_part)

    @staticmethod
    def should_be_two_stems(instruments) -> bool:
        return len(instruments) < 2

    def __str__(self):
        return f"Demucs builder with command: {self.construct_command()}"


def perform_demucs(params: ExtractParams) -> ResultWaves:
    def build_from_extract_params(params: ExtractParams) -> str:
        return DemucsCommandBuilder()\
            .add_instrument_part(params.instruments)\
            .add_quality_part(params.quality)\
            .add_input_part(params.input_path)\
            .construct_command()


    def run_demucs(command: str):
        demucs_exec_res = os.system(command)
        if demucs_exec_res != 0:
            raise Exception(f"Demucs did not exec successfully. Error {demucs_exec_res}")


    def potential_directory():
        input_filename = Path(params.input_path).stem
        return os.path.join("separated", "mdx_extra_q", input_filename)

    
    def find_output_files(params: ExtractParams) -> dict:
        def include_other(directory, paths):
            path_to_other = f"no_{params.instruments[0].value}.wav"\
                if DemucsCommandBuilder.should_be_two_stems(params.instruments)\
                    else "other.wav"
            reversed_path_dir = {Instrument("other"): os.path.join(directory, path_to_other)}
            return paths | reversed_path_dir

        get_paths_dict = lambda directory: \
            {instrument: os.path.join(directory, f"{instrument.value}.wav")
                for instrument in params.instruments}

        directory = potential_directory()
        if not os.path.exists(directory):
            raise Exception("Can't find demucs extraction folder")
        paths = get_paths_dict(directory)
        if params.reverse:
            paths = include_other(directory, paths)
        return paths
    
    command = build_from_extract_params(params)
    run_demucs(command)
    
    result_paths = find_output_files(params)
    result_waves = [(instr, sf.read(result_path)[0]) for instr, result_path in result_paths.items()]
    shutil.rmtree(potential_directory())

    return result_waves
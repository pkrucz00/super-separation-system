from dataclasses import dataclass
from enum import Enum

import numpy.typing as npt

AudioWave = npt.NDArray   #TODO choose type of ndarray
Pathname = str


#TODO - use this enum and create other enums where value should be one in a list
class ExtractionType(Enum):
    karaoke = "karaoke"
    bass = "bass"
    drums = "drums"
    vocals = "vocals"
    full = "full"


@dataclass
class ExtractParams:
    input_path: Pathname
    instrument: str = "vocals"
    reverse: bool = False
    quality: str = "fast"
    max_iter: int = 20
    
    @staticmethod
    def should_reverse(reverse, extraction_type):
        return reverse or extraction_type == "karaoke"
    
    @staticmethod
    def choose_instrument(extraction_type):
        return "vocals" if extraction_type == "karaoke" else extraction_type 
    
@dataclass
class SaveWavParams:
    sample_rate: int
    extraction_type: ExtractionType
    output_path: Pathname = "result"
    
@dataclass
class EvalParams:
    ref_path: Pathname
    
@dataclass
class SaveEvalParams:
    output_path: Pathname = "eval"
from dataclasses import dataclass
from enum import Enum

import numpy.typing as npt

AudioWave = npt.NDArray   #TODO choose type of ndarray
Path = str


#TODO - use this enum and create other enums where value should be one in a list
class ExtractionType(Enum):
    KARAOKE = "karaoke"
    BASS = "bass"
    DRUMS = "drums"
    VOCALS = "vocals"
    FULL = "full"


@dataclass
class ExtractParams:
    input_path: Path
    instrument: str = "vocals"  #TODO add validation
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
class SaveParams:
    output_path: str = "result"
    
@dataclass
class EvalParams:
    ref_path: Path
    output_path: Path = "eval"
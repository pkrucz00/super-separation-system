from dataclasses import dataclass
from enum import Enum

from typing import Any
import numpy as np
import numpy.typing as npt


AudioWave = npt.NDArray[np.float_]
MonoWave = npt.NDArray[np.float_]
Spectrogram = npt.NDArray[np.float_]
Pathname = str

class Instrument(Enum):
    vocals = "vocals"
    bass = "bass"
    drums = "drums"

#TODO - add enums: quality
class ExtractionType(Enum):
    karaoke = "karaoke"
    bass = "bass"
    drums = "drums"
    vocals = "vocals"
    full = "full"
    
    def to_instrument(self) -> list[Instrument]:
        stem_dict = {ExtractionType.full: ["vocals", "bass", "drums"],
            ExtractionType.karaoke: ["vocals"], ExtractionType.bass: ["bass"],
            ExtractionType.drums: ["drums"], ExtractionType.vocals: ["vocals"]}
        
        return [Instrument(instr_name) for instr_name in stem_dict[self]]
    
    def needed_eval_refs(self) -> int:
        return len(self.to_instrument())
    
    def needs_reversal(self) -> bool:
        return self is ExtractionType.karaoke or self is ExtractionType.full

@dataclass
class ExtractParams:
    input_path: Pathname
    instruments: list[Instrument]
    reverse: bool = False
    quality: str = "fast"
    max_iter: int = 20
    
    @staticmethod
    def should_reverse(reverse: bool, extraction_type: ExtractionType) -> bool:
        return reverse or extraction_type.needs_reversal()
        
@dataclass
class SaveWavParams:
    sample_rate: int
    instrument: str
    input_track: str
    output_path: Pathname = "result"
    
@dataclass
class EvalParams:
    ref_path: Pathname
    
@dataclass  #TODO define EvalResult
class SaveEvalParams:
    output_path: Pathname = "eval"
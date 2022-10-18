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
    
    def to_instrument(self) -> str:
        if self is ExtractionType.full:
            return ""
        
        stem_dict = {ExtractionType.karaoke: "vocals", ExtractionType.bass: "bass",
                        ExtractionType.drums: "drums", ExtractionType.vocals: "vocals"}
        return stem_dict[self]


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
    def choose_instrument(extraction_type: ExtractionType) -> str:
        if extraction_type == ExtractionType.full:
            return ""
        
        stem_dict = {ExtractionType.karaoke: "vocals", ExtractionType.BASS: "bass",
                ExtractionType.DRUMS: "drums", ExtractionType.VOCAL: "vocals"}
        return stem_dict[extraction_type]
        
@dataclass
class SaveWavParams:
    sample_rate: int
    extraction_type: ExtractionType
    output_path: Pathname = "result"
    
@dataclass
class EvalParams:
    ref_path: Pathname
    
@dataclass  #TODO define EvalResult
class SaveEvalParams:
    output_path: Pathname = "eval"
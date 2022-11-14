from sss.dataclasses import ExtractionType, AudioWave
from dataclasses import dataclass


@dataclass
class DataContainer:
    method: str = None
    extraction_type: ExtractionType = None
    input_track_name: str = None

    audio_wave: AudioWave = None
    sr: int = None

    evaluation_references = [None, None, None, None]  # todo: add type and figure out how to handle evaluation
    evaluation_results = None

from sss.dataclasses import ExtractionType, AudioWave
from dataclasses import dataclass


@dataclass
class DataContainer:
    audio_wave: AudioWave = None
    method: str = None
    extraction_type: ExtractionType = None
    sr: int = None
    evaluation_results = None
    input_track_name: str = None


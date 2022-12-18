from sss.dataclasses import ExtractionType, AudioWave
from dataclasses import dataclass


@dataclass
class DataContainer:
    method: str = None
    extraction_type: ExtractionType = None
    input_track_name: str = None

    audio_wave: AudioWave = None
    sr: int = None

    evaluation_references = {'vocals': None, 'drums': None, 'bass': None, 'other': None}
    evaluation_results = {'vocals': None, 'drums': None, 'bass': None, 'other': None}

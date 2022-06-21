import os
import json
import warnings
from pathlib import Path

from enum import Enum

import numpy as np
from numpy.random import rand

from sklearn.decomposition import NMF
from sklearn.exceptions import ConvergenceWarning

import librosa
import soundfile as sf

import museval
import click

from time import time

RANK = 96
warnings.filterwarnings(action="ignore", category=ConvergenceWarning)


class ExtractionType(Enum):
    KARAOKE = "karaoke"
    BASS = "bass"
    DRUMS = "drums"
    VOCAL = "vocal"
    FULL = "full"


class Separator:
    def __init__(self):
        self.evaluation_results = None
        self.output_reversed_audio = None
        self.sr = None
        self.output_audio = None

    @staticmethod
    def load_train_matrix(type: ExtractionType):
        if type not in (ExtractionType.BASS, ExtractionType.DRUMS, ExtractionType.VOCAL):
            raise AttributeError(f"{type.value} is not available now")
        base_dir = Path("train/wage_matrices")
        w_rel_path = f"{type.value}.npy"
        w_path = os.path.join(base_dir, w_rel_path)
        return np.load(w_path)

    @staticmethod
    def perform_NMF(V, max_iter, max_time):
        W, H = rand(V.shape[0], RANK), rand(RANK, V.shape[1])
        model = NMF(n_components=RANK,
                    init="custom",
                    solver="mu",
                    max_iter=1,
                    beta_loss="kullback-leibler")
        start_time = time()
        for _ in range(max_iter):
            if time() - start_time > max_time:
                print("Max time exceeded")
                break
            W = model.fit_transform(V, W=W, H=H)
            H = model.components_
        return W, H

    @staticmethod
    def get_spectrogram_from_mono_wave(wave):
        return np.abs(librosa.stft(y=wave, n_fft=2048, hop_length=512))

    @staticmethod
    def get_mono_wave_from_spectrogram(spectrogram):
        return librosa.istft(stft_matrix=spectrogram, n_fft=2048, hop_length=512)

    def compute_audio_for_one_channel(self, input_audio, W_train, max_iter, max_time):
        spectrogram = self.get_spectrogram_from_mono_wave(input_audio)
        _, H = self.perform_NMF(spectrogram, max_iter, max_time)
        output_spectrogram = W_train @ H
        rest_spectrogram = spectrogram - output_spectrogram
        return self.get_mono_wave_from_spectrogram(output_spectrogram),\
               self.get_mono_wave_from_spectrogram(rest_spectrogram)

    def compute_audio(self, input_audio, W_train, max_iter, max_time):
        left_output_audio, left_rest_audio = \
            self.compute_audio_for_one_channel(input_audio[:, 0], W_train, max_iter, max_time)
        right_output_audio, right_rest_audio = \
            self.compute_audio_for_one_channel(input_audio[:, 1], W_train, max_iter, max_time)
        return np.vstack((left_output_audio, right_output_audio)).T,\
                np.vstack((left_rest_audio, right_rest_audio)).T

    def compute_output_audio(self, input_audio_path, W_train, max_iter, max_time, should_reverse=False):
        input_audio, sr = self.load_wmv(input_audio_path)
        output_audio, rest_audio = self.compute_audio(input_audio, W_train, max_iter, max_time)

        self.sr = sr
        self.output_audio = output_audio

        if should_reverse:
            self.output_reversed_audio = rest_audio

    def evaluate(self, reference):
        results = museval.evaluate([reference], [self.output_audio])
        return tuple([res.flatten() for res in results])

    @staticmethod
    def get_unit_score(sdr, sir, sar, isr, second):
        metrics = {"SDR": sdr, "SIR": sir, "SAR": sar, "ISR": isr}
        return {"time": second, "metrics": metrics}

    def evaluate_results(self, reference_path):
        print("Starting result evaluation ...")
        reference, _ = self.load_wmv(reference_path)
        self.evaluation_results = self.evaluate(reference)

    @staticmethod
    def load_wmv(path):
        return sf.read(path)

    @staticmethod
    def save_to_wmv(output_audio, path, sr):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        sf.write(path + '.wav', np.array(output_audio), sr, "PCM_24")
        print(f"File saved to {path}")

    @staticmethod
    def save_dict_as_json(eval_dict, path):
        with open(path, "w", encoding="UTF-8") as file:
            file.write(json.dumps(eval_dict, indent=4))
            print(f"Evaluation scores saved to {path}")

    def save_evaluation(self, path):
        sdrs, sirs, sars, idrs = self.evaluation_results
        targets = [self.get_unit_score(sdr, sir, sar, idr, second)
                   for second, (sdr, sir, sar, idr)
                   in enumerate(zip(sdrs, sirs, sars, idrs))]
        eval_dict = {"targets": targets}
        self.save_dict_as_json(eval_dict, path)

    def sss(self, extraction_type, method, quality, reverse, reference, max_time, max_iter, input_file):
        W_t = self.load_train_matrix(extraction_type)
        self.compute_output_audio(input_file, W_t, should_reverse=reverse, max_iter=max_iter, max_time=max_time)

        if reference:
            self.evaluate_results(reference)

    def save_results(self, output_file, extraction_type, reverse):
        output_file += f'-{extraction_type.value}'

        self.save_to_wmv(self.output_audio, output_file, self.sr)

        if reverse:
            output_file += '-reversed'
            self.save_to_wmv(self.output_reversed_audio, output_file, self.sr)


@click.command()
@click.option('-t', '--extraction-type', default='VOCAL', help='type of the extraction',
              type=click.Choice(ExtractionType.__members__),
              callback=lambda c, p, v: getattr(ExtractionType, v) if v else None)
@click.option('-m', '--method', default='NMF', help='extraction method',
              type=click.Choice(['NMF'], case_sensitive=False))
@click.option('-q', '--quality', default='NORMAL', help='choose extraction quality',
              type=click.Choice(['FAST', 'NORMAL', 'HIGH'], case_sensitive=False))
@click.option('-e', '--evaluation-data', default=[None, None], nargs=2,
              type=click.Tuple([click.Path(), click.Path(exists=True)]), help='extraction evaluation')
@click.option('--reverse/--no-reverse', '-r/', default=False, help='reversed extraction')
@click.option('-T', '--max-time', default=1000, type=click.IntRange(1,), help='maximum extraction time')
@click.option('-I', '--max-iter', default=3, type=click.IntRange(1,), help='maximum iterations number')
@click.option('-o', '--output-file', default="results\\separated", type=click.Path(), help='output file location')
@click.argument('input-file', type=click.Path(exists=True))
def sss_command(extraction_type, method, quality, reverse, evaluation_data, max_time, max_iter, input_file, output_file):
    my_sep = Separator()
    my_sep.sss(extraction_type, method, quality, reverse, evaluation_data[1], max_time, max_iter, input_file)

    my_sep.save_results(output_file, extraction_type, reverse)
    if evaluation_data[0]:
        my_sep.save_evaluation(evaluation_data[0])


if __name__ == "__main__":
    sss_command()

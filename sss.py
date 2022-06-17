import os
import json
import warnings
from time import time
from pathlib import Path

from enum import Enum
from dataclasses import dataclass, field

import numpy as np
from numpy.random import rand

from sklearn.decomposition import NMF
from sklearn.exceptions import ConvergenceWarning

import librosa
import soundfile as sf

import museval
import click

RANK = 96
warnings.filterwarnings(action="ignore", category=ConvergenceWarning)


class ExtractionType(Enum):
    KARAOKE = "karaoke"
    BASS = "bass"
    DRUMS = "drums"
    VOCAL = "vocal"
    FULL = "full"


def prepare_output_path(input_path):
    filename = Path(input_path).stem
    return f"{filename}-{EXTRACTED_FEATURE}-out.wav"


def prepare_reverse_path(path):
    filename = Path(path).stem
    return f"{filename}-rev.wav"


def load_train_matrix(type: ExtractionType):
    if type not in (ExtractionType.BASS, ExtractionType.DRUMS, ExtractionType.VOCAL):
        raise AttributeError(f"{type.value} is not available now")
    base_dir = Path("train/wage_matrices")
    w_rel_path = f"{type.value}.npy"
    w_path = os.path.join(base_dir, w_rel_path)
    return np.load(w_path)


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


def get_spectrogram_from_mono_wave(wave):
    return np.abs(librosa.stft(y=wave, n_fft=2048, hop_length=512))


def get_mono_wave_from_spectrogram(spectrogram):
    return librosa.istft(stft_matrix=spectrogram, n_fft=2048, hop_length=512)


def compute_audio_for_one_channel(input_audio, W_train, max_iter, max_time):
    spectrogram = get_spectrogram_from_mono_wave(input_audio)
    _, H = perform_NMF(spectrogram, max_iter, max_time)
    output_spectrogram = W_train @ H
    rest_spectrogram = spectrogram - output_spectrogram
    return get_mono_wave_from_spectrogram(output_spectrogram),\
           get_mono_wave_from_spectrogram(rest_spectrogram)


def compute_output_audio(input_audio, W_train, max_iter, max_time):
    left_output_audio, left_rest_audio = \
        compute_audio_for_one_channel(input_audio[:, 0], W_train, max_iter, max_time)
    right_output_audio, right_rest_audio = \
        compute_audio_for_one_channel(input_audio[:, 1], W_train, max_iter, max_time)
    return np.vstack((left_output_audio, right_output_audio)).T,\
            np.vstack((left_rest_audio, right_rest_audio)).T


def get_unit_score(sdr, sir, sar, isr, second):
    metrics = {"SDR": sdr, "SIR": sir, "SAR": sar, "ISR": isr}
    return {"time": second, "metrics": metrics}


def save_dict_as_json(eval_dict, path):
    with open(path, "w", encoding="UTF-8") as file:
        file.write(json.dumps(eval_dict, indent=4))
        print(f"Evaluation scores saved to {path}")


def save_evaluation(sdrs, sirs, sars, idrs, path):
    targets = [get_unit_score(sdr, sir, sar, idr, second)
               for second, (sdr, sir, sar, idr)
               in enumerate(zip(sdrs, sirs, sars, idrs))]
    eval_dict = {"targets": targets}
    save_dict_as_json(eval_dict, path)


def evaluate(reference, estimate):
    results = museval.evaluate([reference], [estimate])
    return tuple([res.flatten() for res in results])


def evaluate_and_save(eval_data, estimate):
    print("Starting result evaluation ...")
    output_path, reference_path = eval_data
    reference, _ = load_wmv(reference_path)
    results = evaluate(reference, estimate)
    save_evaluation(*results, output_path)


def compute_and_save_output_audio(input_audio_path, W_train, output_path,
                                  max_iter, max_time, should_reverse=False):
    input_audio, sr = load_wmv(input_audio_path)
    output_audio, rest_audio = compute_output_audio(input_audio, W_train, max_iter, max_time)
    save_to_wmv(output_audio, output_path, sr)

    if should_reverse:
        output_path += '-reversed'
        save_to_wmv(rest_audio, prepare_reverse_path(output_path), sr)

    return output_audio


def load_wmv(path):
    return sf.read(path)


def save_to_wmv(output_audio, path, sr):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    sf.write(path + '.wav', np.array(output_audio), sr, "PCM_24")
    print(f"File saved to {path}")


@click.command()
@click.option('-t', '--type', default='VOCAL', help='type of the extraction',
              type=click.Choice(ExtractionType.__members__),
              callback=lambda c, p, v: getattr(ExtractionType, v) if v else None)
@click.option('-m', '--method', default='NMF', help='extraction method',
              type=click.Choice(['NMF'], case_sensitive=False))
@click.option('-q', '--quality', default='NORMAL', help='choose extraction quality',
              type=click.Choice(['FAST', 'NORMAL', 'HIGH'], case_sensitive=False))
@click.option('-e', '--evaluation-data', default=None, nargs=2,
              type=click.Tuple([click.Path(), click.Path(exists=True)]), help='extraction evaluation')
@click.option('--reverse/--no-reverse', '-r/', default=False, help='reversed extraction')
@click.option('-T', '--max-time', default=1000, type=click.IntRange(1,), help='maximum extraction time')
@click.option('-I', '--max-iter', default=1000000000, type=click.IntRange(1,), help='maximum iterations number')
@click.option('-o', '--output-file', default="results\\separated", type=click.Path(), help='output file location')
@click.argument('input-file', type=click.Path(exists=True))
def sss(type, method, quality, reverse, evaluation_data, max_time, max_iter, input_file, output_file):
    output_file += f'-{type.value}'

    W_t = load_train_matrix(type)
    output = compute_and_save_output_audio(
        input_file, W_t, output_file,
        should_reverse=reverse,
        max_iter=max_iter,
        max_time=max_time)
    if evaluation_data:
        evaluate_and_save(evaluation_data, output)


if __name__ == "__main__":
    sss()

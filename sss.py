import os
from time import time
from pathlib import Path
import click
from dataclasses import dataclass, field

import numpy as np
from sklearn.decomposition import NMF

import librosa
import soundfile as sf
import json

import museval

RANK = 96


def prepare_output_path(input_path):
    filename = Path(input_path).stem
    return f"{filename}-{EXTRACTED_FEATURE}-out.wav"


def prepare_reverse_path(path):
    filename = Path(path).stem
    return f"{filename}-rev.wav"


def load_train_matrix(path):
    return np.load(path)


def perform_NMF(V):
    model = NMF(n_components=RANK,
                init="random",
                solver="mu",
                max_iter=2,
                beta_loss="kullback-leibler",
                random_state=0)
    W = model.fit_transform(V)
    H = model.components_
    return W, H


def get_spectrogram_from_mono_wave(wave):
    return np.abs(librosa.stft(y=wave, n_fft=2048, hop_length=512))


def get_mono_wave_from_spectrogram(spectrogram):
    return librosa.istft(stft_matrix=spectrogram, n_fft=2048, hop_length=512)


def get_train_matrix(train_data):
    first_track = train_data[0]
    train_audio = librosa.to_mono(first_track.targets[EXTRACTED_FEATURE].audio.T)
    spectrogram = get_spectrogram_from_mono_wave(train_audio)
    W, _ = perform_NMF(spectrogram)
    return W


def compute_audio_for_one_channel(input_audio, W_train):
    spectrogram = get_spectrogram_from_mono_wave(input_audio)
    _, H = perform_NMF(spectrogram)
    output_spectrogram = W_train @ H
    rest_spectrogram = spectrogram - output_spectrogram
    return get_mono_wave_from_spectrogram(output_spectrogram),\
           get_mono_wave_from_spectrogram(rest_spectrogram)


def compute_output_audio(input_audio, W_train):
    left_output_audio, left_rest_audio = \
        compute_audio_for_one_channel(input_audio[:, 0], W_train)
    right_output_audio, right_rest_audio = \
        compute_audio_for_one_channel(input_audio[:, 1], W_train)
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
                                  should_reverse=False):
    input_audio, sr = load_wmv(input_audio_path)
    output_audio, rest_audio = compute_output_audio(input_audio, W_train)

    save_to_wmv(output_audio, output_path, sr)

    if should_reverse:
        output_path += '-reversed'
        save_to_wmv(rest_audio, prepare_reverse_path(output_path), sr)

    return output_audio


def load_wmv(path):
    return sf.read(path)


def save_to_wmv(output_audio, path, sr):
    sf.write(path + '.wav', np.array(output_audio), sr, "PCM_24")
    print(f"File saved to {path}")


@click.command()
@click.option('-t', '--type', default='VOCAL', help='type of the extraction',
              type=click.Choice(['KARAOKE', 'BASS', 'DRUMS', 'VOCAL', 'FULL'], case_sensitive=False))
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
    w_path = f"database\\train\\{EXTRACTED_FEATURE}.npy"
    output_file += f'-{type}'

    W_t = load_train_matrix(w_path)
    output = compute_and_save_output_audio(
        input_file, W_t, output_file,
        should_reverse=reverse)
    if evaluation_data:
        evaluate_and_save(evaluation_data, output)


if __name__ == "__main__":
    sss()

import os
from time import time
from pathlib import Path
import argparse
from dataclasses import dataclass, field

import numpy as np
from sklearn.decomposition import NMF

import librosa
import soundfile as sf
import museval


EXTRACTED_FEATURE = "bass"
RESULT_DIR = "results"

RANK = 96


def prepare_output_path(input_path):
    filename = Path(input_path).stem
    return f"{filename}-{EXTRACTED_FEATURE}-out.wav"


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--out", type=str, help="Path to the output file")
    parser.add_argument("input_path", type=str, help="Path to the input file")

    # być może trzeba to będzie rozdzielić na dwie funkcje gdy argumentów zrobi się dużo
    args = parser.parse_args()
    args.out = args.out if args.out else prepare_output_path(args.input_path)
    return args


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


# def get_evaluation(track, output_audio, rest_audio):
#     estimates = {EXTRACTED_FEATURE: output_audio,
#                  "accompaniment": rest_audio}
#     return museval.eval_mus_track(track, estimates, output_dir="./eval")


def test_and_compare_results(input_audio_path, W_train, output_path):
    input_audio, sr = load_wmv(input_audio_path)
    output_audio, rest_audio = compute_output_audio(input_audio, W_train)

        # print(get_evaluation(track, output_audio, rest_audio))
    save_to_wmv(output_audio, output_path, sr)
    # save_to_wmv(rest_audio, track)


def load_wmv(path):
    return sf.read(path)


def save_to_wmv(output_audio, path, sr):
    sf.write(path, np.array(output_audio), sr, "PCM_24")
    print(f"File saved to {path}")


if __name__ == "__main__":
    args = get_args()
    w_path = f"train/wage_matrices/{EXTRACTED_FEATURE}.npy"

    W_t = load_train_matrix(w_path)
    test_and_compare_results(args.input_path, W_t, args.out)

import os
from time import time
from pathlib import Path
import argparse
from dataclasses import dataclass, field

import numpy as np
from sklearn.decomposition import NMF

import librosa
import soundfile as sf
import json

import museval


EXTRACTED_FEATURE = "bass"
RESULT_DIR = "results"

RANK = 96


@dataclass
class EvaluationData:
    output_path: str
    reference_path: str


def prepare_output_path(input_path):
    filename = Path(input_path).stem
    return f"{filename}-{EXTRACTED_FEATURE}-out.wav"


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--out", type=str, help="Path to the output file")
    parser.add_argument("-e", "--evaluation", nargs=2, type=str,
                        help="Paths to reference and evaluation result output json")
    parser.add_argument("input_path", type=str, help="Path to the input file")

    # być może trzeba to będzie rozdzielić na dwie funkcje gdy argumentów zrobi się dużo
    args = parser.parse_args()
    args.out = args.out if args.out else prepare_output_path(args.input_path)
    args.evaluation = EvaluationData(reference_path=args.evaluation[0], output_path=args.evaluation[1])
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


def evaluate_and_save(eval_data: EvaluationData, estimate):
    print("Starting result evaluation ...")
    reference, _ = load_wmv(eval_data.reference_path)
    results = evaluate(reference, estimate)
    save_evaluation(*results, eval_data.output_path)


def compute_and_save_output_audio(input_audio_path, W_train, output_path,
                                  eval_ref_path=None, eval_out_path=None,
                                  should_reverse=False):  #TODO do odwracania
    input_audio, sr = load_wmv(input_audio_path)
    output_audio, rest_audio = compute_output_audio(input_audio, W_train)

    if eval_ref_path and eval_out_path:
        evaluate_and_save(eval_ref_path, output_audio, eval_out_path)

    save_to_wmv(output_audio, output_path, sr)

    return output_audio

# TODO use it in the next commit
    # if should_reverse:
    #     save_to_wmv(rest_audio, track, sr)


def load_wmv(path):
    return sf.read(path)


def save_to_wmv(output_audio, path, sr):
    sf.write(path, np.array(output_audio), sr, "PCM_24")
    print(f"File saved to {path}")


if __name__ == "__main__":
    args = get_args()
    w_path = f"train/wage_matrices/{EXTRACTED_FEATURE}.npy"

    W_t = load_train_matrix(w_path)
    output = compute_and_save_output_audio(args.input_path, W_t, args.out)
    if args.evaluation:
        evaluate_and_save(args.evaluation, output)

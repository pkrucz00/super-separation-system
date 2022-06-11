import os
from time import time
import numpy as np
from sklearn.decomposition import NMF

import librosa
import soundfile as sf

import musdb
import museval


EXTRACTED_FEATURE = "vocals"
RESULT_DIR = "results"

MEL_BINS = 96
RANK = 96


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


def get_evaluation(track, output_audio, rest_audio):
    estimates = {EXTRACTED_FEATURE: output_audio,
                 "accompaniment": rest_audio}
    return museval.eval_mus_track(track, estimates, output_dir="./eval")


def test_and_compare_results(test_data, W_train):
    for track in test_data[:2]:
        output_audio, rest_audio = compute_output_audio(track.audio, W_train)

        print(get_evaluation(track, output_audio, rest_audio))
        save_to_wmv(output_audio, track)
        save_to_wmv(rest_audio, track)


def save_to_wmv(output_audio, track):
    sf.write(os.path.join(RESULT_DIR, f"{track.name}-{EXTRACTED_FEATURE}-out.wav"),
             np.array(output_audio), 44100, "PCM_24")


if __name__=="__main__":
    mus_train = musdb.DB(root="database", is_wav=True, subsets="train")
    mus_test = musdb.DB(root="database", is_wav=True, subsets="test")
    print("Database loaded")

    W_t = get_train_matrix(mus_train)
    test_and_compare_results(mus_test, W_t)





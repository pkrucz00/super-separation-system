import os.path
import numpy as np
from sklearn.decomposition import NMF

import librosa
import musdb

RANK = 96


def perform_NMF(V):
    model = NMF(n_components=RANK,
                init="random",
                solver="mu",
                max_iter=10,
                beta_loss="kullback-leibler",
                random_state=0)
    W = model.fit_transform(V)
    H = model.components_
    return W, H


def get_spectrogram_from_mono_wave(wave):
    return np.abs(librosa.stft(y=wave, n_fft=2048, hop_length=512))


def get_mono_wave_from_spectrogram(spectrogram):
    return librosa.istft(stft_matrix=spectrogram, n_fft=2048, hop_length=512)


def get_train_matrix(track, feature):
    train_audio = librosa.to_mono(track.targets[feature].audio.T)
    spectrogram = get_spectrogram_from_mono_wave(train_audio)
    W, _ = perform_NMF(spectrogram)
    return W


def save_matrix(matrix, path):
    with open(path + ".npy", "wb") as file:
        np.save(file, matrix)


if __name__ == "__main__":
    mus_train = musdb.DB(root="database", is_wav=True, subsets="train")
    print("Database loaded")

    first_track = mus_train[0]  # TODO think about better ways of preparing data
    output_folder = "database\\train"
    for feature in ("vocals", "bass", "drums"):
        W = get_train_matrix(first_track, feature)
        print('Test', os.path.join(output_folder, feature))
        save_matrix(W, os.path.join(output_folder, feature))

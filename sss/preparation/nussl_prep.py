#!/usr/bin/env python
import nussl
import os
import glob
import pickle

from pathlib import Path

RANK = 96
test_folder = Path("database/test")

def save_model(model, label):
    default_folder = Path("train/nmf_models")
    input_path = default_folder / f"{label}.pk1"
    with open(input_path, "wb") as file:
        pickle.dump(model, file, pickle.HIGHEST_PROTOCOL)
        print(f"Model saved to {input_path}")


if __name__=="__main__":
    for extract_type in ["bass", "drums", "vocals"]:
        files_depth_2 = glob.glob("*/*", root_dir=test_folder)
        audio_signals = [nussl.AudioSignal(os.path.join(test_folder, audio_path)) 
                         for audio_path in files_depth_2 if extract_type in audio_path][:3]
        model = nussl.separation.NMFMixin.fit(audio_signals=audio_signals, n_components=RANK)
        save_model(model, extract_type)
        
        
        
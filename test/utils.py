import os
import numpy as np
import soundfile as sf

SR=44_100

def save_stub_audiowave(wave, pathname):
    sf.write(pathname, wave, SR)
    
def delete_stub_audiowave(pathname):
    os.remove(pathname)
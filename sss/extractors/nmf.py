from sss.dataclasses import ExtractParams, AudioWave

def perform_nmf(params: ExtractParams) -> AudioWave:
    print(f"Beep bop, performing NMF on {params.input_path}, beep bop boop")
    return [[2, 1], [3, 7]]
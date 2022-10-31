#!/usr/bin/env python

from pathlib import Path

from sss.dataclasses import ExtractParams, SaveWavParams, EvalParams, SaveEvalParams, ExtractionType
from sss.commander import extract, save, evaluate, save_eval

import librosa
import soundfile as sf

import click


def init_extract_params(input_file, extraction_type, reverse, quality, max_iter):
    return ExtractParams(
        input_path=input_file,
        instrument=extraction_type.to_instrument(),
        reverse=ExtractParams.should_reverse(reverse, extraction_type),
        quality=quality,
        max_iter=max_iter
    )


@click.command()
@click.option('-t', '--extraction-type', default='vocals', help='type of the extraction',
              type=click.Choice(ExtractionType.__members__),
              callback=lambda c, p, v: getattr(ExtractionType, v) if v else None)
@click.option('-m', '--method', default='nmf', help='extraction method',
              type=click.Choice(['nmf', 'demucs'], case_sensitive=False))
@click.option('-q', '--quality', default='normal', help='choose extraction quality',
              type=click.Choice(['fast', 'normal', 'high'], case_sensitive=False))
@click.option('-e', '--evaluation-data', default=None, nargs=2,
              type=click.Tuple([click.Path(exists=True), click.Path()]), help='extraction evaluation')
@click.option('--reverse/--no-reverse', '-r/', default=False, help='reversed extraction')
@click.option('-I', '--max-iter', default=3, type=click.IntRange(1,), help='maximum iterations number')
@click.option('-o', '--output-file', default="results\\separated", type=click.Path(), help='output file location')
@click.argument('input-file', type=click.Path(exists=True))
def sss_command(extraction_type, method, quality, reverse, evaluation_data, max_iter, input_file, output_file):
    extract_parameters = init_extract_params(input_file, extraction_type, reverse, quality, max_iter)
    _, sr = sf.read(input_file)
    save_parameters = SaveWavParams(output_path=output_file,
                                    sample_rate=sr,
                                    instrument=extraction_type.to_instrument(),
                                    input_track=Path(input_file).stem)
    
    result_wave = extract(method, extract_parameters)
    save(result_wave, method, save_parameters)

    if evaluation_data:
        eval_results = evaluate(result_wave,
                 eval_params=EvalParams(ref_path=evaluation_data[0]))
        save_eval(eval_results, save_eval_params=SaveEvalParams(output_path=evaluation_data[1]))
        
# ./sss.py -t drums -o "results" -e "database/test/Al James - Schoolboy Facination/drums.wav" "eval.json" "database/test/Al James - Schoolboy Facination/mixture.wav"
# ./sss.py -t drums -m "demucs" -o results "maanam-test.wav"
if __name__ == "__main__":
    sss_command()

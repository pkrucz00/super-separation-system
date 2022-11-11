#!/usr/bin/env python

from pathlib import Path

from sss.dataclasses import ExtractParams, SaveWavParams, EvalParams, SaveEvalParams, ExtractionType,  Pathname
from sss.commander import extract, save, evaluate, save_eval

import soundfile as sf

import click


def init_extract_params(input_file: Pathname, extraction_type: ExtractionType, reverse: bool, quality: str, max_iter: int):
    return ExtractParams(
        input_path=input_file,
        instruments=extraction_type.to_instrument(),
        reverse=ExtractParams.should_reverse(reverse, extraction_type),
        quality=quality,
        max_iter=max_iter
    )
    
    
def eval_args_valid_for_extract(extraction_type: ExtractionType, eval_data: tuple, reverse: bool) -> bool:
    expected_eval_data_length = extraction_type.needed_eval_refs() + int(reverse)
    return len(eval_data) == expected_eval_data_length
    

@click.command()
@click.option('-t', '--extraction-type', default='vocals', help='type of the extraction',
              type=click.Choice(ExtractionType.__members__),
              callback=lambda _c, _p, v: getattr(ExtractionType, v) if v else None)
@click.option('-m', '--method', default='nmf', help='extraction method',
              type=click.Choice(['nmf', 'demucs', 'nussl'], case_sensitive=False))
@click.option('-q', '--quality', default='normal', help='choose extraction quality',
              type=click.Choice(['fast', 'normal', 'high'], case_sensitive=False))
@click.option('-e', '--evaluation-data', default=None, nargs=2,
              type=click.Tuple([click.Path(exists=True), click.Path()]),
              multiple=True,
              help='extraction evaluation')
@click.option('--reverse/--no-reverse', '-r/', default=False, help='reversed extraction')
@click.option('-I', '--max-iter', default=None, type=click.IntRange(1,), help='maximum iterations number')
@click.option('-o', '--output-file', default="results\\separated", type=click.Path(), help='output file location')
@click.argument('input-file', type=click.Path(exists=True))
def sss_command(extraction_type, method, quality, reverse, evaluation_data, max_iter, input_file, output_file):
    extract_parameters = init_extract_params(input_file, extraction_type, reverse, quality, max_iter)
    _, sr = sf.read(input_file)
    save_parameters = SaveWavParams(output_path=output_file,
                                    sample_rate=sr,
                                    input_track=Path(input_file).stem)
    
    result_waves = extract(method,extract_parameters)
    for instrument, wave in result_waves:
        save(wave, instrument, save_parameters)

    if evaluation_data and eval_args_valid_for_extract(extraction_type, evaluation_data, reverse):
        for (_, wave), (eval_ref_path, eval_out_path) in zip(result_waves, evaluation_data):
            eval_results = evaluate(wave,
                    eval_params=EvalParams(ref_path=eval_ref_path))
            save_eval(eval_results, save_eval_params=SaveEvalParams(output_path=eval_out_path))
    else:
        print("Omitting evaluation")
        

# ./sss.py -t drums -e "database/test/Al James - Schoolboy Facination/drums.wav" "eval.json" "database/test/Al James - Schoolboy Facination/mixture.wav" 
if __name__ == "__main__":
    sss_command()

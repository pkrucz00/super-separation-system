import json

from sss.persistance import save_results, move_demucs

from sss.extractors.nmf import perform_nmf
from sss.extractors.demucs import perform_demucs
from sss.extractors.ExtractorParameters import ExtractorParameters


def perform_extraction(method, params):
    methods = {"nmf": perform_nmf, "demucs": perform_demucs}
    return methods[method](params)


def load_and_validate_json(input_json):
    input_map = json.loads(input_json)
    ### TODO add jsonschema
    return input_map

    
def evaluate_results(result_wave, eval_data):
    print("Evaluating: beep bop boop")
    

def save(result_wave, out_path, method):
    if method == "demucs":
        move_demucs(out_path)
    else:
        save_results(result_wave, out_path)


def command(input_json):
    input_map = load_and_validate_json(input_json)
    method, out_path = input_map["method"], input_map["output_path"]
    
    result = perform_extraction(method, ExtractorParameters(input_map))
    save(result, out_path, method)
    
    if "evaluation_data" in input_map:
        eval_data = input_map["evaluation_data"]
        evaluate_results(result, eval_data)    
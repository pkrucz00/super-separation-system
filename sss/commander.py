
import json


class ExtractorParameters:
    def __init__(self, input_map):
        self.input_path = input_map["input_path"]
        self.instrument = input_map.get("type", "full")
        self.reverse = self.__should_reverse(input_map)
        self.quality = input_map.get("quality", "fast")
        self.max_iter = input_map.get("max_iter", 20)
        
    @staticmethod
    def __should_reverse(input_map):
        return "reverse" in input_map and input_map["reverse"] or input_map["type"] == "karaoke"
    
    def __str__(self):
        return f"{self.input_path}\n{self.instrument}\n{self.reverse}\n"


def perform_extraction(method, params):
    if method == "nmf":
        print(f"apply NMF with params {params}")
        return [[2, 1], [3, 7]]


def load_and_validate_json(input_json):
    input_map = json.loads(input_json)
    ### TODO add jsonschema
    return input_map

    
def evaluate_results(ref_path, eval_path):
    pass


def command(input_json):
    input_map = load_and_validate_json(input_json)
    result = perform_extraction(
        input_map["method"],
        ExtractorParameters(input_map))
    
    
    print(result)
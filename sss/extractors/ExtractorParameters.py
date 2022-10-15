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
        return f"ExtractorParameters: {self.__dict__}"
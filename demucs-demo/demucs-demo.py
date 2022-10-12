import os
import click
import shutil

from enum import Enum
from pathlib import Path

class ExtractionType(Enum):
    KARAOKE = "karaoke"
    BASS = "bass"
    DRUMS = "drums"
    VOCAL = "vocal"
    FULL = "full"
    
    def to_stem_cmd(self):
        if self is ExtractionType.FULL:
            return ""
        
        stem_dict = {ExtractionType.KARAOKE: "vocals", ExtractionType.BASS: "bass",
                        ExtractionType.DRUMS: "drums", ExtractionType.VOCAL: "vocals"}
        return f"--two-stems {stem_dict[self]}"
    

def move_output_files(input_filename, output_folder):
    input_track = Path(input_filename).stem
    curr_folder = os.path.join(output_folder, "mdx_extra_q", input_track)
    
    sep_track_filenames = os.listdir(curr_folder)
    curr_paths = [os.path.join(curr_folder, filename) 
                 for filename in sep_track_filenames]
    dest_paths = [os.path.join(output_folder, f"{input_track}-{filename}")
                  for filename in sep_track_filenames]
    for old_path, new_path in zip(curr_paths, dest_paths):
        os.rename(old_path, new_path)
    
    folder_for_removal = os.path.join(output_folder, "mdx_extra_q")
    shutil.rmtree(folder_for_removal)


@click.command()
@click.option('-t', '--extraction-type', default='VOCAL', help='type of the extraction',
              type=click.Choice(ExtractionType.__members__),
              callback=lambda c, p, v: getattr(ExtractionType, v) if v else None)
@click.option('-o', '--output-file', default="results\\separated", type=click.Path(), help='output file location')
@click.argument('input-file', type=click.Path(exists=True))
def demucs_demo(extraction_type, output_file, input_file):
    result = os.system(f"demucs {extraction_type.to_stem_cmd()} -o {output_file} {input_file}")
    
    if not result:
        move_output_files(input_file, output_file)

# python demucs-demo.py maanam-test.mp4    
# python demucs-demo.py -o my_output_folder maanam-test.mp4
if __name__=="__main__":
    demucs_demo()
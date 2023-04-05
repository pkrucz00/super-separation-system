import os, shutil
import unittest
from unittest.mock import patch

from sss import commander
from sss.dataclasses import *


# mocked
import soundfile

class TestCommander(unittest.TestCase):
        
    def test_extract(self):
        # given
        method = "nmf"
        extract_parameters = ExtractParams(
            input_path="maanam-test.wav",
            instruments=[Instrument("vocals")],
            reverse=False,
            quality="fast",
            max_iter=1)
        
        # when
        actual_results = commander.extract(method, extract_parameters)
        
        # then
        self.assertEqual(len(actual_results), 1, "There is only one resulting audiowave")
        
        actual_instrument, actual_audio_wave = actual_results[0]
        self.assertEqual(actual_instrument, extract_parameters.instruments[0], "The instrument is good")
        self.assertEqual(actual_audio_wave.shape[1], 2, "The output is a stereo file (two channels)")
        
        
    def test_save(self):
        # given
        stub_track_name = "test"
        stub_output_folder = "stub_folder"
        params = SaveWavParams(
            sample_rate=44_100,
            input_track=stub_track_name,
            output_path=stub_output_folder)
        instrument = Instrument("vocals")
        audio_wave = np.arange(10, dtype="float64").reshape((-1, 2))
        
        # when
        actual_path = commander.save(audio_wave, instrument, params)
        
        try:
            # then
            self.assertTrue(os.path.isfile(actual_path + ".wav"), "Check if the file is in the folder given by save function")
            self.assertTrue(stub_output_folder in actual_path, "Check if save file is in the right folder")
            self.assertTrue(stub_track_name in actual_path, "Check if path includes title of the track")
        finally:
            #clean up
            shutil.rmtree(stub_output_folder)
        
        
    @patch('soundfile.read')
    def test_evaluate(self, mock_sf_read):
        # given
        stub_audiowave = np.arange(1_000_000, dtype="float64").reshape(-1, 2)
        dummy_ref_path = "abcd.wav"
        params = EvalParams(dummy_ref_path)
        
        # mock init
        dummy_ref_audiowave = np.arange(1, 1_000_001, dtype="float64").reshape(-1, 2)
        mock_sf_read.return_value = (dummy_ref_audiowave, 44100)
        
        # when 
        actual_evaluation = commander.evaluate(stub_audiowave, params)
     
        # then
        self.assertEqual(len(actual_evaluation), 4, "Evaluation consists of 4 types of metrics")
        self.assertTrue(len(actual_evaluation[0]) > 0, "There is one or more metric value")
        
        # mock check
        self.assertTrue(mock_sf_read.called)
        
    
    def test_save_eval(self):
        # given
        stub_output_path = "output_path"
        dummy_eval_results = tuple([[1,2,3] for _ in range(4)])
        stub_params = SaveEvalParams(stub_output_path)
        
        # when
        result_path = commander.save_eval(dummy_eval_results, stub_params)
        
        try:
            # then
            self.assertTrue(os.path.isfile(result_path))
            
        finally:
            #cleanup
            os.remove(stub_output_path)

if __name__=='__main__':
    unittest.main()
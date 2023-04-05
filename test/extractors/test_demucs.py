import unittest

import numpy as np

import sss.extractors.demucs as demucs
from sss.dataclasses import ExtractParams, Instrument

from test.utils import *

# Should demucs itself be mocked?
class TestDemucs(unittest.TestCase):
    def test_extraction(self):
        # given
        stub_audiowave = np.arange(100_000).reshape((-1, 2))
        stub_path = "stub_path_demucs.wav"
        save_stub_audiowave(stub_audiowave, stub_path)
        params = ExtractParams(
            input_path=stub_path,
            instruments=[Instrument("vocals"), Instrument("drums")],
            reverse=True,
            quality="fast",
            max_iter=1
        )
        
        expected_instruments = [Instrument("vocals"), Instrument("drums"), Instrument("other")]
    
        # when
        actual_result = demucs.perform_demucs(params)
        
        actual_instruments = [instr for instr, _ in actual_result]
        actual_audiowaves = [wave for _, wave in actual_result]
    
        # then
        self.assertEqual(len(actual_result), 3)
        self.assertListEqual(actual_instruments, expected_instruments)
        for actual_wave in actual_audiowaves:
            self.assertEqual(actual_wave.shape[1], 2, "Audiowaves are stereo (two channels)")
        
        #cleanup
        delete_stub_audiowave(stub_path)

if __name__=='__main__':
    unittest.main()
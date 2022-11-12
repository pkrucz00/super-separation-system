import os
import io

import numpy as np
from PyQt5 import QtWidgets, QtCore, QtMultimedia
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QIcon

from scipy.io import wavfile

from generated.gui_save_window_generated import Ui_SaveWindow

from sss.dataclasses import SaveWavParams, SaveEvalParams
from sss.commander import save, save_eval


class GUISave(Ui_SaveWindow):
    def __init__(self, my_data, widget):
        self.my_data = my_data
        self.widget = widget

        self.window = None
        self.player = QtMultimedia.QMediaPlayer()

    def add_features(self, window, gui_main):
        self.window = window
        self.main_ui = gui_main

        self.saveEvaluationButton.setDisabled(True)
        self.runButton.setDisabled(True)

        self.playButton.clicked.connect(self.play_handler)
        self.runButton.clicked.connect(self.run_handler)
        self.runButton.setIcon(QIcon('resources\\play_img.png'))
        self.volumeDownButton.clicked.connect(self.volumeDown_handler)
        self.volumeDownButton.setIcon(QIcon('resources\\vol_down_img.png'))
        self.volumeUpButton.clicked.connect(self.volumeUp_handler)
        self.volumeUpButton.setIcon(QIcon('resources\\vol_up_img.png'))
        self.saveOutputButton.clicked.connect(self.save_output_handler)
        self.saveEvaluationButton.clicked.connect(self.save_evaluation_handler)
        self.returnButton.clicked.connect(self.return_handler)

    def save_output_handler(self):
        output_location = QtWidgets.QFileDialog.getExistingDirectory(self.window,
                                                                          "Choose separation output directory", " ")
        if output_location:
            save(result_wave=self.my_data.audio_wave,
                 method=self.my_data.method,
                 save_params=SaveWavParams(
                     output_path=output_location,
                     instrument=self.my_data.extraction_type,
                     sample_rate=self.my_data.sr,
                     input_track=self.my_data.input_track_name))

    def save_evaluation_handler(self):
        evaluation_location = QtWidgets.QFileDialog.getExistingDirectory(self.window,
                                                                              "Choose evaluation output directory", " ")
        if evaluation_location:
            save_eval(eval_results=self.my_data.evaluation_results,
                            save_eval_params=
                                SaveEvalParams(evaluation_location + '/eval.json'))

    def return_handler(self):
        self.player.stop()
        self.runButton.setDisabled(True)
        self.runButton.setIcon(QIcon('resources\\play_img.png'))

        self.main_ui.importFIleLabel.setText(f'Import your music file here')
        self.main_ui.input_location = ''
        self.main_ui.startButton.setDisabled(True)

        self.main_ui.referenceLocationButton.setText('Reference')
        self.main_ui.evaluation_reference = ''
        self.saveEvaluationButton.setDisabled(True)

        self.widget.setCurrentIndex(0)

    def play_handler(self):
        if not os.path.isdir('temp_files'):
            os.makedirs('temp_files')
        for file_name in os.listdir('temp_files'):
            file = 'temp_files/' + file_name
            if os.path.isfile(file):
                os.remove(file)

        save(result_wave=self.my_data.audio_wave,
             method=self.my_data.method,
             save_params=SaveWavParams(
                 output_path='temp_files',
                 instrument=self.my_data.extraction_type,
                 sample_rate=self.my_data.sr,
                 input_track=self.my_data.input_track_name))

        file_path = os.path.join(os.getcwd(), 'temp_files', f'{self.my_data.input_track_name}-{self.my_data.extraction_type}.wav')
        url = QUrl.fromLocalFile(file_path)
        print(type(url))
        content = QtMultimedia.QMediaContent(url)
        self.player.setMedia(content)

        self.runButton.setDisabled(False)
        self.runButton.setIcon(QIcon('resources\\pause_img.png'))
        self.runButton.disconnect()
        self.runButton.clicked.connect(self.stop_handler)
        # self.runButton.setText('Stop')
        self.player.play()

    def run_handler(self):
        self.runButton.disconnect()
        self.runButton.clicked.connect(self.stop_handler)
        # self.runButton.setText('Stop')
        self.runButton.setIcon(QIcon('resources\\pause_img.png'))
        self.player.play()

    def stop_handler(self):
        self.runButton.disconnect()
        self.runButton.clicked.connect(self.run_handler)
        # self.runButton.setText('Run')
        self.runButton.setIcon(QIcon('resources\\play_img.png'))
        self.player.pause()

    def volumeUp_handler(self):
        current_volume = self.player.volume()
        self.player.setVolume(current_volume + 5)

    def volumeDown_handler(self):
        current_volume = self.player.volume()
        self.player.setVolume(current_volume - 5)

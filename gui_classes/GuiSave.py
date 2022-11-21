import functools
import os

import numpy as np
from PyQt5 import QtWidgets, QtCore, QtMultimedia, QtGui
from PyQt5.QtCore import QUrl, QTimer
from PyQt5.QtGui import QIcon


from generated.gui_save_window_generated import Ui_SaveWindow

from sss.dataclasses import SaveWavParams, SaveEvalParams
from sss.commander import save, save_eval


class GUISave(Ui_SaveWindow):
    def __init__(self, my_data, widget):
        self.my_data = my_data
        self.widget = widget

        self.window = None
        self.main_ui = None
        self.timer = None
        self.display_eval_res = False
        self.dynamicWidgets = []
        self.player = QtMultimedia.QMediaPlayer()
        self.mean_eval = {'vocals': {}, 'drums': {}, 'bass': {}, 'other': {}}

    def add_features(self, window, gui_main):
        self.window = window
        self.main_ui = gui_main

        self.runButton.setDisabled(True)

        self.runButton.clicked.connect(self.run_handler)
        self.runButton.setIcon(QIcon('resources\\play_img.png'))
        self.volumeDownButton.clicked.connect(self.volumeDown_handler)
        self.volumeDownButton.setIcon(QIcon('resources\\vol_down_img.png'))
        self.volumeUpButton.clicked.connect(self.volumeUp_handler)
        self.volumeUpButton.setIcon(QIcon('resources\\vol_up_img.png'))
        self.returnButton.clicked.connect(self.return_handler)

    def add_save_results(self):
        self.timer = QTimer()

        font = QtGui.QFont()
        font.setFamily("Segoe UI")
        font.setPointSize(12)

        index = 0
        for index, result in enumerate(self.my_data.audio_wave):
            labelName = QtWidgets.QLabel(self.centralwidget)
            labelName.setFont(font)
            labelName.setText(f'{result[0].value}')
            labelName.setMinimumSize(QtCore.QSize(120, 40))

            listenButton = QtWidgets.QPushButton(self.centralwidget)
            listenButton.setText('Listen')
            listenButton.setFont(font)
            listenButton.clicked.connect(functools.partial(self.play_handler, index))
            listenButton.setMinimumSize(QtCore.QSize(120, 40))

            saveOutputButton = QtWidgets.QPushButton(self.centralwidget)
            saveOutputButton.setText('Save Output')
            saveOutputButton.setFont(font)
            saveOutputButton.clicked.connect(functools.partial(self.save_output_handler, index))
            saveOutputButton.setMinimumSize(QtCore.QSize(120, 40))

            saveEvaluationButton = QtWidgets.QPushButton(self.centralwidget)
            saveEvaluationButton.setText('Save Evaluation')
            saveEvaluationButton.setFont(font)
            saveEvaluationButton.clicked.connect(functools.partial(self.save_evaluation_handler, result[0].value))
            saveEvaluationButton.setMinimumSize(QtCore.QSize(120, 40))
            if not self.my_data.evaluation_results[result[0].value]:
                saveEvaluationButton.setDisabled(True)
            else:
                for metric_index, metric_name in enumerate(['SDR', 'SIR', 'SAR', 'ISR']):
                    eval_sum = np.sum(np.nan_to_num(self.my_data.evaluation_results[result[0].value][0]))
                    eval_len = self.my_data.evaluation_results[result[0].value][0].shape
                    self.mean_eval[result[0].value][metric_name] = eval_sum / eval_len

                self.timer.timeout.connect(functools.partial(self.eval_res_disp_handler, saveEvaluationButton, result[0].value))

            self.resultsLayout.addWidget(labelName, index, 0, 1, 1)
            self.resultsLayout.addWidget(listenButton, index, 1, 1, 1)
            self.resultsLayout.addWidget(saveOutputButton, index, 2, 1, 1)
            self.resultsLayout.addWidget(saveEvaluationButton, index, 3, 1, 1)

            self.dynamicWidgets.append([labelName, listenButton, saveOutputButton, saveEvaluationButton])

        evauationResults = QtWidgets.QLabel(self.centralwidget)
        evauationResults.setFont(font)
        evauationResults.setMaximumSize(QtCore.QSize(500, 500))
        self.resultsLayout.addWidget(evauationResults, index+1, 0, 1, 4)
        evauationResults.setText('')
        self.dynamicWidgets.append([evauationResults])

        self.timer.start(100)

    def save_output_handler(self, index):
        output_location = QtWidgets.QFileDialog.getExistingDirectory(self.window,
                                                                          "Choose separation output directory", " ")
        if output_location:
            save(result_wave=self.my_data.audio_wave[index][1],
                 instrument=self.my_data.audio_wave[index][0],
                 save_params=SaveWavParams(
                     sample_rate=self.my_data.sr,
                     input_track=self.my_data.input_track_name,
                     output_path=output_location))

    def save_evaluation_handler(self, instrument):
        evaluation_location = QtWidgets.QFileDialog.getExistingDirectory(self.window, "Choose evaluation output directory", " ")
        if evaluation_location:
            save_eval(eval_results=self.my_data.evaluation_results[instrument],
                      save_eval_params=SaveEvalParams(evaluation_location + f'/{self.my_data.input_track_name}-{instrument}-eval.json'))

    def return_handler(self):
        self.timer.stop()

        self.player.stop()
        self.runButton.setDisabled(True)
        self.runButton.setIcon(QIcon('resources\\play_img.png'))

        self.main_ui.importFIleLabel.setText(f'Import your music file here')
        self.main_ui.input_location = ''
        self.main_ui.startButton.setDisabled(True)

        for instrument_widgets in self.dynamicWidgets:
            for widget in instrument_widgets:
                widget.deleteLater()
        self.dynamicWidgets = []

        for button_name in self.main_ui.reference_buttons:
            self.main_ui.reference_buttons[button_name].setText(button_name)

        for instrument in self.my_data.evaluation_results:
            self.my_data.evaluation_results[instrument] = None

        for instrument in self.my_data.evaluation_references:
            self.my_data.evaluation_references[instrument] = None

        for instrument in self.mean_eval:
            self.mean_eval[instrument] = {}

        self.widget.setCurrentIndex(0)

    def play_handler(self, index):
        if not os.path.isdir('temp_files'):
            os.makedirs('temp_files')
        for file_name in os.listdir('temp_files'):
            file = 'temp_files/' + file_name
            if os.path.isfile(file):
                os.remove(file)

        save(result_wave=self.my_data.audio_wave[index][1],
             instrument=self.my_data.audio_wave[index][0],
             save_params=SaveWavParams(
                 sample_rate=self.my_data.sr,
                 input_track=self.my_data.input_track_name,
                 output_path='temp_files'))

        ### TESTING  # todo: delete this block later; solve problem with player updating (when new .wav file has the same name)
        file_path = os.path.join(os.getcwd(), 'temp_file.wav')
        url = QUrl.fromLocalFile(file_path)
        content = QtMultimedia.QMediaContent(url)
        self.player.setMedia(content)
        ### TESTING END

        file_path = os.path.join(os.getcwd(), 'temp_files', f'{self.my_data.input_track_name}-{self.my_data.audio_wave[index][0].value}.wav')
        url = QUrl.fromLocalFile(file_path)
        content = QtMultimedia.QMediaContent(url)
        self.player.setMedia(content)

        self.runButton.setDisabled(False)
        self.runButton.setIcon(QIcon('resources\\pause_img.png'))
        self.runButton.disconnect()
        self.runButton.clicked.connect(self.stop_handler)

        self.player.play()

    def eval_res_disp_handler(self, button, instrument):
        under = button.underMouse()
        if under:
            if not self.display_eval_res:
                means = self.mean_eval[instrument]
                self.dynamicWidgets[-1][0].setText(f'{instrument}\nSDR: {means["SDR"]}\nSIR{means["SIR"]}\nSAR: {means["SAR"]}\nISR: {means["ISR"]}')
                self.display_eval_res = True
        else:
            if self.display_eval_res:
                self.dynamicWidgets[-1][0].setText('')
                self.display_eval_res = False

    def run_handler(self):
        self.runButton.disconnect()
        self.runButton.clicked.connect(self.stop_handler)
        self.runButton.setIcon(QIcon('resources\\pause_img.png'))
        self.player.play()

    def stop_handler(self):
        self.runButton.disconnect()
        self.runButton.clicked.connect(self.run_handler)
        self.runButton.setIcon(QIcon('resources\\play_img.png'))
        self.player.pause()

    def volumeUp_handler(self):
        current_volume = self.player.volume()
        self.player.setVolume(current_volume + 5)

    def volumeDown_handler(self):
        current_volume = self.player.volume()
        self.player.setVolume(current_volume - 5)

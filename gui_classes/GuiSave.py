import functools
import os

from PyQt5 import QtWidgets, QtCore, QtMultimedia, QtGui
from PyQt5.QtCore import QUrl
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
        self.dynamicWidgets = []
        self.player = QtMultimedia.QMediaPlayer()

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
        for index, result in enumerate(self.my_data.audio_wave):
            font = QtGui.QFont()
            font.setFamily("Segoe UI")
            font.setPointSize(12)

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

            self.resultsLayout.addWidget(labelName, index, 0, 1, 1)
            self.resultsLayout.addWidget(listenButton, index, 1, 1, 1)
            self.resultsLayout.addWidget(saveOutputButton, index, 2, 1, 1)
            self.resultsLayout.addWidget(saveEvaluationButton, index, 3, 1, 1)

            self.dynamicWidgets.append([labelName, listenButton, saveOutputButton, saveEvaluationButton])

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
        print('T0', self.my_data.evaluation_results[instrument])
        print('T1', SaveEvalParams(evaluation_location + f'/{self.my_data.input_track_name}-{instrument}-eval.json'))
        if evaluation_location:
            save_eval(eval_results=self.my_data.evaluation_results[instrument],
                      save_eval_params=SaveEvalParams(evaluation_location + f'/{self.my_data.input_track_name}-{instrument}-eval.json'))

    def return_handler(self):
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

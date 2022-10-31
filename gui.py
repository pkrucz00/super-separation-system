#!/usr/bin/env python
import os
import sys
import soundfile as sf

from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication, QUrl
from PyQt5.QtGui import QMovie
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer

from generated.gui_main_window_generated import Ui_MainWindow
from generated.gui_loading_window_generated import Ui_LoadingWindow
from generated.gui_save_window_generated import Ui_SaveWindow

from sss.dataclasses import ExtractParams, SaveWavParams, EvalParams, SaveEvalParams, ExtractionType, AudioWave
from sss.commander import extract,  evaluate, save, save_eval

from dataclasses import dataclass

@dataclass
class DataContainer:
    audio_wave: AudioWave = None
    method: str = None
    extraction_type: ExtractionType = None
    sr: int = None
    evaluation_results = None
    input_track_name: str = None


class GUIMain(Ui_MainWindow):
    def __init__(self, my_data):
        self.my_data = my_data

        self.evaluation_reference = None
        self.input_location = None
        self.window = None
        self.save_ui = None

    def add_features(self, window, gui_save):
        self.window = window
        self.input_location = None
        self.evaluation_reference = None
        self.startButton.setDisabled(True)
        self.save_ui = gui_save

        self.importFileButton.clicked.connect(self.wav_file_location_handler)
        self.referenceLocationButton.clicked.connect(self.evaluation_reference_file_location_handler)

        self.startButton.clicked.connect(self.run_sss)

    def wav_file_location_handler(self):
        self.input_location, _ = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                                       "Choose input file", " ", "(*.wav)")
        if(self.input_location):
            self.my_data.input_track_name = ''.join(self.input_location.split('/')[-1].split('.')[:-1])
            self.importFIleLabel.setText(f'file imported')
            self.startButton.setDisabled(False)

    def evaluation_reference_file_location_handler(self):
        self.evaluation_reference, _ = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                                             "Choose evaluation reference file",
                                                                             " ", "(*.wav)")
        if self.evaluation_reference:
            self.save_ui.saveEvaluationButton.setDisabled(False)

    def run_sss(self):
        self.my_data.extraction_type = ExtractionType[self.extractionTypeComboBox.currentText().lower()].to_instrument()
        self.my_data.method = self.extractionMethodComboBox.currentText().lower() 
        widget.setCurrentIndex(1)
        QCoreApplication.processEvents()

        self.my_data.audio_wave = \
            extract(method=self.my_data.method,
                    params=ExtractParams(
                            input_path=self.input_location,
                            instrument=self.my_data.extraction_type,
                            reverse=self.reverseCheckBox.isChecked(),
                            quality='to_delete',
                            max_iter=self.maxIterationsSpinBox.value()))
        _, self.my_data.sr = sf.read(self.input_location)
        
        if self.evaluation_reference:
           self.my_data.evaluation_results = evaluate(result_wave=self.my_data.audio_wave,
                                             eval_params=EvalParams(self.evaluation_reference))
           self.evaluation_reference = ''

        self.save_ui.outputNameLabel.setText(f'{self.my_data.extraction_type}')
        widget.setCurrentIndex(2)


class GUILoading(Ui_LoadingWindow):
    def __init__(self):
        self.window = None
        self.loading_gif = QMovie('resources\loading.gif')

    def add_features(self, window):
        self.window = window

        self.gifLabel.setMovie(self.loading_gif)
        self.loading_gif.start()


class GUISave(Ui_SaveWindow):
    def __init__(self, my_data):
        self.window = None
        self.my_data = my_data
        self.player = QMediaPlayer()

    def add_features(self, window):
        self.window = window

        self.saveEvaluationButton.setDisabled(True)
        self.runButton.setDisabled(True)

        self.playButton.clicked.connect(self.play_handler)
        self.runButton.clicked.connect(self.run_handler)
        self.volumeDownButton.clicked.connect(self.volumeDown_handler)
        self.volumeUpButton.clicked.connect(self.volumeUp_handler)
        self.saveOutputButton.clicked.connect(self.save_output_handler)
        self.saveEvaluationButton.clicked.connect(self.save_evaluation_handler)
        self.returnButton.clicked.connect(self.return_handler)

    def save_output_handler(self):
        output_location = QtWidgets.QFileDialog.getExistingDirectory(self.window,
                                                                          "Choose separation output directory", "c:\\")
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
        widget.setCurrentIndex(0)

    def play_handler(self):
        for file_name in os.listdir('temp_files'):
            file = 'temp_files/' + file_name
            print(file)
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
        content = QMediaContent(url)
        self.player.setMedia(content)

        self.runButton.setDisabled(False)
        self.runButton.disconnect()
        self.runButton.clicked.connect(self.stop_handler)
        self.runButton.setText('Stop')
        self.player.play()

    def run_handler(self):
        self.runButton.disconnect()
        self.runButton.clicked.connect(self.stop_handler)
        self.runButton.setText('Stop')
        self.player.play()

    def stop_handler(self):
        self.runButton.disconnect()
        self.runButton.clicked.connect(self.run_handler)
        self.runButton.setText('Run')
        self.player.pause()

    def volumeUp_handler(self):
        currentVolume = self.player.volume()
        self.player.setVolume(currentVolume + 5)

    def volumeDown_handler(self):
        currentVolume = self.player.volume()
        self.player.setVolume(currentVolume - 5)


if __name__ == "__main__":
    my_data = DataContainer()

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()

    window_loading = QtWidgets.QMainWindow()
    loading = GUILoading()
    loading.setupUi(window_loading)
    loading.add_features(window_loading)

    window_save = QtWidgets.QMainWindow()
    gui_save = GUISave(my_data)
    gui_save.setupUi(window_save)
    gui_save.add_features(window_save)

    window_main = QtWidgets.QMainWindow()
    main = GUIMain(my_data)
    main.setupUi(window_main)
    main.add_features(window_main, gui_save)

    widget.addWidget(window_main)
    widget.addWidget(window_loading)
    widget.addWidget(window_save)

    widget.show()
    sys.exit(app.exec_())

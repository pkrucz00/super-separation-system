import soundfile as sf
import threading
import functools

from PyQt5 import QtWidgets, QtCore

from generated.gui_main_window_generated import Ui_MainWindow

from sss.dataclasses import ExtractParams, EvalParams, ExtractionType
from sss.commander import extract,  evaluate


class ExtractManager(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def start(self, my_data, extract_params):
        threading.Thread(target=self._execute, args=(my_data, extract_params), daemon=True).start()

    def _execute(self, my_data, extract_params):
        self.started.emit()

        my_data.audio_wave = extract(method=my_data.method, params=extract_params)

        for (instrument, wave) in my_data.audio_wave:
            if my_data.evaluation_references[instrument.value]:
                my_data.evaluation_results[instrument.value] = evaluate(result_wave=wave, eval_params=EvalParams(my_data.evaluation_references[instrument.value]))

        self.finished.emit()


class GUIMain(Ui_MainWindow):
    def __init__(self, my_data, widget):
        self.my_data = my_data
        self.widget = widget

        self.extractManager = ExtractManager()

        self.reference_buttons = None
        self.input_location = None
        self.window = None
        self.save_ui = None

    def add_features(self, window, gui_save):
        self.window = window
        self.save_ui = gui_save

        self.importFileButton.clicked.connect(self.wav_file_location_handler)

        self.reference_buttons = {'vocals': self.VocalsRefLocButton, 'drums': self.DrumsRefLocButton,
                                  'bass': self.BassRefLocButton, 'other': self.OtherRefLocButton}
        for instrument in self.reference_buttons:
            self.reference_buttons[instrument].clicked.connect(functools.partial(self.eval_ref_file_location_handler, instrument))

        self.startButton.setDisabled(True)
        self.startButton.clicked.connect(self.run_sss)


    def wav_file_location_handler(self):
        self.input_location, _ = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                                       "Choose input file", " ", "(*.wav)")
        if self.input_location:
            self.my_data.input_track_name = ''.join(self.input_location.split('/')[-1].split('.')[:-1])
            self.importFIleLabel.setText(f'File imported - {self.my_data.input_track_name}')
            self.startButton.setDisabled(False)

    def eval_ref_file_location_handler(self, instrument):
        self.my_data.evaluation_references[instrument], _ = QtWidgets.QFileDialog.getOpenFileName(self.window, "Choose evaluation reference file", " ", "(*.wav)")

        if self.my_data.evaluation_references[instrument]:
            self.reference_buttons[instrument].setText(f'{self.my_data.evaluation_references[instrument].split("/")[-1]}')

    def run_sss(self):
        self.my_data.extraction_type = ExtractionType(self.extractionTypeComboBox.currentText().lower()).to_instrument()
        self.my_data.method = self.extractionMethodComboBox.currentText().lower()
        # QCoreApplication.processEvents()

        _, self.my_data.sr = sf.read(self.input_location)

        extract_params = ExtractParams(
                        input_path=self.input_location,
                        instruments=self.my_data.extraction_type,
                        quality=self.qualityComboBox.currentText().lower(),
                        reverse=self.reverseCheckBox.isChecked() or self.extractionTypeComboBox.currentText().lower() == 'karaoke',
                        max_iter=0)

        self.extractManager.started.connect(lambda: self.widget.setCurrentIndex(1))
        self.extractManager.finished.connect(lambda: self.widget.setCurrentIndex(2))
        self.extractManager.finished.connect(self.save_ui.add_save_results)
        self.extractManager.start(my_data=self.my_data, extract_params=extract_params)

import soundfile as sf
import threading
import functools

from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QCoreApplication

from generated.gui_main_window_generated import Ui_MainWindow

from sss.dataclasses import ExtractParams, EvalParams, ExtractionType
from sss.commander import extract,  evaluate


class ExtractManager(QtCore.QObject):
    started = QtCore.pyqtSignal()
    finished = QtCore.pyqtSignal()

    def start(self, my_data, extract_params, gui_main):
        # threading.Thread(target=self._execute, args=(my_data, extract_params, eval_reference), daemon=True).start()

        test_thread = threading.Thread(target=self._execute, args=(my_data, extract_params, gui_main), daemon=True)
        test_thread.start()
        # test_thread.join()

    def _execute(self, my_data, extract_params, gui_main):
        self.started.emit()

        my_data.audio_wave = extract(method=my_data.method, params=extract_params)

        if gui_main.evaluation_reference:
            my_data.evaluation_results = evaluate(result_wave=my_data.audio_wave, eval_params=EvalParams(gui_main.evaluation_reference))

        self.finished.emit()


class GUIMain(Ui_MainWindow):
    def __init__(self, my_data, widget):
        self.my_data = my_data
        self.widget = widget

        self.extractManager = ExtractManager()
        self.evaluation_reference = None
        self.input_location = None
        self.window = None
        self.save_ui = None

    def add_features(self, window, gui_save):
        self.window = window
        self.save_ui = gui_save

        self.input_location = None
        self.evaluation_reference = None
        self.startButton.setDisabled(True)

        self.importFileButton.clicked.connect(self.wav_file_location_handler)
        self.referenceLocationButton.clicked.connect(self.evaluation_reference_file_location_handler)

        self.startButton.clicked.connect(self.run_sss)

    def wav_file_location_handler(self):
        self.input_location, _ = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                                       "Choose input file", " ", "(*.wav)")
        if self.input_location:
            self.my_data.input_track_name = ''.join(self.input_location.split('/')[-1].split('.')[:-1])
            self.importFIleLabel.setText(f'File imported - {self.my_data.input_track_name}')
            self.startButton.setDisabled(False)

    def evaluation_reference_file_location_handler(self):
        self.evaluation_reference, _ = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                                             "Choose evaluation reference file",
                                                                             " ", "(*.wav)")
        if self.evaluation_reference:
            self.referenceLocationButton.setText(f'{self.evaluation_reference.split("/")[-1]}')

    def run_sss(self):
        self.my_data.extraction_type = ExtractionType(self.extractionTypeComboBox.currentText().lower()).to_instrument()
        self.my_data.method = self.extractionMethodComboBox.currentText().lower()
        # QCoreApplication.processEvents()

        _, self.my_data.sr = sf.read(self.input_location)

        extract_params = ExtractParams(
                        input_path=self.input_location,
                        instruments=self.my_data.extraction_type,
                        quality='todo',  # todo
                        reverse=self.reverseCheckBox.isChecked(),
                        max_iter=self.maxIterationsSpinBox.value())

        self.extractManager.started.connect(lambda: self.widget.setCurrentIndex(1))
        self.extractManager.finished.connect(lambda: self.widget.setCurrentIndex(2))
        self.extractManager.finished.connect(self.save_ui.add_save_results)
        self.extractManager.start(my_data=self.my_data, extract_params=extract_params, gui_main=self)

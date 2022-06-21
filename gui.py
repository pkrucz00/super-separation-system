from PyQt5 import QtWidgets
from PyQt5.QtCore import QCoreApplication
import sys

from gui_main_window_generated import Ui_MainWindow
from gui_loading_window_generated import Ui_LoadingWindow
from gui_save_window_generated import Ui_SaveWindow

from sss import Separator, ExtractionType


class DataContainer:
    def __init__(self):
        self.extraction_type = None
        self.reverse = None
        self.evaluate = False


class GUIMain(Ui_MainWindow):
    def __init__(self, my_separator, my_data):
        self.my_separator = my_separator
        self.my_data = my_data

        self.evaluation_reference = None
        self.input_location = None
        self.window = None
        self.save_ui = None

    def add_features(self, window, save):
        self.window = window
        self.input_location = None
        self.evaluation_reference = None
        self.startButton.setDisabled(True)
        self.save_ui = save

        self.importFileButton.clicked.connect(self.wav_file_location_handler)
        self.referenceLocationButton.clicked.connect(self.evaluation_reference_file_location_handler)

        self.startButton.clicked.connect(self.run_sss)

    def wav_file_location_handler(self):
        self.input_location, _ = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                                       "Choose input file", " ", "(*.wav)")
        self.importFIleLabel.setText(f'file imported')
        self.startButton.setDisabled(False)

    def evaluation_reference_file_location_handler(self):
        self.evaluation_reference, _ = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                                             "Choose evaluation reference file",
                                                                             " ", "(*.wav)")
        self.save_ui.saveEvaluationButton.setDisabled(False)

    def run_sss(self):
        self.my_data.extraction_type = ExtractionType[self.extractionTypeComboBox.currentText()]
        self.my_data.reverse = self.reverseCheckBox.isChecked()

        widget.setCurrentIndex(1)
        QCoreApplication.processEvents()

        self.my_separator.sss(ExtractionType[self.extractionTypeComboBox.currentText()],
                              self.extractionMethodComboBox.currentText(),
                              self.qualityComboBox.currentText(),
                              self.reverseCheckBox.isChecked(),
                              self.evaluation_reference,
                              self.maxTimeSpinBox.value(),
                              self.maxIterationsSpinBox.value(),
                              self.input_location)

        widget.setCurrentIndex(2)


class GUISave(Ui_SaveWindow):
    def __init__(self, my_separator, my_data):
        self.my_separator = my_separator
        self.my_data = my_data

        self.window = None

    def add_features(self, window):
        self.window = window

        self.saveEvaluationButton.setDisabled(True)

        self.playButton.clicked.connect(self.play_handler)
        self.saveOutputButton.clicked.connect(self.save_output_handler)
        self.saveEvaluationButton.clicked.connect(self.save_evaluation_handler)
        self.returnButton.clicked.connect(self.return_handler)

    def save_output_handler(self):
        output_location = QtWidgets.QFileDialog.getExistingDirectory(self.window,
                                                                          "Choose separation output directory", "c:\\")

        print(output_location)
        self.my_separator.save_results(output_location + '/extracted',
                                       self.my_data.extraction_type,
                                       self.my_data.reverse)

    def save_evaluation_handler(self):
        evaluation_location = QtWidgets.QFileDialog.getExistingDirectory(self.window,
                                                                              "Choose evaluation output directory", " ")
        self.my_separator.save_evaluation(evaluation_location + '/eval.json')

    def return_handler(self):
        widget.setCurrentIndex(0)

    def play_handler(self):
        pass


if __name__ == "__main__":
    my_sep = Separator()
    my_data = DataContainer()

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()

    window_loading = QtWidgets.QMainWindow()
    loading = Ui_LoadingWindow()
    loading.setupUi(window_loading)

    window_save = QtWidgets.QMainWindow()
    save = GUISave(my_sep, my_data)
    save.setupUi(window_save)
    save.add_features(window_save)

    window_main = QtWidgets.QMainWindow()
    main = GUIMain(my_sep, my_data)
    main.setupUi(window_main)
    main.add_features(window_main, save)

    widget.addWidget(window_main)
    widget.addWidget(window_loading)
    widget.addWidget(window_save)

    widget.show()
    sys.exit(app.exec_())

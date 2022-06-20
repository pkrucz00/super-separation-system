from PyQt5 import QtWidgets

from gui_main_window_generated import Ui_MainWindow
from gui_second_window_generated import Ui_SecondWindow
from sss import Separator, ExtractionType
import sys


class DataContainer:
    def __init__(self):
        self.extraction_type = None
        self.reverse = None


class GUIMain(Ui_MainWindow):
    def __init__(self, my_separator, my_data):
        self.my_separator = my_separator
        self.my_data = my_data

        self.evaluation_reference = None
        self.input_location = None
        self.window = None

    def add_features(self, window):
        self.window = window
        self.input_location = None
        self.evaluation_reference = None

        self.importFileButton.clicked.connect(self.wav_file_location_handler)
        self.referenceLocationButton.clicked.connect(self.evaluation_reference_file_location_handler)

        self.startButton.clicked.connect(self.run_sss)

    def wav_file_location_handler(self):
        self.input_location, _ = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                                       "Choose input file", " ", "(*.wav)")
        self.importFIleLabel.setText(f'file imported')

    def evaluation_reference_file_location_handler(self):
        self.evaluation_reference, _ = QtWidgets.QFileDialog.getOpenFileName(self.window,
                                                                             "Choose evaluation reference file",
                                                                             " ", "(*.wav)")

    def run_sss(self):
        self.my_data.extraction_type = ExtractionType[self.extractionTypeComboBox.currentText()]
        self.my_data.reverse = self.reverseCheckBox.isChecked()

        self.my_separator.sss(ExtractionType[self.extractionTypeComboBox.currentText()],
                              self.extractionMethodComboBox.currentText(),
                              self.qualityComboBox.currentText(),
                              self.reverseCheckBox.isChecked(),
                              self.evaluation_reference,
                              self.maxTimeSpinBox.value(),
                              self.maxIterationsSpinBox.value(),
                              self.input_location)

        widget.setCurrentIndex(widget.currentIndex()+1)


class GUISecond(Ui_SecondWindow):
    def __init__(self, my_separator, my_data):
        self.my_separator = my_separator
        self.my_data = my_data

        self.evaluation_location = None
        self.output_location = None
        self.window = None

    def add_features(self, window):
        self.window = window
        self.output_location = None
        self.evaluation_location = None

        self.outputLocationButton.clicked.connect(self.separation_output_location_handler)
        self.evaluationLocationButton.clicked.connect(self.evaluation_output_location_handler)
        self.returnButton.clicked.connect(self.return_handler)
        self.saveButton.clicked.connect(self.save_results_handler)

    def separation_output_location_handler(self):
        self.output_location = QtWidgets.QFileDialog.getExistingDirectory(self.window,
                                                                          "Choose separation output directory", "c:\\")

    def evaluation_output_location_handler(self):
        self.evaluation_location = QtWidgets.QFileDialog.getExistingDirectory(self.window,
                                                                              "Choose evaluation output directory", " ")

    def return_handler(self):
        widget.setCurrentIndex(widget.currentIndex()-1)

    def save_results_handler(self):
        self.my_separator.save_results(self.output_location + '/extracted',
                                       self.my_data.extraction_type,
                                       self.my_data.reverse,
                                       self.evaluation_location + '/eval.json')


if __name__ == "__main__":
    my_sep = Separator()
    my_data = DataContainer()

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()

    window_1 = QtWidgets.QMainWindow()
    main = GUIMain(my_sep, my_data)
    main.setupUi(window_1)
    main.add_features(window_1)
    widget.addWidget(window_1)

    window_2 = QtWidgets.QMainWindow()
    second = GUISecond(my_sep, my_data)
    second.setupUi(window_2)
    second.add_features(window_2)
    widget.addWidget(window_2)

    widget.show()
    sys.exit(app.exec_())

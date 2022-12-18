#!/usr/bin/env python
import sys

from PyQt5 import QtWidgets

from gui_classes.DataContainer import DataContainer
from gui_classes.GuiLoading import GUILoading
from gui_classes.GuiMain import GUIMain
from gui_classes.GuiSave import GUISave


if __name__ == "__main__":
    my_data = DataContainer()

    app = QtWidgets.QApplication(sys.argv)
    widget = QtWidgets.QStackedWidget()

    window_loading = QtWidgets.QMainWindow()
    gui_loading = GUILoading()
    gui_loading.setupUi(window_loading)

    window_save = QtWidgets.QMainWindow()
    gui_save = GUISave(my_data, widget)
    gui_save.setupUi(window_save)

    window_main = QtWidgets.QMainWindow()
    gui_main = GUIMain(my_data, widget)
    gui_main.setupUi(window_main)

    gui_loading.add_features(window_loading)
    gui_save.add_features(window_save, gui_main)
    gui_main.add_features(window_main, gui_save)

    widget.addWidget(window_main)
    widget.addWidget(window_loading)
    widget.addWidget(window_save)

    widget.show()
    sys.exit(app.exec_())

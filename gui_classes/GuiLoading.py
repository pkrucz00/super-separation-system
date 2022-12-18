from PyQt5.QtGui import QMovie
from generated.gui_loading_window_generated import Ui_LoadingWindow


class GUILoading(Ui_LoadingWindow):
    def __init__(self):
        self.window = None
        self.loading_gif = QMovie('resources\loading.gif')

    def add_features(self, window):
        self.window = window

        self.gifLabel.setMovie(self.loading_gif)
        self.loading_gif.start()

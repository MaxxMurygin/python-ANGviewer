import logging
import os
import time
from configparser import ConfigParser

from manager import EffectiveManager

import threading

# ----------gui-----------------
import sys
import PyQt5
from gui_ANGviewer.guiFormMainCode import GuiFormMain, QtWidgets
from PyQt5 import QtCore, QtGui, QtWidgets

from PyQt5.QtWidgets import QApplication, QSplashScreen, QWidget, \
    QMainWindow, QLabel, QGridLayout, QStyle, QDesktopWidget
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import Qt, QTimer, QRect


# ==============================

class GifSplashScreen(QSplashScreen):
    def __init__(self, *args, **kwargs):
        super(GifSplashScreen, self).__init__(*args, **kwargs)
        self.movie = QMovie(':/Images/Source/Images/orbit_Load.gif')
        self.movie.frameChanged.connect(self.onFrameChanged)
        self.movie.start()

    def onFrameChanged(self, _):
        self.setPixmap(self.movie.currentPixmap())

    def finish(self, widget):
        self.movie.stop()
        super(GifSplashScreen, self).finish(widget)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)

    splash = GifSplashScreen()
    splash.show()

    # ==================================================================
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) %(message)s', )

    logging.getLogger('matplotlib.font_manager').disabled = True

    config_file: str = "currentConfigView.conf" if (os.path.exists("currentConfigView.conf")) else "config.conf"


    # ==================================================================

    def create_main_window():
        global manager

        splash.showMessage(
            'Инициализация модулей',
            Qt.AlignHCenter | Qt.AlignBottom, Qt.white
        )
        app.processEvents()

        manager = EffectiveManager(config_file)

        splash.showMessage(
            'Инициализация интерфейса',
            Qt.AlignHCenter | Qt.AlignBottom, Qt.white
        )
        app.processEvents()

        try:
            app.window = GuiFormMain(manager)
        except:
            splash.close()
            exit()

        # app.window.action_view.figGraphTime.tight_layout()
        # app.window.action_view.figGraphTime.canvas.draw()
        # app.window.action_view.figGraphPolar.tight_layout()
        # app.window.action_view.figGraphPolar.canvas.draw()

        # rect = app.window.frameGeometry()
        # rect.moveCenter(app.desktop().availableGeometry().center())
        # app.window.move(rect.topLeft())

        splash.showMessage(
            'Загрузка завершена',
            Qt.AlignHCenter | Qt.AlignBottom, Qt.white
        )
        app.processEvents()

        splash.finish(app.window)
        app.window.show()

    QTimer.singleShot(500, create_main_window)

    sys.exit(app.exec_())

    exit()

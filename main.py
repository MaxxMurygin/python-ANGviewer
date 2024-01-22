import logging
import os
from configparser import ConfigParser

from manager import EffectiveManager

# ----------gui-----------------
import sys
from gui_ANGviewer.guiFormMainCode import GuiFormMain, QtWidgets

# ==============================


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) %(message)s', )

    logging.getLogger('matplotlib.font_manager').disabled = True

    config_file: str = "currentConfigView.conf" if (os.path.exists("currentConfigView.conf")) else "config.conf"

    manager = EffectiveManager(config_file)

    app = QtWidgets.QApplication(sys.argv)
    window = GuiFormMain(manager)
    window.show()

    window.action_view.figGraphTime.tight_layout()
    window.action_view.figGraphTime.canvas.draw()
    window.action_view.figGraphPolar.tight_layout()
    window.action_view.figGraphPolar.canvas.draw()
    window.repaint()

    sys.exit(app.exec_())

    exit()

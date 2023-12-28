import logging
from manager import EffectiveManager

import sys
from gui_ANGviewer.guiFormMainCode import guiFormMain, QtWidgets

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) %(message)s', )
    logging.getLogger('matplotlib.font_manager').disabled = True

    config_file = "config.conf"
    manager = EffectiveManager(config_file)

    app = QtWidgets.QApplication(sys.argv)
    window = guiFormMain(manager)
    window.show()

    window.figGraphTime.tight_layout()
    window.figGraphTime.canvas.draw()
    window.figGraphPolar.tight_layout()
    window.figGraphPolar.canvas.draw()
    window.repaint()

    sys.exit(app.exec_())

    exit()

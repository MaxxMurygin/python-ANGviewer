import logging
import os
from configparser import ConfigParser

from manager import EffectiveManager

#----------gui-----------------
import sys
from gui_ANGviewer.guiFormMainCode import guiFormMain,QtWidgets
#==============================

def get_conf(filename='config.conf'):
    parser = ConfigParser(inline_comment_prefixes="#")
    parser.read(os.path.join(os.getcwd(), filename))
    conf = {}
    try:
        for section in parser.sections():
            conf[section] = {}
            for key, val in parser.items(section):
                conf[section][key] = val
    except Exception as err:
        # logging.error(str(err))
        return
    return conf


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='(%(threadName)-10s) %(message)s', )
    logging.getLogger('matplotlib.font_manager').disabled = True


    conf = get_conf()
    manager = EffectiveManager(conf)

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
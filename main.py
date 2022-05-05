import asyncio
import os
import sys

from PyQt5.QtCore import QObject, pyqtSignal
from asyncqt import QEventLoop
from PyQt5.QtWidgets import QApplication, QWidget


import main_window

DEFINE_DEBUG_MODE = False
DEFINE_MASTER_MODE = False
DEFINE_EVENT_MODE = True

def resource_path(file_name, detail_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, file_name)
    return os.path.dirname(os.path.abspath(__file__)) + detail_path + file_name


if __name__ == '__main__':
    app = QApplication(sys.argv)
    # loop = QEventLoop(app) # QT event 루프
    # asyncio.set_event_loop(loop)

    mWindow = main_window.WindowClass()
    mWindow.show()

    # loop.run_forever()

    sys.exit(app.exec_())

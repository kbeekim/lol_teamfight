import os
import sys
from PyQt5.QtWidgets import QApplication, QWidget
import main_window


def resource_path(file_name, detail_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, file_name)
    return os.path.dirname(os.path.abspath(__file__)) + detail_path + file_name


if __name__ == '__main__':
    app = QApplication(sys.argv)

    mWindow = main_window.WindowClass()
    mWindow.show()

    sys.exit(app.exec_())

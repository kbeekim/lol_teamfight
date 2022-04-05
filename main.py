import sys
from PyQt5.QtWidgets import QApplication, QWidget
import window

if __name__ == '__main__':
    app = QApplication(sys.argv)

    mWindow = window.WindowClass()
    mWindow.show()

    sys.exit(app.exec_())

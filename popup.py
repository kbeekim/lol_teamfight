from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import QWidget, QPushButton, QMessageBox

POPUP_TYPE_OK = 0
POPUP_TYPE_OK_CANCEL = 1


class ValvePopup(QWidget):
    # Signal 선언부
    send_valve_popup_signal = pyqtSignal(bool, name='sendValvePopupSignal')

    def __init__(self, popup_type, popup_name, popup_str, parent=None):
        QWidget.__init__(self, parent)
        # self.accept_button = QPushButton()
        # self.cancel_button = QPushButton()
        self.init_ui(popup_type, popup_name, popup_str)

    def init_ui(self, popup_type, popup_name, popup_str):
        if popup_type == POPUP_TYPE_OK:
            self.show_popup_ok(popup_name, popup_str)
        elif popup_type == POPUP_TYPE_OK_CANCEL:
            self.show_popup_ok_cancel(popup_name, popup_str)

    def show_popup_ok(self, title: str, content: str):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(content)
        msg_box.setStandardButtons(QMessageBox.Ok)
        msg_box.setIcon(QMessageBox.Information)  # 메세지창 내부에 표시될 아이콘

        result = msg_box.exec_()

        if result == QMessageBox.Ok:
            self.send_valve_popup_signal.emit(True)

    def show_popup_ok_cancel(self, title: str, content: str):
        msg_box = QMessageBox()
        msg_box.setWindowTitle(title)
        msg_box.setText(content)
        msg_box.setStandardButtons(QMessageBox.Cancel | QMessageBox.Ok)

        result = msg_box.exec_()

        if result == QMessageBox.Cancel:
            self.send_valve_popup_signal.emit(False)

        elif result == QMessageBox.Ok:

            self.send_valve_popup_signal.emit(True)
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

import excel
from main import resource_path

UI_FILE_NAME = 'main_second_window.ui'

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]
excel_data = excel.ExcelClass()


class SecondWindow(QWidget, form_class):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)

        self.data_load_btn.clicked.connect(self.clicked_data_load_btn)

    def clicked_data_load_btn(self):
        print("안녕")
        excel_data.read_gspread_sheet4()

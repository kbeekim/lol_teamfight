from PyQt5 import uic
from PyQt5.QtWidgets import QWidget

import excel
from popup import ValvePopup, POPUP_TYPE_OK
from global_settings import *

UI_FILE_NAME = 'main_second_window.ui'

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]
excel_data = excel.ExcelClass()

TOP_USR_IDX = 0
TOP_CMP_IDX = 1
JUG_USR_IDX = 2
JUG_CMP_IDX = 3
MID_USR_IDX = 4
MID_CMP_IDX = 5
ADC_USR_IDX = 6
ADC_CMP_IDX = 7
SUP_USR_IDX = 8
SUP_CMP_IDX = 9


def check_position(idx):
    if idx % 10 == TOP_USR_IDX or idx % 10 == TOP_CMP_IDX:
        return "TOP"
    elif idx % 10 == JUG_USR_IDX or idx % 10 == JUG_CMP_IDX:
        return "JUG"
    elif idx % 10 == MID_USR_IDX or idx % 10 == MID_CMP_IDX:
        return "MID"
    elif idx % 10 == ADC_USR_IDX or idx % 10 == ADC_CMP_IDX:
        return "ADC"
    elif idx % 10 == SUP_USR_IDX or idx % 10 == SUP_CMP_IDX:
        return "SUP"


class SecondWindow(QWidget, form_class):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.data_load_btn.clicked.connect(self.clicked_data_load_btn)

        self.win_list = []
        self.lost_list = []

    def clicked_data_load_btn(self):
        if not excel_data.read_gspread_sheet4():
            ValvePopup(POPUP_TYPE_OK, "오류창", "엑셀 시트4 데이터 확인 필요")

        self.win_list, self.lost_list = excel_data.get_analysis_data()
    #     self.check_user_record("롤리폴리팝")
    #
    # def check_user_record(self, user_name):
    #     rate_data = []
    #
    #     for n in range(len(self.win_list)):
    #         if user_name in self.win_list[n]:
    #             usr_pos = check_position(self.win_list[n].index(user_name))
    #             print(f"{self.win_list[n]}")
    #             print(f"찾았다 {n + 1}번째 내전에서 {user_name} 포지션 {usr_pos}")
    #             if usr_pos == "SUP":



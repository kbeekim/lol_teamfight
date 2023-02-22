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

        self.record_data = []

    def clicked_data_load_btn(self):
        if not excel_data.read_gspread_sheet4():
            ValvePopup(POPUP_TYPE_OK, "오류창", "엑셀 시트4 데이터 확인 필요")

        win_list, lost_list = excel_data.get_analysis_data()

        if len(win_list) == len(lost_list):
            print("무조건 같아야지!")
            for n in range(len(win_list)):
                # print(f"{n}번째 {win_list[n]}  /  {lost_list[n]}")
                dict_d = {'TOP': [win_list[n][TOP_USR_IDX], win_list[n][TOP_CMP_IDX], lost_list[n][TOP_USR_IDX],
                                  lost_list[n][TOP_CMP_IDX]],
                          'JUG': [win_list[n][JUG_USR_IDX], win_list[n][JUG_CMP_IDX], lost_list[n][JUG_USR_IDX],
                                  lost_list[n][JUG_CMP_IDX]],
                          'MID': [win_list[n][MID_USR_IDX], win_list[n][MID_CMP_IDX], lost_list[n][MID_USR_IDX],
                                  lost_list[n][MID_CMP_IDX]],
                          'ADC': [win_list[n][ADC_USR_IDX], win_list[n][ADC_CMP_IDX], lost_list[n][ADC_USR_IDX],
                                  lost_list[n][ADC_CMP_IDX]],
                          'SUP': [win_list[n][SUP_USR_IDX], win_list[n][SUP_CMP_IDX], lost_list[n][SUP_USR_IDX],
                                  lost_list[n][SUP_CMP_IDX]],
                          }
                self.record_data.append(dict_d)

        print(len(self.record_data))

        self.check_user_record("beijingchinese")

    def check_user_record(self, user_name):
        # kb.todo usr 가 플레이한 데이터 없을시 예외처리 필요

        print(f"{user_name} 데이터 불러오기")
        user_record = []

        for n, each_data in enumerate(self.record_data):
            for pos in list(each_data.keys()):  # ['TOP', 'JUG', 'MID', 'ADC', 'SUP']:
                pos_data = each_data.get(pos)
                if user_name in pos_data:
                    if pos_data.index(user_name) == 0:  # 이김
                        user_record.append([n, pos, "WIN", pos_data[1]])
                    else:  # 졌다
                        user_record.append([n, pos, "LOSE", pos_data[3]])
                    break
        # print(user_record)

        self.calc_odds(user_record)

        return user_record

    def calc_odds(self, in_data):
        # List 형식
        # 순번,   포지션,    승/패,    챔피언
        user_odds = {'TOP': [0, 0, 0, 0.0], 'JUG': [0, 0, 0, 0.0], 'MID': [0, 0, 0, 0.0], 'ADC': [0, 0, 0, 0.0], 'SUP': [0, 0, 0, 0.0]}

        # TOP : 승 패 전 승률
        for n, dat in enumerate(in_data):
            print(dat)
            pos = dat[1]
            wl = dat[2]

            if pos == 'TOP':
                if wl == 'WIN':
                    user_odds.get('TOP')[0] += 1
                else:
                    user_odds.get('TOP')[1] += 1
            elif pos == 'JUG':
                if wl == 'WIN':
                    user_odds.get('JUG')[0] += 1
                else:
                    user_odds.get('JUG')[1] += 1
            elif pos == 'MID':
                if wl == 'WIN':
                    user_odds.get('MID')[0] += 1
                else:
                    user_odds.get('MID')[1] += 1
            elif pos == 'ADC':
                if wl == 'WIN':
                    user_odds.get('ADC')[0] += 1
                else:
                    user_odds.get('ADC')[1] += 1
            elif pos == 'SUP':
                if wl == 'WIN':
                    user_odds.get('SUP')[0] += 1
                else:
                    user_odds.get('SUP')[1] += 1

        print(f"*******************************")

        for pos in list(user_odds.keys()):  # ['TOP', 'JUG', 'MID', 'ADC', 'SUP']:
            w_cnt = user_odds.get(pos)[0]
            l_cnt = user_odds.get(pos)[1]
            total_cnt = w_cnt + l_cnt

            if total_cnt > 0:
                odds = round((w_cnt / total_cnt), 2) * 100
                user_odds.get(pos)[2] = total_cnt
                user_odds.get(pos)[3] = odds

            print(f"{pos}전적: {user_odds.get(pos)[0]}승, {user_odds.get(pos)[1]}패, {user_odds.get(pos)[2]}전, 승률: {user_odds.get(pos)[3]}%")

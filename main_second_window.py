from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtWidgets import QWidget, QTableWidgetItem
from PyQt5.uic.properties import QtGui

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

MIN_PLAY_GAMES = 5
INIT_USER1_TXT = "인력1"
INIT_USER2_TXT = "인력2"


def gen_comb(arr, n):
    result = []
    if n == 0:
        return [[]]

    for i in range(0, len(arr)):
        elem = arr[i]
        rest_arr = arr[i + 1:]

        for C in gen_comb(rest_arr, n - 1):
            result.append([elem] + C)
    return result


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
    def __init__(self, parent, excel_8_data):
        super().__init__()
        self.setupUi(self)

        self.ex8_data = excel_8_data
        self.special_worker = []
        self.record_data = []

        self.spworker_list_widget.setSelectionMode(3)

        self.combo_table.setRowCount(5)     # 출력 시, setRowCount 를 데이터 라인 수만큼 다시한다.
        self.combo_table.setColumnCount(7)

        png_img = ["download.png", "rotation.png", "clear.png", "versus.png"]
        icon_btn = [self.data_load_btn, self.user_rotation_btn, self.clear_btn, self.versus_btn]
        for idx, img in enumerate(png_img):
            qicon = QPixmap(resource_path(img, '/img/'))
            icon_btn[idx].setIcon(QIcon(qicon))
            icon_btn[idx].setIconSize(QSize(48, 48))
            if idx == 3:
                icon_btn[idx].setStyleSheet(
                    "background-color: white;"
                    "border: 1px solid white;"
                )
            else:
                icon_btn[idx].setStyleSheet(
                    "background-color: white;"
                )
        self.combo_bnt.setStyleSheet(
            "color: black;"
            "background-color: white;"
            "border: 2px solid black;"
            "border-radius: 5px;"
        )

        # 콤보 버튼 숨기기
        self.combo_bnt.hide()
        # 콤비 버튼 클릭 시
        self.combo_bnt.clicked.connect(self.clicked_show_combo_btn)
        # 특별 인력 리스트 더블 클릭 시
        self.spworker_list_widget.itemDoubleClicked.connect(self.double_clicked_spworker)
        # user01 버튼 클릭 시
        self.user01_btn.clicked.connect(partial(self.clicked_user_btn, INIT_USER1_TXT))
        # user02 버튼 클릭 시
        self.user02_btn.clicked.connect(partial(self.clicked_user_btn, INIT_USER2_TXT))
        # 데이터 로드 버튼 클릭 시
        self.data_load_btn.clicked.connect(self.clicked_data_load_btn)
        # user rotation 버튼 클릭 시
        self.user_rotation_btn.clicked.connect(self.clicked_rotation_btn)
        # clear 버튼 클릭 시
        self.clear_btn.clicked.connect(self.clicked_clear_btn)
        # versus 버튼 클릭 시 (rotation 과 동일 기능)
        self.versus_btn.clicked.connect(self.clicked_rotation_btn)

        self.user_txt = [INIT_USER1_TXT, INIT_USER2_TXT]
        self.print_user_txt()

    def is_user_btn_empty(self, btn):
        res = False
        if btn == self.user01_btn:
            if btn.text() == INIT_USER1_TXT:
                res = True
        if btn == self.user02_btn:
            if btn.text() == INIT_USER2_TXT:
                res = True
        return res

    def print_user_txt(self):
        able_next = True
        self.user01_btn.setText(self.user_txt[0])
        self.user02_btn.setText(self.user_txt[1])

        for user_btn in [self.user01_btn, self.user02_btn]:
            # setText 를 했으니 여기서는 버튼Text 확인..
            if self.is_user_btn_empty(user_btn):
                user_btn.setStyleSheet(
                    "color: black;"
                    "background-color: white;"
                    "border: 1px solid black;"
                )
                # 둘 중 하나라도 초기값이라면 준비안 된 상태
                able_next = False
            else:
                user_btn.setStyleSheet(
                    "color: black;"
                    "background-color: white;"
                    "border: 2px solid black;"
                )

        if able_next:
            self.combo_bnt.show()
        else:
            self.combo_bnt.hide()

    def double_clicked_spworker(self):
        ret = False
        # 단일 더블클릭 으로 [0] 인덱스!
        tmp_user = self.spworker_list_widget.selectedItems()[0].text()

        if self.user_txt[0] == INIT_USER1_TXT:
            self.user_txt[0] = tmp_user
            ret = True
        else:
            if self.user_txt[1] == INIT_USER2_TXT:
                self.user_txt[1] = tmp_user
                ret = True

        if ret:
            self.spworker_list_widget.selectedItems()[0].setFlags(Qt.NoItemFlags)
            self.print_user_txt()

    def clicked_user_btn(self, init_txt):
        tmp_user = None
        if init_txt == INIT_USER1_TXT:  # 1번 버튼 눌렀다!
            if self.user_txt[0] != INIT_USER1_TXT:
                tmp_user = self.user_txt[0]
                self.user_txt[0] = INIT_USER1_TXT
        elif init_txt == INIT_USER2_TXT:  # 2번 버튼 눌렀다!
            if self.user_txt[1] != INIT_USER2_TXT:
                tmp_user = self.user_txt[1]
                self.user_txt[1] = INIT_USER2_TXT
        else:
            # 이상 오류
            ValvePopup(POPUP_TYPE_OK, "오류창", "수상한 버튼을 입력했습니다.")
            return

        if tmp_user is not None:
            for idx in range(self.spworker_list_widget.count()):
                item = self.spworker_list_widget.item(idx)
                if item.text() == tmp_user:
                    item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

            self.print_user_txt()

    def clear_user_btn(self):
        if not self.is_user_btn_empty(self.user01_btn):
            self.clicked_user_btn(INIT_USER1_TXT)
        if not self.is_user_btn_empty(self.user02_btn):
            self.clicked_user_btn(INIT_USER2_TXT)

    def clicked_rotation_btn(self):
        # 서로 전환
        tmp_user = self.user_txt[0]
        self.user_txt[0] = self.user_txt[1]
        self.user_txt[1] = tmp_user

        # 초기값은 고정
        if self.user_txt[0] == INIT_USER2_TXT:
            self.user_txt[0] = INIT_USER1_TXT
        if self.user_txt[1] == INIT_USER1_TXT:
            self.user_txt[1] = INIT_USER2_TXT

        self.print_user_txt()

    def clicked_data_load_btn(self):
        # 일단 화면 초기화
        self.clicked_clear_btn()
        self.spworker_list_widget.clear()

        if not excel_data.read_gspread_sheet4():
            ValvePopup(POPUP_TYPE_OK, "오류창", "엑셀 시트4 데이터 확인 필요")
            return

        win_list, lost_list = excel_data.get_analysis_data()
        self.record_data = []

        # 5회 이상 참여한 인력 리스트
        special_worker = self.ex8_data.get_worker_name(MIN_PLAY_GAMES)
        if G_DEFINE_DEBUG_MODE:
            print(f"롤무원 등장 \n{special_worker}")

        # [{'TOP': ['이긴팀 유저 이름', '이긴팀 챔피언', '진팀 유저이름', '진팀 챔피언'] ...
        if len(win_list) == len(lost_list):
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
            ValvePopup(POPUP_TYPE_OK, "확인창", "데이터 로드 성공! (sh4.게임결과(입력))")

            for worker in special_worker:
                self.spworker_list_widget.addItem(worker)
        else:
            ValvePopup(POPUP_TYPE_OK, "확인창", "데이터가 올바르지않습니다. (sh4.게임결과(입력))")

    def clicked_clear_btn(self):
        self.combo_table.clear()
        self.comb_label.clear()
        self.user1_label.clear()
        self.user2_label.clear()
        self.clear_user_btn()

    def clicked_show_combo_btn(self):
        # 혹시 모를 예외처리들 - 데이터 확인 / 버튼 2개 확인
        if len(self.record_data) == 0:
            ValvePopup(POPUP_TYPE_OK, "확인창", "데이터 확인 바랍니다.")
        elif self.is_user_btn_empty(self.user01_btn):
            ValvePopup(POPUP_TYPE_OK, "확인창", f"{INIT_USER1_TXT} 탈주한 것으로 보입니다.")
        elif self.is_user_btn_empty(self.user02_btn):
            ValvePopup(POPUP_TYPE_OK, "확인창", f"{INIT_USER2_TXT} 탈주한 것으로 보입니다.")
        else:
            self.print_combo_data(self.user01_btn.text(), self.user02_btn.text())

    def print_combo_data(self, user1, user2):
        #    [0]       [1]     [2]       [3]       [4]       [5]       [6]
        # 내선 순번 / 1 승,패 / 2 승,패 / 1 포지션 / 1 챔피언 / 2 포지션 / 2 챔피언
        combo_data, user1_record, user2_record = self.make_combo_data(user1, user2)
        to_win_cnt = 0
        to_lose_cnt = 0
        en_win_cnt = 0
        en_lose_cnt = 0

        table_title = ["내전 순번", f"[{user1}]승/패 ", f"[{user2}]승/패",
                       f"[{user1}]포지션", f"[{user1}]챔피언", f"[{user2}]포지션", f"[{user2}]챔피언"]

        self.combo_table.setRowCount(len(combo_data) + 1)

        for cnt_n, n_data in enumerate(combo_data):
            if n_data[1] == n_data[2]:  # 같은 팀
                if n_data[1] == "WIN":  # 승리
                    to_win_cnt += 1
                else:
                    to_lose_cnt += 1
            else:  # 다른 팀
                if n_data[1] == "WIN":  # 승리
                    en_win_cnt += 1
                else:
                    en_lose_cnt += 1

            for cnt_d in range(len(n_data)):
                if cnt_n == 0:
                    self.combo_table.setItem(0, cnt_d, QTableWidgetItem(str(table_title[cnt_d])))

                self.combo_table.setItem(cnt_n + 1, cnt_d, QTableWidgetItem(str(combo_data[cnt_n][cnt_d])))

        if to_win_cnt + to_lose_cnt == 0:
            to_rate = 0
        else:
            to_rate = round(to_win_cnt / (to_win_cnt + to_lose_cnt), 4) * 100

        if en_win_cnt + en_lose_cnt == 0:
            en_rate = 0
        else:
            en_rate = round(en_win_cnt / (en_win_cnt + en_lose_cnt), 4) * 100

        res_text = ""
        res_text = (
            f"[{user1}]님과 [{user2}]님은 \n내전 총 [{len(self.record_data)}]판 중, [{len(combo_data)}]판을 같이 플레이 했습니다.\n\n"
            f"같은팀으로 총 {to_win_cnt + to_lose_cnt}판 | {to_win_cnt}승 {to_lose_cnt}패 하여 {to_rate} 승률을 기록했습니다.\n"
            f"다른팀으로 총 {en_win_cnt + en_lose_cnt}판 | {en_win_cnt}승 {en_lose_cnt}패 하여 {en_rate} 승률을 기록했습니다.")

        self.comb_label.setText(res_text)

        self.user1_label.setText(f"{user1} 님의 내전 승률\n\n" + self.calc_odds(user1_record))
        self.user2_label.setText(f"{user2} 님의 내전 승률\n\n" + self.calc_odds(user2_record))

    def make_combo_data(self, user1, user2):
        combo_data = []

        # record_data-> [[내선 IDX, 포지션, 승/패, 챔피언], ...
        user1_record = self.make_user_record(user1)
        user2_record = self.make_user_record(user2)

        if len(user1_record) == 0 or len(user2_record) == 0:
            return []

        for user1_round in user1_record:
            for user2_round in user2_record:
                if user1_round[0] == user2_round[0]:  # 같은 게임 플레이
                    combo_data.append(
                        [user1_round[0] + 1, user1_round[2], user2_round[2], user1_round[1], user1_round[3],
                         user2_round[1], user2_round[3]])

        return combo_data, user1_record, user2_record

    def make_user_record(self, user_name):
        user_record = []
        # [[내선 IDX, 포지션, 승/패, 챔피언],
        for n, each_data in enumerate(self.record_data):
            for pos in list(each_data.keys()):  # ['TOP', 'JUG', 'MID', 'ADC', 'SUP']:
                pos_data = each_data.get(pos)
                if user_name in pos_data:
                    if pos_data.index(user_name) == 0:  # 이김
                        user_record.append([n, pos, "WIN", pos_data[1]])
                    else:  # 졌다
                        user_record.append([n, pos, "LOSE", pos_data[3]])
                    break

        return user_record

    def calc_odds(self, in_user_record):
        # List 형식
        # 순번,   포지션,    승/패,    챔피언
        user_odds = {'TOP': [0, 0, 0, 0.0], 'JUG': [0, 0, 0, 0.0], 'MID': [0, 0, 0, 0.0], 'ADC': [0, 0, 0, 0.0],
                     'SUP': [0, 0, 0, 0.0]}

        # TOP : 승 패 전 승률
        for n, dat in enumerate(in_user_record):
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

        ret_text = ""
        for pos in list(user_odds.keys()):  # ['TOP', 'JUG', 'MID', 'ADC', 'SUP']:
            w_cnt = user_odds.get(pos)[0]
            l_cnt = user_odds.get(pos)[1]
            total_cnt = w_cnt + l_cnt

            if total_cnt > 0:
                odds = round((w_cnt / total_cnt), 4) * 100
                user_odds.get(pos)[2] = total_cnt
                user_odds.get(pos)[3] = odds

                ret_text += str(
                    f"{pos}전적: {user_odds.get(pos)[0]}승, {user_odds.get(pos)[1]}패, {user_odds.get(pos)[2]}전, 승률: {user_odds.get(pos)[3]}% \n")

        return ret_text

    # def test_total_combo(self):
    #     comb_cases = gen_comb(self.special_worker, 2)
    #     print(f"{len(comb_cases)} 가지 경우의 수")
    #
    #     highest_list = [None, None, 0, 0, 0]
    #     lowest_list = [None, None, 100, 0, 0]
    #
    #     for cnt, mate in enumerate(comb_cases):
    #         print(f"{cnt} 번째")
    #         tmp_rate = self.test_combo_data(mate[0], mate[1])
    #
    #         if tmp_rate == -1:
    #             continue
    #
    #         if tmp_rate[2] > highest_list[2]:
    #             highest_list[0] = mate[0]
    #             highest_list[1] = mate[1]
    #
    #             highest_list[2] = tmp_rate[2]
    #             highest_list[3] = tmp_rate[0]
    #             highest_list[4] = tmp_rate[1]
    #
    #         if lowest_list[2] > tmp_rate[2]:
    #             lowest_list[0] = mate[0]
    #             lowest_list[1] = mate[1]
    #
    #             lowest_list[2] = tmp_rate[2]
    #             lowest_list[3] = tmp_rate[0]
    #             lowest_list[4] = tmp_rate[1]
    #
    #     print(highest_list)
    #     print(lowest_list)

    # print(f"**시즌 최고의 듀오**")
    # print(f"{highest_list[0]} {highest_list[1]} : {highest_list[3]} 승, {highest_list[4]} 패 로 승률 {highest_list[2]}")
    # print(self.print_combo_data(highest_list[0], highest_list[1]))
    #
    # print(f"**시즌 최악의 듀오**")
    # print(f"{lowest_list[0]} {lowest_list[1]} : {lowest_list[3]} 승, {lowest_list[4]} 패 로 승률 {lowest_list[2]}")
    # print(self.print_combo_data(lowest_list[0], lowest_list[1]))

    # def test_combo_data(self, user1, user2):
    #     #    [0]       [1]     [2]       [3]       [4]       [5]       [6]
    #     # 내선 순번 / 1 승,패 / 2 승,패 / 1 포지션 / 1 챔피언 / 2 포지션 / 2 챔피언
    #     combo_data = self.make_combo_data(user1, user2)
    #     to_win_cnt = 0
    #     to_lose_cnt = 0
    #     ret_data = []
    #
    #     print(user1, user2)
    #     print(combo_data)
    #
    #     for cnt_n, n_data in enumerate(combo_data):
    #         if n_data[1] == n_data[2]:  # 같은 팀
    #             if n_data[1] == "WIN":  # 승리
    #                 to_win_cnt += 1
    #             else:
    #                 to_lose_cnt += 1
    #
    #     if to_win_cnt + to_lose_cnt == 0:
    #         return -1
    #
    #     if to_win_cnt == 0:
    #         to_rate = 0
    #     else:
    #         to_rate = round(to_win_cnt / (to_win_cnt + to_lose_cnt), 2) * 100
    #
    #     ret_data = [to_win_cnt, to_lose_cnt, to_rate]
    #     return ret_data

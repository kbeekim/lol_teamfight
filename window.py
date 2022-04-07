import sys
from itertools import combinations

import self as self
from PyQt5.QtCore import QCoreApplication, Qt, QEvent, QMimeData
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip, QMainWindow, QAction, qApp
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from django.conf.locale import pl

import excel
import soldier_window

#kb.todo path 설정
absolute_path = "C:/Users/YS KIM/PycharmProjects/pythonProject/"
form_class = uic.loadUiType(absolute_path + "main_window.ui")[0]
excel_data = excel.ExcelClass()

MAX_PLAYER_CNT = 10
MAX_GROUP_MEMBER = 5

TEAM_FLAG_NORMAL = 0
TEAM_FLAG_GROUP = 1
TEAM_FLAG_DIVISION = 2

PLAYER_BTN_DEFAULT = 0
PLAYER_BTN_NORMAL = 1
PLAYER_BTN_GROUP = 2
PLAYER_BTN_DIVISION = 3
PLAYER_BTN_SOLDIER = 4

PLAYER_INFO_ERROR_WRONG_IDX = -1
PLAYER_INFO_ERROR_INFO_IS_EMPTY = -2
PLAYER_INFO_ERROR_FULL_PLAYER = -3

STATUS_BAR_TIMEOUT_DEFAULT = 2000
STATUS_BAR_TYPE_NORMAL = 0
STATUS_BAR_TYPE_WARN =  1


class PlayerInfoClass():
    def __init__(self):
        self.player_info = [None] * MAX_PLAYER_CNT
        self.player_cnt = 0

    def set_player_info(self, idx, info):
        if not 0 <= idx < MAX_PLAYER_CNT:
            return PLAYER_INFO_ERROR_WRONG_IDX
        elif self.player_cnt >= MAX_PLAYER_CNT:
            return PLAYER_INFO_ERROR_FULL_PLAYER

        self.player_info[idx] = info
        self.player_cnt += 1

    def get_player_info(self, idx):
        if not 0 <= idx < MAX_PLAYER_CNT:
            return PLAYER_INFO_ERROR_WRONG_IDX
        elif self.player_info[idx] is None:
            return PLAYER_INFO_ERROR_INFO_IS_EMPTY
        return self.player_info[idx]

    def clear_player_info(self, idx):
        if not 0 <= idx < MAX_PLAYER_CNT:
            return PLAYER_INFO_ERROR_WRONG_IDX

        self.player_info[idx] = None
        if not self.player_cnt == 0:
            self.player_cnt -= 1

    # 이미 선택되어 있는지 확인하는 함수
    def is_player_already_in(self, in_text):
        # worker_info 와 연계 kb.todo
        for idx in range(len(self.player_info)):
            if self.player_info[idx] is not None:   # 위험! None 이면..
                if self.player_info[idx][1] == in_text:
                    return True
        return False

    def get_player_cnt(self):
        return self.player_cnt

    # 해당 idx 에 해당하는 참가자 정보가 비어있는지 확인한다.
    def is_empty_player_info(self, idx):
        if self.player_info[idx] is not None:
            return False
        else:
            return True

    # 참가자가 모두 찼는지 확인한다.
    def is_full_player_info(self):
        for i in self.player_info:
            if i is None:
                return False
        return True


class WindowClass(QMainWindow, form_class):
    SOLDIER_INFO_SUCCESS = 0
    SOLDIER_INFO_ERROR_FULL_PLAYER = 1
    SOLDIER_INFO_ERROR_SAME_NAME = 2

    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("롤 인력시장 기록소")

        # 10명의 참가자 정보 List
        self.pl = PlayerInfoClass()
        self.player_btn_list = [None] * MAX_PLAYER_CNT

        # self.selected_worker = []         # listWidget 에 disable 된 item(worker) 을 다시 원복 해주기 위해 ..

        # 인력 목록
        # SelectionMode = 0 = > NoSelection        # SelectionMode = 1 = > SingleSelection
        # SelectionMode = 2 = > MultiSelection     # SelectionMode = 3 = > ExtendedSelection
        # SelectionMode = 4 = > ContiguousSelection
        self.worker_list_widget.setSelectionMode(3)
        self.nick_list = excel_data.get_worker_nickname()
        for nl in self.nick_list:
            self.worker_list_widget.addItem(str(nl))

        # 10명 GridLayout 안 player 버튼
        for x in range(5):
            for y in range(2):
                turn = (2 * x) + y
                self.player_btn_list[turn] = (QPushButton(str(turn + 1)))
                self.set_style_player_btn(turn, PLAYER_BTN_DEFAULT)

                self.player_btn_list[turn].setMaximumHeight(70)  # 버튼 높이 강제 조절
                self.player_btn_list[turn].setFont(QFont("Noto_Sans", 15))  # 폰트,크기 조절

                # 버튼의 idx를 알기위해 ObjectName으로 정함
                self.player_btn_list[turn].setObjectName(str(turn))
                # player 버튼
                self.player_btn_list[turn].clicked.connect(self.clicked_player_btn)
                self.gridLayout.addWidget(self.player_btn_list[turn], x, y)

        # 초기화 버튼
        self.clear_btn.clicked.connect(self.clicked_clear_btn)
        self.clear_btn.setStyleSheet(
            "color: black;"
            "background-color: white;"
            "border: 1px solid white;"
        )
        # 투입 버튼
        self.insert_worker_btn.clicked.connect(self.clicked_insert_worker_btn)
        # 그룹 투입 버튼
        self.insert_group_btn.clicked.connect(self.clicked_insert_group_btn)
        # 분할 투입 버튼
        self.insert_division_btn.clicked.connect(self.clicked_insert_division_btn)
        # 용병 추가 버튼
        self.insert_soldier_btn.clicked.connect(self.clicked_insert_soldier_btn)
        self.soldier = None
        # 인력 리스트 더블 클릭 시
        self.worker_list_widget.itemDoubleClicked.connect(self.double_clicked_worker)
        # 검색 엔진
        self.search_edit.textChanged.connect(self.search_worker_filter)
        self.search_edit.setPlaceholderText("인력 검색")
        # 비우기 버튼
        self.search_clear_btn.clicked.connect(self.clicked_search_clear_btn)

        # 출발 (팀짜기) 버튼
        self.make_team_btn.setStyleSheet(
            "color: black;"
            "background-color: white;"
            "border: 2px solid rgb(255, 0, 110);"
            "border-radius: 5px;"
        )
        self.make_team_btn.hide()
        self.make_team_btn.clicked.connect(self.clicked_make_team_btn)

        # ( x / 10 ) label
        self.refresh_player_cnt()

        # 상태바
        self.statusBar().setFont(QFont("Noto_Sans", 12))

    def clicked_search_clear_btn(self):
        self.search_edit.setText("")

    def refresh_player_cnt(self):
        cnt = self.pl.get_player_cnt()
        self.player_cnt_label.setText(str(cnt) + "/" + str(MAX_PLAYER_CNT))

        if cnt == MAX_PLAYER_CNT - 1:
            self.show_message("환호와 박수가 대기 중입니다. (9/10)", STATUS_BAR_TYPE_NORMAL)

        if cnt == MAX_PLAYER_CNT:
            self.make_team_btn.show()
        elif self.make_team_btn.isEnabled():
            self.make_team_btn.hide()

    def double_clicked_worker(self):
        self.clicked_insert_worker_btn()

    def search_worker_filter(self, filter_text):
        self.worker_list_widget.clear()

        for nl in self.nick_list:
            # kbeekim) 대소문자 구분 없이 검색하도록 한다.
            if filter_text.casefold() in nl.casefold():
                self.worker_list_widget.addItem(nl)

        self.refresh_worker_list()

    #kb.todo
    def clicked_make_team_btn(self):
        if not self.pl.get_player_cnt() == MAX_PLAYER_CNT:
            self.show_message("모든 정원이 차지 않았습니다.", STATUS_BAR_TYPE_WARN)
            return

    def clicked_insert_soldier_btn(self):
        if self.pl.get_player_cnt() == MAX_PLAYER_CNT:
            self.show_message("더 이상 들어갈 자리가 없어보입니다.", STATUS_BAR_TYPE_WARN)
            return
        if not self.soldier:
            self.soldier = soldier_window.SoldierWindow(self)

        self.soldier.show()

    def clicked_clear_btn(self):
        for idx in range(MAX_PLAYER_CNT):
            self.player_btn_list[idx].setText(str(idx + 1))
            self.pl.clear_player_info(idx)
            self.set_style_player_btn(idx, PLAYER_BTN_DEFAULT)

        self.refresh_player_cnt()

        self.search_edit.setText("")
        self.refresh_worker_list()

    def clicked_player_btn(self):
        player_btn = self.sender()
        btn_idx = int(player_btn.objectName())

        # 해당 idx 에 해당하는 player_info 존재한다면 btn text 변환 및 list 초기화
        if not self.pl.is_empty_player_info(btn_idx):
            self.pl.clear_player_info(btn_idx)
            player_btn.setText(str(btn_idx + 1))
            self.set_style_player_btn(btn_idx, PLAYER_BTN_DEFAULT)
            self.refresh_player_cnt()

            self.refresh_worker_list()

    def clicked_insert_worker_btn(self):
        self.insert_worker_to_player(self.worker_list_widget.selectedItems(), TEAM_FLAG_NORMAL)

    def clicked_insert_group_btn(self):
        self.insert_worker_to_player(self.worker_list_widget.selectedItems(), TEAM_FLAG_GROUP)

    def clicked_insert_division_btn(self):
        self.insert_worker_to_player(self.worker_list_widget.selectedItems(), TEAM_FLAG_DIVISION)
        return

    def insert_worker_to_player(self, workers, team_flag):
        if len(workers) == 0:
            self.show_message("인력 선택이 안되어있습니다.", STATUS_BAR_TYPE_WARN)
            return
        elif not self.pl.get_player_cnt() + len(workers) <= MAX_PLAYER_CNT:
            self.show_message("이대로 가다간 배가 침몰할 거 깉이요!   (10명 정원 초과)", STATUS_BAR_TYPE_WARN)
            return

        if team_flag == TEAM_FLAG_GROUP:
            if len(workers) < 2:
                self.show_message("그룹이라면 적어도 두 명은 선택하셔야죠!", STATUS_BAR_TYPE_WARN)
                return
            elif len(workers) > MAX_GROUP_MEMBER:
                self.show_message("한 팀에 최대 5명 입니다!", STATUS_BAR_TYPE_WARN)
                return
        if team_flag == TEAM_FLAG_DIVISION:
            if len(workers) == 1:
                self.show_message("나 자신과의 싸움은 나중으로 미루죠   (2명 선택)", STATUS_BAR_TYPE_WARN)
                return
            if len(workers) > 2:
                self.show_message("적을 많이 만들어서 좋을 건 없죠   (2명 선택)", STATUS_BAR_TYPE_WARN)
                return

        for i in range(len(workers)):
            worker_name = workers[i].text()
            workers[i].setFlags(Qt.NoItemFlags)

            # print("[kb.test] 추가 인력:  " + worker_name)
            for idx in range(MAX_PLAYER_CNT):
                if self.pl.is_empty_player_info(idx):
                    self.pl.set_player_info(idx, excel_data.get_worker_info_by_nickname(worker_name))
                    self.player_btn_list[idx].setText(worker_name)

                    if team_flag == TEAM_FLAG_NORMAL:
                        self.set_style_player_btn(idx, PLAYER_BTN_NORMAL)
                    if team_flag == TEAM_FLAG_GROUP:
                        self.set_style_player_btn(idx, PLAYER_BTN_GROUP)
                    if team_flag == TEAM_FLAG_DIVISION:
                        self.set_style_player_btn(idx, PLAYER_BTN_DIVISION)
                    break

        self.refresh_player_cnt()

    def set_style_player_btn(self, btn_idx, color):
        if color == PLAYER_BTN_NORMAL:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 2px solid black;"
            )
        elif color == PLAYER_BTN_GROUP:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 2px solid rgb(58, 134, 255);"
            )
        elif color == PLAYER_BTN_DIVISION:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 2px solid rgb(251, 86, 7);"
            )
        elif color == PLAYER_BTN_SOLDIER:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 2px solid rgb(0, 120, 62);"
            )
        else:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 1px solid black;"
            )

    # kb.todo] worker_info 이 유동적으로 바뀔 수 있도록 수정해야함 (연계)
    # kb.todo] soldier_info 안에 nickname mmr 있어서 꺼내써도되는데.. 일단은..
    def insert_soldier_to_player(self, soldier_nick, tier, soldier_info):
        if self.pl.get_player_cnt() == MAX_PLAYER_CNT:
            return self.SOLDIER_INFO_ERROR_FULL_PLAYER
        if self.pl.is_player_already_in(soldier_nick):
            return self.SOLDIER_INFO_ERROR_SAME_NAME

        for idx in range(MAX_PLAYER_CNT):
            if self.pl.is_empty_player_info(idx):
                self.pl.set_player_info(idx, soldier_info)
                tmp = f'{soldier_nick}\n({tier})'
                self.player_btn_list[idx].setText(soldier_nick+"\n("+"다이아"+")")
                self.player_btn_list[idx].setText(tmp)

                self.set_style_player_btn(idx, PLAYER_BTN_SOLDIER)
                break
        self.refresh_player_cnt()
        return self.SOLDIER_INFO_SUCCESS

    def refresh_worker_list(self):
        """ worker_list_widget 의 Flag (활성/비활성화) 를 갱신하는 함수
          - worker_list_widget 안 items 들의 닉네임과 player_list 를 비교하여
          - 이미 등록된 player 의 경우 Flag 를 비활성화한다.
          - worker_list_widget 이 변경되거나 player_list 가 변경될 때 호출해주면 된다.
        Args:
            -
        Returns:
            -
        """
        for idx in range(self.worker_list_widget.count()):
            item = self.worker_list_widget.item(idx)

            if self.pl.is_player_already_in(item.text()):
                item.setFlags(Qt.NoItemFlags)
            else:
                item.setFlags(Qt.ItemIsEnabled |
                                      Qt.ItemIsSelectable)

    def show_message(self, msg, msg_type):
        if msg_type == STATUS_BAR_TYPE_NORMAL:
            self.statusBar().setStyleSheet(
                "color: black;"
            )
            self.statusBar().showMessage(msg, STATUS_BAR_TIMEOUT_DEFAULT)
        elif msg_type == STATUS_BAR_TYPE_WARN:
            self.statusBar().setStyleSheet(
                "color: red;"
            )
            self.statusBar().showMessage(msg, STATUS_BAR_TIMEOUT_DEFAULT)

import sys
from itertools import combinations

from PyQt5.QtCore import QCoreApplication, Qt, QEvent, QMimeData
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QToolTip, QMainWindow, QAction, qApp
from PyQt5 import uic, QtWidgets
from PyQt5.QtWidgets import *
from django.conf.locale import pl

import excel
#kb.todo path 설정
import soldier_window

absolute_path = "C:/Users/YS KIM/PycharmProjects/pythonProject/"
form_class = uic.loadUiType(absolute_path + "untitled.ui")[0]
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
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("롤 인력시장 기록소")

        # 10명의 참가자 정보 List
        self.pl = PlayerInfoClass()
        self.player_btn_list = [None] * MAX_PLAYER_CNT
        self.selected_worker = []         # listWidget 에 disable 된 item(worker) 을 다시 원복 해주기 위해 ..

        # 인력 목록
        # SelectionMode = 0 = > NoSelection        # SelectionMode = 1 = > SingleSelection
        # SelectionMode = 2 = > MultiSelection     # SelectionMode = 3 = > ExtendedSelection
        # SelectionMode = 4 = > ContiguousSelection
        self.worker_list_widget.setSelectionMode(3)
        nick_list = excel_data.get_worker_nickname()
        for nl in nick_list:
            self.worker_list_widget.addItem(str(nl))

        # 10명 GridLayout 안 player 버튼
        for x in range(5):
            for y in range(2):
                turn = (2 * x) + y
                self.player_btn_list[turn] = (QPushButton(str(turn + 1)))
                self.color_player_btn(turn, PLAYER_BTN_DEFAULT)

                self.player_btn_list[turn].setMaximumHeight(60)  # 버튼 높이 강제 조절
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

        # # 검색 버튼
        # self.searchUserEdit.returnPressed.connect(self.clicked_search_worker)

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

    def refresh_player_cnt(self):
        cnt = self.pl.get_player_cnt()
        self.player_cnt_label.setText(str(cnt) + "/" + str(MAX_PLAYER_CNT))
        if cnt == MAX_PLAYER_CNT:
            self.make_team_btn.show()
        elif self.make_team_btn.isEnabled():
            self.make_team_btn.hide()

    def double_clicked_worker(self):
        self.clicked_insert_worker_btn()

    #kb.todo
    def clicked_make_team_btn(self):
        if not self.pl.get_player_cnt() == MAX_PLAYER_CNT:
            print("모든 정원이 차지 않았습니다. ㄱㄱ?")
            return

    # kb.todo
    def clicked_insert_soldier_btn(self):
        if self.pl.get_player_cnt() == MAX_PLAYER_CNT:
            print("더 이상 들어갈 자리가 없어보입니다.")
            return
        if not self.soldier:
            self.soldier = soldier_window.SoldierWindow(self)

        self.soldier.show()

    def clicked_clear_btn(self):
        for idx in range(MAX_PLAYER_CNT):
            self.player_btn_list[idx].setText(str(idx + 1))
            self.pl.clear_player_info(idx)
            self.color_player_btn(idx, PLAYER_BTN_DEFAULT)

        self.refresh_player_cnt()

        items = self.selected_worker
        for i in range(len(items)):
            items[i].setFlags(Qt.ItemIsEnabled |
                              Qt.ItemIsSelectable)
        self.selected_worker.clear()

    def clicked_player_btn(self):
        player_btn = self.sender()
        btn_idx = int(player_btn.objectName())
        player_nick = player_btn.text()
        selected_worker_idx = -1

        # 해당 idx 에 해당하는 player_info 존재한다면 btn text 변환 및 list 초기화
        if not self.pl.is_empty_player_info(btn_idx):
            self.pl.clear_player_info(btn_idx)
            player_btn.setText(str(btn_idx + 1))
            self.color_player_btn(btn_idx, PLAYER_BTN_DEFAULT)
            self.refresh_player_cnt()

            items = self.selected_worker
            for i in range(len(items)):
                if items[i].text() == player_nick:
                    items[i].setFlags(Qt.ItemIsEnabled |
                                      Qt.ItemIsSelectable)
                    del self.selected_worker[i]
                    break

    def clicked_insert_worker_btn(self):
        self.insert_worker_to_player(self.worker_list_widget.selectedItems(), TEAM_FLAG_NORMAL)

    def clicked_insert_group_btn(self):
        self.insert_worker_to_player(self.worker_list_widget.selectedItems(), TEAM_FLAG_GROUP)

    def clicked_insert_division_btn(self):
        self.insert_worker_to_player(self.worker_list_widget.selectedItems(), TEAM_FLAG_DIVISION)
        return

    def insert_worker_to_player(self, workers, team_flag):
        if len(workers) == 0:
            print("실패 : 인력 선택을 안했습니다.")
            return
        elif not self.pl.get_player_cnt() + len(workers) <= MAX_PLAYER_CNT:
            print("실패 : 이대로 가다간 배가 침몰할 수 있어요!")
            return

        if team_flag == TEAM_FLAG_GROUP:
            if len(workers) < 2:
                print("실패 : 적어도 두 명은 선택하셔야죠!")
                return
            elif len(workers) > MAX_GROUP_MEMBER:
                print("실패 : 한 팀에 최대 5명 입니다!")
                return
        if team_flag == TEAM_FLAG_DIVISION:
            if not len(workers) == 2:
                print("실패 : 적 수는 오직 2명 입니다.")
                return

        for i in range(len(workers)):
            worker_name = workers[i].text()
            workers[i].setFlags(Qt.NoItemFlags)

            self.selected_worker.append(workers[i])

            print("[kb.test] 추가 인력:  " + worker_name)
            for idx in range(MAX_PLAYER_CNT):
                if self.pl.is_empty_player_info(idx):
                    self.pl.set_player_info(idx, excel_data.get_worker_info_by_nickname(worker_name))
                    self.player_btn_list[idx].setText(worker_name)

                    if team_flag == TEAM_FLAG_NORMAL:
                        self.color_player_btn(idx, PLAYER_BTN_NORMAL)
                    if team_flag == TEAM_FLAG_GROUP:
                        self.color_player_btn(idx, PLAYER_BTN_GROUP)
                    if team_flag == TEAM_FLAG_DIVISION:
                        self.color_player_btn(idx, PLAYER_BTN_DIVISION)

                    break

        self.refresh_player_cnt()

    def color_player_btn(self, btn_idx, color):
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

    # kb.todo worker_info 이 유동적으로 바뀔 수 있도록 수정해야함
    def insert_soldier_to_player(self, soldier_nick, soldier_info):
        if self.pl.get_player_cnt() == MAX_PLAYER_CNT:
            print("실패 : 이대로 가다간 배가 침몰할 수 있어요!")
            return
        for idx in range(MAX_PLAYER_CNT):
            if self.pl.is_empty_player_info(idx):
                #kb.todo
                self.pl.set_player_info(idx, soldier_info)
                self.player_btn_list[idx].setText(soldier_nick)
                self.color_player_btn(idx, PLAYER_BTN_SOLDIER)
                break
        self.refresh_player_cnt()

    def show_message(self, msg):
        self.statusBar().showMessage(msg, 1000)

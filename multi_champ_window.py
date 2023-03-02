from functools import partial

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QCompleter, QTextEdit, QPushButton, QHBoxLayout, QLabel

import excel
from global_settings import *

UI_FILE_NAME = 'multi_champ_window.ui'
MAX_BTN_CNT = 10

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]
excel_data = excel.ExcelClass()


class MultiChampWindow(QWidget, form_class):
    def __init__(self, input_btn_list):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("챔피언 다중 입력")
        # windowModality 설정을 NonModal -> ApplicationModal 으로 설정하여 해당 창을 종료 전까지 다른 창 사용 못하게 설정
        self.setWindowModality(Qt.ApplicationModal)

        self.champ_list = G_CHAMPION
        self.champ_chosung_list = G_CHAMPION_CHOSUNG
        self.champ_eng_list = G_CHAMPION_ENG
        self.champ_else_list = G_CHAMPION_ELSE

        # 챔피언 목록
        # SelectionMode = 0 = > NoSelection        # SelectionMode = 1 = > SingleSelection
        # SelectionMode = 2 = > MultiSelection     # SelectionMode = 3 = > ExtendedSelection
        # SelectionMode = 4 = > ContiguousSelection
        self.champ_list_widget.setSelectionMode(1)

        # 챔피언 리스트 채우기
        self.load_champ_list()

        # 검색 엔진
        self.search_champ_edit.textChanged.connect(self.search_champ_filter)
        self.search_champ_edit.setPlaceholderText("챔피언 검색")
        self.search_champ_edit.setFocus()

        # 예외처리 확인
        if len(input_btn_list) == MAX_BTN_CNT:
            self.input_btn_list = input_btn_list
            self.btn_list = [None] * MAX_BTN_CNT
            self.label = [None] * MAX_BTN_CNT
        else:
            # kb.todo
            print("오류")
            return

        # 10버튼 생성 (5*2 배열)
        for idx in range(5):
            h_btn_layout = QHBoxLayout()
            for n in range(2):
                turn = (idx * 2) + n
                self.btn_list[turn] = (QPushButton())
                self.btn_list[turn].setMaximumHeight(50)  # 버튼 높이 강제 조절
                self.btn_list[turn].setFont(QFont(G_FONT, 13))  # 폰트,크기 조절

                h_btn_layout.addWidget(self.btn_list[turn])
            self.teamABLayout.addLayout(h_btn_layout)

        # 10버튼 문구 초기화 및 클릭 시 이벤트 등록
        self.init_10btn()

        # 챔피언 리스트 더블 클릭 시
        self.champ_list_widget.itemDoubleClicked.connect(self.double_clicked_champ)
        # Ok 버튼 클릭 시
        self.champ_ok_btn.clicked.connect(self.clicked_ok_btn)
        # 비우기 버튼 클릭 시
        self.champ_clear_btn.clicked.connect(self.clicked_champ_clear_btn)

        if G_DEFINE_DEBUG_MODE:
            print("================MultiChampWindow===================")
            # for cmp in range(len(G_CHAMPION_CLICKED)):
            #     if G_CHAMPION_CLICKED[cmp] is True:
            #         print(f"클릭된 챔프: {G_CHAMPION[cmp]}")

    def init_10btn(self):
        # [A-Top, B-Top, A-JUG, B-JUG, A-MID, B-MID, A-ADC, B-ADC, A-SUP, B-SUP]
        for idx in range(len(self.input_btn_list)):
            self.btn_list[idx].setText(self.input_btn_list[idx].text())
            # 10버튼 클릭 시
            self.btn_list[idx].clicked.connect(partial(self.clicked_10btn, idx))

    def clicked_10btn(self, btn_idx):
        btn_text = self.btn_list[btn_idx].text()
        champ_idx = self.find_idx_champ(btn_text)

        # 챔피언 등록 되어있다면 해지
        if champ_idx is not None:
            G_CHAMPION_CLICKED[champ_idx] = False

            self.btn_list[btn_idx].setText(G_INIT_CHAMP_TXT)
            self.input_btn_list[btn_idx].setText(G_INIT_CHAMP_TXT)
            self.refresh_champ_list()

    def load_champ_list(self):
        self.champ_list_widget.clear()

        for idx, cl in enumerate(self.champ_list):
            self.champ_list_widget.addItem(str(cl))
            if G_CHAMPION_CLICKED[idx]:
                self.champ_list_widget.item(idx).setFlags(Qt.NoItemFlags)

    def search_champ_filter(self, filter_text):
        self.champ_list_widget.clear()

        for idx, cl in enumerate(self.champ_list):
            if filter_text in cl or filter_text in self.champ_chosung_list[idx] \
                    or filter_text in self.champ_eng_list[idx] or filter_text in self.champ_else_list[idx]:
                self.champ_list_widget.addItem(cl)

        self.refresh_champ_list()

    def double_clicked_champ(self):
        target_btn_idx = self.find_able_btn()

        if target_btn_idx is not None:
            G_CHAMPION_CLICKED[self.find_idx_champ(self.champ_list_widget.selectedItems()[0].text())] = True
            champ_str = self.champ_list_widget.selectedItems()[0].text()

            self.btn_list[target_btn_idx].setText(champ_str)
            self.input_btn_list[target_btn_idx].setText(champ_str)

            self.refresh_champ_list()

    def clicked_ok_btn(self):
        self.close()

    def clicked_champ_clear_btn(self):
        self.search_champ_edit.setText("")

    def refresh_champ_list(self):
        for idx in range(self.champ_list_widget.count()):
            item = self.champ_list_widget.item(idx)

            if G_CHAMPION_CLICKED[self.find_idx_champ(item.text())]:
                item.setFlags(Qt.NoItemFlags)
            else:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def find_idx_champ(self, champ_name):
        ret = None

        for champ_idx, cl in enumerate(self.champ_list):
            if champ_name == cl:
                ret = champ_idx
                break
        return ret

    def find_able_btn(self):
        ret = None

        for idx in range(len(self.btn_list)):  # 10
            if self.btn_list[idx].text() == G_INIT_CHAMP_TXT:
                ret = idx
                break
        return ret

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QLineEdit, QVBoxLayout, QCompleter, QTextEdit

import excel
from global_settings import *

UI_FILE_NAME = 'champ_window.ui'

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]
excel_data = excel.ExcelClass()


class ChampWindow(QWidget, form_class):
    def __init__(self, btn):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("챔피언 입력")
        # windowModality 설정을 NonModal -> ApplicationModal 으로 설정하여 해당 창을 종료 전까지 다른 창 사용 못하게 설정
        self.setWindowModality(Qt.ApplicationModal)

        self.out_btn = btn
        self.champ_list = G_CHAMPION
        self.champ_chosung_list = G_CHAMPION_CHOSUNG
        self.champ_eng_list = G_CHAMPION_ENG
        self.champ_else_list = G_CHAMPION_ELSE

        self.load_champ_list()

        # 검색 엔진
        self.search_champ_edit.textChanged.connect(self.search_champ_filter)
        self.search_champ_edit.setPlaceholderText("챔피언 검색")
        self.search_champ_edit.setFocus()

        # 챔피언 목록
        # SelectionMode = 0 = > NoSelection        # SelectionMode = 1 = > SingleSelection
        # SelectionMode = 2 = > MultiSelection     # SelectionMode = 3 = > ExtendedSelection
        # SelectionMode = 4 = > ContiguousSelection
        self.champ_list_widget.setSelectionMode(1)

        # 챔피언 리스트 더블 클릭 시
        self.champ_list_widget.itemDoubleClicked.connect(self.double_clicked_champ)

        self.champ_ok_btn.clicked.connect(self.clicked_ok_btn)

        if G_DEFINE_DEBUG_MODE:
            print("===================================")
            for cmp in range(len(G_CHAMPION_CLICKED)):
                if G_CHAMPION_CLICKED[cmp] is True:
                    print(f"클릭된 챔프: {G_CHAMPION[cmp]}")

    def search_champ_filter(self, filter_text):
        self.champ_list_widget.clear()
        print(filter_text)
        for idx, cl in enumerate(self.champ_list):
            if filter_text in cl or filter_text in self.champ_chosung_list[idx] \
                    or filter_text in self.champ_eng_list[idx] or filter_text in self.champ_else_list[idx]:
                self.champ_list_widget.addItem(cl)

        self.refresh_champ_list()

    def load_champ_list(self):
        self.champ_list_widget.clear()

        init_text = self.out_btn.text()
        init_idx = None

        for idx, cl in enumerate(self.champ_list):
            self.champ_list_widget.addItem(str(cl))
            if G_CHAMPION_CLICKED[idx]:
                self.champ_list_widget.item(idx).setFlags(Qt.NoItemFlags)
            if init_text == cl:
                init_idx = idx

        if init_idx is not None:
            self.champ_list_widget.item(init_idx).setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            G_CHAMPION_CLICKED[init_idx] = False

    def double_clicked_champ(self):
        G_CHAMPION_CLICKED[self.find_idx_champ(self.champ_list_widget.selectedItems()[0].text())] = True

        champ_str = self.champ_list_widget.selectedItems()[0].text()
        self.out_btn.setText(champ_str)
        self.close()

    def clicked_ok_btn(self):
        if len(self.champ_list_widget.selectedItems()) != 1:
            print("이상해요")
            return

        G_CHAMPION_CLICKED[self.find_idx_champ(self.champ_list_widget.selectedItems()[0].text())] = True

        champ_str = self.champ_list_widget.selectedItems()[0].text()
        self.out_btn.setText(champ_str)
        self.close()

    def refresh_champ_list(self):
        for idx in range(self.champ_list_widget.count()):
            item = self.champ_list_widget.item(idx)

            if G_CHAMPION_CLICKED[self.find_idx_champ(item.text())]:
                item.setFlags(Qt.NoItemFlags)
            else:
                item.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)

    def find_idx_champ(self, champ_name):
        for champ_idx, cl in enumerate(self.champ_list):
            if champ_name == cl:
                return champ_idx

    # def check_typo_sheet4_champ(self):
    #     check_champ, check_champ2 = self.ex.read_gspread_sheet4()
    #     print("***챔피언 오타 검사기***")
    #
    #     for idx, n in enumerate(check_champ):
    #         if n in G_CHAMPION or n in G_SHEET4_EXCEPT_STR:
    #             continue
    #         else:
    #             print(f"오타 발견! (파랑) : {n} {idx}행")
    #
    #     for idx, n in enumerate(check_champ2):
    #         if n in G_CHAMPION or n in G_SHEET4_EXCEPT_STR:
    #             continue
    #         else:
    #             print(f"오타 발견! (빨강) : {n} {idx}행")

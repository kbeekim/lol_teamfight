from PyQt5 import uic
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtWidgets import QDialog, QPushButton
from PyQt5.QtGui import QDragEnterEvent, QDrag
from PyQt5.QtGui import QDropEvent

from main import resource_path
from main import DEFINE_DEBUG_MODE

UI_FILE_NAME = 'team_window.ui'

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]


class DragButton(QPushButton):

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)


class TeamWindow(QDialog, form_class):
    def __init__(self, team_info, player_info, str_before):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("팀 결과")
        self.setAcceptDrops(True)
        # self.setWindowIcon(QIcon(BASE_DIR + '/img/team.png'))

        # windowModality 설정을 NonModal -> ApplicationModal 으로 설정하여 해당 창을 종료 전까지 다른 창 사용 못하게 설정
        self.setWindowModality(Qt.ApplicationModal)

        self.team_info = team_info
        self.player_info = player_info
        self.str_before = str_before

        self.set_text_ui()
        self.ok_btn.clicked.connect(self.clicked_ok_btn)

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        TEAM_A = 0
        TEAM_B = 1
        pos = e.pos()
        src_w = e.source()
        team = None

        for n in range(self.teamALayout.count()):
            if self.teamALayout.itemAt(n).widget() == src_w:
                team = TEAM_A
                src_n = n
                break
            if self.teamBLayout.itemAt(n).widget() == src_w:
                team = TEAM_B
                src_n = n
                break

        if team == TEAM_A:
            if pos.x() <= 289 and pos.y() <= 316:
                for n in range(self.teamALayout.count()):
                    w = self.teamALayout.itemAt(n).widget()
                    # print("w.y() + w.size().height() :  " + str(w.y() + w.size().height()))
                    if pos.y() <= w.y() + w.size().height():
                        self.teamALayout.insertWidget(n, src_w)
                        self.teamALayout.insertWidget(src_n, w)
                        break
            else:
                print("wrong drop position -A")

        elif team == TEAM_B:
            if 363 <= pos.x() <= 649 and pos.y() <= 316:
                for n in range(self.teamBLayout.count()):
                    w = self.teamBLayout.itemAt(n).widget()
                    # print("w.y() + w.size().height() :  " + str(w.y() + w.size().height()))
                    if pos.y() <= w.y() + w.size().height():
                        self.teamBLayout.insertWidget(n, src_w)
                        self.teamBLayout.insertWidget(src_n, w)
                        break
            else:
                print("wrong drop position -B")
        else:
            print("Unknown Widget")

        # if DEFINE_DEBUG_MODE:
            # print(f'pos x, y : {pos.x()}, {pos.y()}')

        e.accept()

    def set_text_ui(self):
        teamA_list = self.team_info[0]
        teamA_mmr = round(self.team_info[1] / 5, 1)
        teamB_list = self.team_info[2]
        teamB_mmr = round(self.team_info[3] / 5, 1)

        # kb.todo 뒷 배경도 검정색으로..?

        line_list = ['TOP', 'JUG', 'MID', 'BOT', 'SUP']
        for idx, btn in enumerate(line_list):
            btn = DragButton(btn)
            btn.setMaximumHeight(56)  # 버튼 높이 강제 조절
            btn.setText(self.get_nickname(teamA_list[idx]) + "\n(" + str(self.get_mmr(teamA_list[idx])) + ")")
            btn.setStyleSheet(
                "color: white;"
                "background-color: black;"
            )
            self.teamALayout.addWidget(btn)

        for idx, btn in enumerate(line_list):
            btn = DragButton(btn)
            btn.setMaximumHeight(56)  # 버튼 높이 강제 조절
            btn.setText(self.get_nickname(teamB_list[idx]) + "\n(" + str(self.get_mmr(teamB_list[idx])) + ")")
            btn.setStyleSheet(
                "color: white;"
                "background-color: black;"
            )
            self.teamBLayout.addWidget(btn)

        log_str = "\n>>> 새로운 방식 (After)\n"
        if DEFINE_DEBUG_MODE:
            print(f"1팀: 합계 [{self.team_info[1]}]")
            log_str += f"1팀: 합계 [{self.team_info[1]}]\n"

            for i in teamA_list:
                print(f"[{self.get_short_nick(i)}] / {str(self.get_mmr(i))}")
                log_str += f"[{self.get_short_nick(i)}] / {str(self.get_mmr(i))}\n"

            print(f"\n2팀: 합계 [{self.team_info[3]}]")
            log_str += f"\n2팀: 합계 [{self.team_info[3]}]\n"

            for i in teamB_list:
                print(f"[{self.get_short_nick(i)}] / {str(self.get_mmr(i))}")
                log_str += f"[{self.get_short_nick(i)}] / {str(self.get_mmr(i))}\n"

            print(
                f"두 팀 차이: 합계[{round(abs(self.team_info[3] - self.team_info[1]), 1)}] \n")
            log_str += f"* 두 팀 차이: 합계[{round(abs(self.team_info[3] - self.team_info[1]), 1)}]\n"

            self.log_edit.setText(self.str_before + log_str)

        str_1 = f"1팀: {self.get_short_nick(teamA_list[0])} {self.get_short_nick(teamA_list[1])} " \
                f"{self.get_short_nick(teamA_list[2])} {self.get_short_nick(teamA_list[3])} {self.get_short_nick(teamA_list[4])}"
        str_2 = f"2팀: {self.get_short_nick(teamB_list[0])} {self.get_short_nick(teamB_list[1])} " \
                f"{self.get_short_nick(teamB_list[2])} {self.get_short_nick(teamB_list[3])} {self.get_short_nick(teamB_list[4])} "

        self.team_edit.setText(str_1 + "\n" + str_2)

        if DEFINE_DEBUG_MODE:
            print("=======결과=======")
            print(str_1 + "\n" + str_2)

    def clicked_ok_btn(self):
        self.close()

    def get_nickname(self, idx):
        return self.player_info[idx]['NICKNAME']

    def get_short_nick(self, idx):
        return self.player_info[idx]['SHORTNICK']

    def get_mmr(self, idx):
        return self.player_info[idx]['MMR']

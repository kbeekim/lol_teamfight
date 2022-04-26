from PyQt5 import uic
from PyQt5.QtCore import Qt, QMimeData
from PyQt5.QtWidgets import QDialog, QPushButton, QTableWidgetItem
from PyQt5.QtGui import QDragEnterEvent, QDrag, QPixmap
from PyQt5.QtGui import QDropEvent

import excel
from main import resource_path
from main import DEFINE_DEBUG_MODE

UI_FILE_NAME = 'team_window.ui'

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]
excel_data = excel.ExcelClass()


class DragButton(QPushButton):

    def mouseMoveEvent(self, e):
        if e.buttons() == Qt.LeftButton:
            drag = QDrag(self)
            mime = QMimeData()
            drag.setMimeData(mime)
            drag.exec_(Qt.MoveAction)


class TeamWindow(QDialog, form_class):
    def __init__(self, team_info, player_info):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("팀 결과")
        self.setAcceptDrops(True)
        # self.setWindowIcon(QIcon(BASE_DIR + '/img/team.png'))

        # windowModality 설정을 NonModal -> ApplicationModal 으로 설정하여 해당 창을 종료 전까지 다른 창 사용 못하게 설정
        self.setWindowModality(Qt.ApplicationModal)

        self.team_info = team_info
        self.player_info = player_info
        self.final_list = []

        pos_img_list = ["top.png", "jungle.png", "mid.png", "bottom.png", "support.png"]

        self.top_label.setPixmap(QPixmap(resource_path(pos_img_list[0], '/img/')))
        self.jug_label.setPixmap(QPixmap(resource_path(pos_img_list[1], '/img/')))
        self.mid_label.setPixmap(QPixmap(resource_path(pos_img_list[2], '/img/')))
        self.adc_label.setPixmap(QPixmap(resource_path(pos_img_list[3], '/img/')))
        self.sup_label.setPixmap(QPixmap(resource_path(pos_img_list[4], '/img/')))

        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(3)

        self.set_text_ui()
        self.team1_win_btn.clicked.connect(self.clicked_team1_win_btn)
        self.team2_win_btn.clicked.connect(self.clicked_team2_win_btn)

        self.upload_btn.clicked.connect(self.clicked_upload_btn)
        self.close_btn.clicked.connect(self.clicked_close_btn)

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
        teamA_sum = self.team_info[1]
        # teamA_mmr = round(self.team_info[1] / 5, 1)

        teamB_list = self.team_info[2]
        teamB_sum = self.team_info[3]
        # teamB_mmr = round(self.team_info[3] / 5, 1)

        line_list = ['TOP', 'JUG', 'MID', 'ADC', 'SUP']
        for idx, line in enumerate(line_list):
            btn = DragButton(line)
            btn.setMaximumHeight(56)  # 버튼 높이 강제 조절
            btn.setText(self.get_nickname(teamA_list[idx]) + "\n(" + str(self.get_mmr(teamA_list[idx])) + ")")
            btn.setStyleSheet(
                "color: white;"
                "background-color: black;"
            )
            self.teamALayout.addWidget(btn)

        for idx, line in enumerate(line_list):
            btn = DragButton(line)
            btn.setMaximumHeight(56)  # 버튼 높이 강제 조절
            btn.setText(self.get_nickname(teamB_list[idx]) + "\n(" + str(self.get_mmr(teamB_list[idx])) + ")")
            btn.setStyleSheet(
                "color: white;"
                "background-color: black;"
            )
            self.teamBLayout.addWidget(btn)

        log_str = f"1팀: 합계 [{teamA_sum}]\n"
        for i in teamA_list:
            log_str += f"[{self.get_short_nick(i)}] / {str(self.get_mmr(i))}\n"
        log_str += f"\n2팀: 합계 [{teamB_sum}]\n"

        for i in teamB_list:
            log_str += f"[{self.get_short_nick(i)}] / {str(self.get_mmr(i))}\n"
        log_str += f"* 두 팀 차이: 합계[{round(abs(teamB_sum - teamA_sum), 1)}]\n"

        self.log_edit.setText(log_str)

        str_1 = f"1팀: {self.get_short_nick(teamA_list[0])} {self.get_short_nick(teamA_list[1])} " \
                f"{self.get_short_nick(teamA_list[2])} {self.get_short_nick(teamA_list[3])} {self.get_short_nick(teamA_list[4])}"
        str_2 = f"2팀: {self.get_short_nick(teamB_list[0])} {self.get_short_nick(teamB_list[1])} " \
                f"{self.get_short_nick(teamB_list[2])} {self.get_short_nick(teamB_list[3])} {self.get_short_nick(teamB_list[4])} "

        self.team_edit.setText(str_1 + "\n" + str_2)

        if DEFINE_DEBUG_MODE:
            print("[kb.debug] 최종 팀결성 결과")
            print(log_str)
            print("=========결과=========")
            print(str_1 + "\n" + str_2)

    def clicked_team1_win_btn(self):
        self.show_team_data(1)

    def clicked_team2_win_btn(self):
        self.show_team_data(2)

    def show_team_data(self, win_team):
        excel_data.read_gspread(excel.SHEET5)
        date_text = excel_data.get_last_date_text()

        self.final_list.clear()
        for n in range(self.teamALayout.count()):  # 5명
            self.tableWidget.setItem(n, 0, QTableWidgetItem(date_text))

            if win_team == 1:
                btn_nick_win = self.teamALayout.itemAt(n).widget().text().splitlines()[0]
                btn_nick_lose = self.teamBLayout.itemAt(n).widget().text().splitlines()[0]

            elif win_team == 2:
                btn_nick_win = self.teamBLayout.itemAt(n).widget().text().splitlines()[0]
                btn_nick_lose = self.teamALayout.itemAt(n).widget().text().splitlines()[0]

            self.tableWidget.setItem(n, 1, QTableWidgetItem(btn_nick_win))
            self.tableWidget.setItem(n, 2, QTableWidgetItem(btn_nick_lose))

            self.final_list.append([date_text, btn_nick_win, btn_nick_lose])

        # kb.todo 임시
        self.tmp_edit.setText("입력 위치: " + str(excel_data.get_update_cell_pos()))

        if DEFINE_DEBUG_MODE:
            print("[kb.debug] gspread 업로드 전, final list")
            print(self.final_list)

    def clicked_upload_btn(self):
        # kb.todo 예외처리
        if self.final_list is None:
            return

        excel_data.update_5_sheet(self.final_list)
        # self.close()

    def clicked_close_btn(self):
        self.close()

    def get_nickname(self, idx):
        return self.player_info[idx]['NICKNAME']

    def get_short_nick(self, idx):
        return self.player_info[idx]['SHORTNICK']

    def get_mmr(self, idx):
        return self.player_info[idx]['MMR']

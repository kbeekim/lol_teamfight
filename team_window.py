from asyncio import sleep
from functools import partial
from random import random

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import *

from PyQt5.QtWidgets import QDialog, QPushButton, QTableWidgetItem, QButtonGroup, QTabWidget
from PyQt5.QtGui import QDragEnterEvent, QDrag, QPixmap
from PyQt5.QtGui import QDropEvent
from asyncqt import QtGui, QtCore

import excel
import champ_window
from main import resource_path, DEFINE_MASTER_MODE
from main import DEFINE_DEBUG_MODE
from popup import ValvePopup, POPUP_TYPE_OK

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

            pixmap = QPixmap(self.size())
            self.render(pixmap)
            drag.setPixmap(pixmap)
            drag.exec_(Qt.MoveAction)


class TeamWindow(QDialog, form_class):
    team_window_closed = pyqtSignal()

    def __init__(self, team_info, player_info):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("팀 결과")
        self.setAcceptDrops(True)
        # self.setWindowIcon(QIcon(BASE_DIR + '/img/team.png'))

        # windowModality 설정을 NonModal -> ApplicationModal 으로 설정하여 해당 창을 종료 전까지 다른 창 사용 못하게 설정
        self.setWindowModality(Qt.ApplicationModal)

        self.champ_input = None

        self.update_ready = False
        self.update_champ_ready = False

        self.team_info = team_info
        self.player_info = player_info
        self.sh5_upload_list = []
        self.sh4_upload_win_list = []
        self.sh4_upload_lose_list = []

        pos_img_list = ["top.png", "jungle.png", "mid.png", "bottom.png", "support.png"]
        self.top_label.setPixmap(QPixmap(resource_path(pos_img_list[0], '/img/')))
        self.jug_label.setPixmap(QPixmap(resource_path(pos_img_list[1], '/img/')))
        self.mid_label.setPixmap(QPixmap(resource_path(pos_img_list[2], '/img/')))
        self.adc_label.setPixmap(QPixmap(resource_path(pos_img_list[3], '/img/')))
        self.sup_label.setPixmap(QPixmap(resource_path(pos_img_list[4], '/img/')))

        self.log_edit = QtWidgets.QTextEdit(self)
        self.team_edit = QtWidgets.QTextEdit(self)
        self.tabs = QTabWidget()
        self.tabs.addTab(self.team_edit, "팀 결과")
        self.tabs.addTab(self.log_edit, "팀 로그")
        self.result_vlayout.addWidget(self.tabs)

        self.set_text_ui()

        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(5)

        self.team1_win_btn.clicked.connect(self.clicked_team1_win_btn)
        self.team2_win_btn.clicked.connect(self.clicked_team2_win_btn)
        self.upload_btn.clicked.connect(self.clicked_upload_btn)
        self.close_btn.clicked.connect(self.clicked_close_btn)

        for idx in range(self.teamALayout.count()):  # 5명
            self.teamALayout.itemAt(idx).widget().clicked.connect(partial(self.clicked_champ_btn, self.teamALayout.itemAt(idx).widget()))
            self.teamBLayout.itemAt(idx).widget().clicked.connect(partial(self.clicked_champ_btn, self.teamBLayout.itemAt(idx).widget()))

        # 기본은 4, 5 시트 동시 입력
        self.sh45_both_upload_radio_btn.click()

    def closeEvent(self, event):
        event.accept()
        self.team_window_closed.emit()

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
            if pos.x() <= 289 and pos.y() <= 361:
                for n in range(self.teamALayout.count()):
                    w = self.teamALayout.itemAt(n).widget()

                    if pos.y() <= w.y() + w.size().height():
                        self.teamALayout.insertWidget(n, src_w)
                        self.teamALayout.insertWidget(src_n, w)
                        break
            else:
                w = ValvePopup(POPUP_TYPE_OK, "확인창", "1팀 안에서의 이동만 가능합니다.")
                w.show()

        elif team == TEAM_B:
            if 363 <= pos.x() <= 649 and pos.y() <= 361:
                for n in range(self.teamBLayout.count()):
                    w = self.teamBLayout.itemAt(n).widget()

                    if pos.y() <= w.y() + w.size().height():
                        self.teamBLayout.insertWidget(n, src_w)
                        self.teamBLayout.insertWidget(src_n, w)
                        break
            else:
                w = ValvePopup(POPUP_TYPE_OK, "확인창", "2팀 안에서의 이동만 가능합니다.")
                w.show()
        else:
            w = ValvePopup(POPUP_TYPE_OK, "확인창", "알 수 없는 에러 (개발자에게 신고하세요.)")

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

        result_txt = "~~~~~~~~~.\n" + str_1 + "\n" + str_2
        self.team_edit.setText(result_txt)

        if DEFINE_DEBUG_MODE:
            print("[kb.debug] 최종 팀결성 결과")
            print(log_str)
            print(result_txt)

    def clicked_champ_btn(self, btn):
        self.champ_input = champ_window.ChampWindow(btn)
        self.champ_input.show()

    def clicked_team1_win_btn(self):
        self.show_team_data(1)

    def clicked_team2_win_btn(self):
        self.show_team_data(2)

    def show_team_data(self, win_team):
        excel_data.read_gspread_sheet5()
        excel_data.read_gspread_sheet4()

        # kb.todo sh4 날짜는?
        date_text = excel_data.get_sh5_last_date_text()
        self.sh5_upload_list.clear()
        self.sh4_upload_win_list.clear()
        self.sh4_upload_lose_list.clear()

        champ_input_complete = True

        for n in range(self.teamALayout.count()):  # 5명
            self.tableWidget.setItem(n, 0, QTableWidgetItem(date_text))

            if win_team == 1:
                nick_win = self.teamALayout.itemAt(n).widget().text().splitlines()[0]
                champ_win = self.teamALayout.itemAt(n).widget().text().splitlines()[1]

                nick_lose = self.teamBLayout.itemAt(n).widget().text().splitlines()[0]
                champ_lose = self.teamBLayout.itemAt(n).widget().text().splitlines()[1]
            elif win_team == 2:
                nick_win = self.teamBLayout.itemAt(n).widget().text().splitlines()[0]
                champ_win = self.teamBLayout.itemAt(n).widget().text().splitlines()[1]

                nick_lose = self.teamALayout.itemAt(n).widget().text().splitlines()[0]
                champ_lose = self.teamALayout.itemAt(n).widget().text().splitlines()[1]

            self.tableWidget.setItem(n, 1, QTableWidgetItem(nick_win))
            self.tableWidget.setItem(n, 2, QTableWidgetItem(champ_win))

            self.tableWidget.setItem(n, 3, QTableWidgetItem(nick_lose))
            self.tableWidget.setItem(n, 4, QTableWidgetItem(champ_lose))

            self.sh5_upload_list.append([date_text, nick_win, nick_lose])
            self.sh4_upload_win_list.append([nick_win, champ_win])
            self.sh4_upload_lose_list.append([nick_lose, champ_lose])

            if not ((champ_lose in champ_window.CHAMPION) and (champ_win in champ_window.CHAMPION)):
                champ_input_complete = False

        # Check Validation
        if not champ_input_complete:
            tmp_str = "챔피언 입력 필요"
            self.update_champ_ready = False
        elif win_team == 1:
            tmp_str = "1팀 승리!\n입력 준비 완료"
            self.update_champ_ready = True
        elif win_team == 2:
            tmp_str = "2팀 승리!\n입력 준비 완료"
            self.update_champ_ready = True

        # kb.todo sheet5 우선은 모두 성공으로 판단
        w = ValvePopup(POPUP_TYPE_OK, "확인창", tmp_str)
        w.show()

        self.update_ready = True

        # kb.todo 임시
        self.tmp_label.setText("5시트 입력 위치: " + str(excel_data.get_sh5_update_cell_pos()) +
                               " / 4시트 기준 위치: " + str(excel_data.get_sh4_update_cell_pos()))

        if DEFINE_DEBUG_MODE:
            print("[kb.debug] gspread 업로드 전, upload_list")
            print(self.sh5_upload_list)
            print(self.sh4_upload_win_list)
            print(self.sh4_upload_lose_list)

    def clicked_upload_btn(self):
        # kb.todo 예외처리
        if self.sh5_upload_list is None:
            return
        if self.sh4_upload_win_list is None:
            return
        if self.sh4_upload_lose_list is None:
            return

        if self.update_ready:
            if self.update_champ_ready:
                if self.sh45_both_upload_radio_btn.isChecked():
                    excel_data.update_5_sheet(self.sh5_upload_list)
                    excel_data.update_4_sheet(self.sh4_upload_win_list, self.sh4_upload_lose_list)
                elif self.sh5_upload_radio_btn.isChecked():
                    excel_data.update_5_sheet(self.sh5_upload_list)
                elif self.sh4_upload_radio_btn.isChecked():
                    excel_data.update_4_sheet(self.sh4_upload_win_list, self.sh4_upload_lose_list)

                # kb.todo sheet5 4 우선은 모두 성공으로 판단
                w = ValvePopup(POPUP_TYPE_OK, "확인창", "업로드 성공!")
                w.show()

                self.close()
            else:
                if self.sh45_both_upload_radio_btn.isChecked():
                    w = ValvePopup(POPUP_TYPE_OK, "확인창", "챔피언을 입력해주세요!")
                    w.show()
                elif self.sh5_upload_radio_btn.isChecked():
                    # kb.todo 조정 단계로 5시트만 입력가능하도록 함
                    excel_data.update_5_sheet(self.sh5_upload_list)
                    w = ValvePopup(POPUP_TYPE_OK, "확인창", "다음부턴 챔피언도 입력해 주세요! \n 업로드 성공!")
                    w.show()
                    self.close()
                elif self.sh4_upload_radio_btn.isChecked():
                    w = ValvePopup(POPUP_TYPE_OK, "확인창", "챔피언을 입력해주세요!")
                    w.show()
        else:
            w = ValvePopup(POPUP_TYPE_OK, "확인창", "승리 버튼을 눌러 데이터를 확인해주세요")
            w.show()

    def clicked_close_btn(self):
        self.close()

    def get_nickname(self, idx):
        return self.player_info[idx]['NICKNAME']

    def get_short_nick(self, idx):
        return self.player_info[idx]['SHORTNICK']

    def get_mmr(self, idx):
        return self.player_info[idx]['MMR']

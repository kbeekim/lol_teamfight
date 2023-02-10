from asyncio import sleep
from functools import partial
import random

from PyQt5 import uic, QtWidgets
from PyQt5.QtCore import *

from PyQt5.QtWidgets import QDialog, QPushButton, QTableWidgetItem, QTabWidget, QHBoxLayout, QButtonGroup, QGroupBox, \
    QProgressDialog
from PyQt5.QtGui import QDragEnterEvent, QDrag, QPixmap, QFont

import excel
import champ_window
from popup import ValvePopup, POPUP_TYPE_OK
from global_settings import *
from thread import Thread

UI_FILE_NAME = 'team_window.ui'

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]
excel_data = excel.ExcelClass()

WIN_TEAM_A = 1
WIN_TEAM_B = 2

# kbeekim) 버튼이 추가된다면 값을 변경해줘야함
TEAM_A_PLAYER_IDX = 0
TEAM_A_CHAMP_IDX = 1

TEAM_B_PLAYER_IDX = 1
TEAM_B_CHAMP_IDX = 0


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


def make_btn(is_draggable, width, text_size, text):
    if is_draggable:
        btn = DragButton()
    else:
        btn = QPushButton()

    btn.setMaximumHeight(56)  # 버튼 높이 강제 조절

    if width is not None:
        btn.setMaximumWidth(width)  # 버튼 너비 강제 조절

    btn.setText(text)

    btn.setStyleSheet("""
        QPushButton {
            color: white;
            background-color: black; 
        }
        QPushButton:hover {
            color: #ff7f50;
        }
    """)

    if text_size is not None:
        btn.setFont(QFont(G_FONT, text_size))

    return btn


class TeamWindow(QDialog, form_class):
    team_window_closed = pyqtSignal()

    def __init__(self, team_info, player_info):
        super().__init__()
        self.excel_thread = None
        self.progress_dialog = None
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
        # 챔피언 중복 초기화
        g_clear_champion_clicked()

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

        self.set_btn_layout()
        self.set_log_layout()

        self.tableWidget.setRowCount(5)
        self.tableWidget.setColumnCount(5)

        self.team1_win_btn.clicked.connect(self.clicked_team1_win_btn)
        self.team2_win_btn.clicked.connect(self.clicked_team2_win_btn)
        self.upload_btn.clicked.connect(self.clicked_upload_btn)
        self.close_btn.clicked.connect(self.clicked_close_btn)

        for idx in range(self.teamALayout.count()):  # 5명
            # self.teamALayout.itemAt(idx).itemAt(TEAM_A_PLAYER_IDX).widget().clicked.connect(partial(self.clicked_champ_btn, self.teamALayout.itemAt(idx).itemAt(TEAM_A_CHAMP_IDX).widget()))
            self.teamALayout.itemAt(idx).itemAt(TEAM_A_CHAMP_IDX).widget().clicked.connect(partial(self.clicked_champ_btn, self.teamALayout.itemAt(idx).itemAt(TEAM_A_CHAMP_IDX).widget()))

            # self.teamALayout.itemAt(idx).itemAt(TEAM_B_PLAYER_IDX).widget().clicked.connect(partial(self.clicked_champ_btn, self.teamALayout.itemAt(idx).itemAt(TEAM_A_CHAMP_IDX).widget()))
            self.teamBLayout.itemAt(idx).itemAt(TEAM_B_CHAMP_IDX).widget().clicked.connect(partial(self.clicked_champ_btn, self.teamBLayout.itemAt(idx).itemAt(TEAM_B_CHAMP_IDX).widget()))

        # 기본은 4, 5 시트 동시 입력
        self.sh45_both_upload_radio_btn.click()

    def closeEvent(self, event):
        event.accept()
        self.team_window_closed.emit()

    def dragEnterEvent(self, e):
        e.accept()

    def dropEvent(self, e):
        src_n = 0
        src_w = None
        TEAM_A, TEAM_B = 0, 1
        pos = e.pos()
        clicked_w = e.source() # DragButton
        team = None

        for n in range(5):
            if self.teamALayout.itemAt(n).itemAt(TEAM_A_PLAYER_IDX).widget() == clicked_w or self.teamALayout.itemAt(n).itemAt(TEAM_A_CHAMP_IDX).widget() == clicked_w:
                team = TEAM_A
                src_n = n
                break
            if self.teamBLayout.itemAt(n).itemAt(TEAM_B_PLAYER_IDX).widget() == clicked_w or self.teamBLayout.itemAt(n).itemAt(TEAM_B_CHAMP_IDX).widget() == clicked_w :
                team = TEAM_B
                src_n = n
                break

        if team == TEAM_A:
            if pos.x() <= 480 and pos.y() <= 380:
                for n in range(5):
                    w = self.teamALayout.itemAt(n).itemAt(TEAM_A_PLAYER_IDX).widget()
                    if pos.y() <= w.y() + w.size().height():
                        # if G_DEFINE_DEBUG_MODE:
                            # print(f"n : {n} [3] src_w : {src_w}")
                            # print(f"src_n : {src_n} [3] w : {w}")

                        # kbeekim) insertLayout 을 통해 바뀌는게 잘안된다..
                        # self.teamALayout.insertLayout(n, src_w)
                        # self.teamALayout.insertLayout(src_n, w)

                        for cnt in range(self.teamALayout.itemAt(n).count()):
                            tmp = self.teamALayout.itemAt(n).itemAt(cnt).widget()
                            self.teamALayout.itemAt(n).insertWidget(cnt, self.teamALayout.itemAt(src_n).itemAt(cnt).widget())
                            self.teamALayout.itemAt(src_n).insertWidget(cnt, tmp)

                        break
            else:
                ValvePopup(POPUP_TYPE_OK, "확인창", "1팀 안에서의 이동만 가능합니다.")

        elif team == TEAM_B:
            if 550 <= pos.x() <= 1020 and pos.y() <= 380:
                for n in range(5):
                    w = self.teamBLayout.itemAt(n).itemAt(TEAM_B_PLAYER_IDX).widget()
                    if pos.y() <= w.y() + w.size().height():

                        for cnt in range(self.teamBLayout.itemAt(n).count()):
                            tmp = self.teamBLayout.itemAt(n).itemAt(cnt).widget()
                            self.teamBLayout.itemAt(n).insertWidget(cnt, self.teamBLayout.itemAt(src_n).itemAt(cnt).widget())
                            self.teamBLayout.itemAt(src_n).insertWidget(cnt, tmp)
                        break
            else:
                ValvePopup(POPUP_TYPE_OK, "확인창", "2팀 안에서의 이동만 가능합니다.")
        else:
            ValvePopup(POPUP_TYPE_OK, "확인창", "알 수 없는 에러 (개발자에게 신고하세요.)")

        if G_DEFINE_DEBUG_MODE:
            print(f'pos x, y : {pos.x()}, {pos.y()}')
        e.accept()

    def set_btn_layout(self):
        teamA_list = self.team_info[0]
        teamB_list = self.team_info[2]

        line_list = ['Test0', 'Test1', 'Test2', 'Test3', 'Test4']
        for idx, line in enumerate(line_list):
            h_layout = QHBoxLayout()
            #kb.todo 자주 사용하는 챔피언
            # h_layout.addWidget(make_btn(False, 56, None, "1"))
            # h_layout.addWidget(make_btn(False, 56, None, "2"))
            # h_layout.addWidget(make_btn(False, 56, None, "3"))

            # kbeekim) 23.02.10 닉네임 변경 대비, subname 추가
            subnick = self.get_subnick(teamA_list[idx])
            if len(subnick) > 0:
                h_layout.addWidget(
                    make_btn(True, None, 13, f"{self.get_nickname(teamA_list[idx])}\n({subnick})"))
            else:
                h_layout.addWidget(make_btn(True, None, 13, self.get_nickname(teamA_list[idx])))

            h_layout.addWidget(make_btn(True, 180, 10, "(챔피언 입력)"))
            self.teamALayout.addLayout(h_layout)

        for idx, line in enumerate(line_list):
            h_layout = QHBoxLayout()

            h_layout.addWidget(make_btn(True, 180, 10, "(챔피언 입력)"))
            # kbeekim) 23.02.10 닉네임 변경 대비, subname 추가
            subnick = self.get_subnick(teamB_list[idx])
            if len(subnick) > 0:
                h_layout.addWidget(
                    make_btn(True, None, 13, f"{self.get_nickname(teamB_list[idx])}\n({subnick})"))
            else:
                h_layout.addWidget(make_btn(True, None, 13, self.get_nickname(teamB_list[idx])))

            #kb.todo 자주 사용하는 챔피언
            # h_layout.addWidget(make_btn(False, 56, None, "1"))
            # h_layout.addWidget(make_btn(False, 56, None, "2"))
            # h_layout.addWidget(make_btn(False, 56, None, "3"))

            self.teamBLayout.addLayout(h_layout)

    def set_log_layout(self):
        teamA_list = self.team_info[0]
        teamA_sum = self.team_info[1]

        teamB_list = self.team_info[2]
        teamB_sum = self.team_info[3]

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

        result_txt = "~~~~~~~~~..\n" + str_1 + "\n" + str_2
        self.team_edit.setText(result_txt)

        if G_DEFINE_DEBUG_MODE:
            print("[kb.debug] 최종 팀결성 결과")
            print(log_str)
            print(result_txt)

    def clicked_champ_btn(self, btn):
        self.champ_input = champ_window.ChampWindow(btn)
        self.champ_input.show()

    def clicked_team1_win_btn(self):
        self.show_team_data(WIN_TEAM_A)

    def clicked_team2_win_btn(self):
        self.show_team_data(WIN_TEAM_B)

    def show_team_data(self, win_team):
        self.progress_dialog = QProgressDialog("데이터를 준비하는 중 입니다.", None, 0, 0)
        self.progress_dialog.setWindowModality(Qt.ApplicationModal)
        self.progress_dialog.setWindowTitle(g_get_lol_random_speech_str())
        self.progress_dialog.setMinimumWidth(600)
        self.progress_dialog.show()

        self.excel_thread = Thread(excel_data, G_THREAD_READ_4_5)
        self.excel_thread.start()
        self.excel_thread.end_thread_signal.connect(partial(self.after_end_excel_thread, win_team))

    @pyqtSlot(bool)
    def after_end_excel_thread(self, win_team, excel_result):
        self.progress_dialog.cancel()

        if not excel_result:
            ValvePopup(POPUP_TYPE_OK, "확인창", "[Error] 엑셀 확인 필요")
            return 
        
        # kb.todo sh4 날짜는?
        date_text = excel_data.get_sh5_last_date_text()
        self.sh5_upload_list.clear()
        self.sh4_upload_win_list.clear()
        self.sh4_upload_lose_list.clear()
        champ_input_complete = True

        for n in range(5):  # 한 팀 5명
            self.tableWidget.setItem(n, 0, QTableWidgetItem(date_text))

            if win_team == WIN_TEAM_A:
                tmp_nick_win = self.teamALayout.itemAt(n).itemAt(TEAM_A_PLAYER_IDX).widget().text()
                champ_win = self.teamALayout.itemAt(n).itemAt(TEAM_A_CHAMP_IDX).widget().text()

                tmp_nick_lose = self.teamBLayout.itemAt(n).itemAt(TEAM_B_PLAYER_IDX).widget().text()
                champ_lose = self.teamBLayout.itemAt(n).itemAt(TEAM_B_CHAMP_IDX).widget().text()
            elif win_team == WIN_TEAM_B:
                tmp_nick_win = self.teamBLayout.itemAt(n).itemAt(TEAM_B_PLAYER_IDX).widget().text()
                champ_win = self.teamBLayout.itemAt(n).itemAt(TEAM_B_CHAMP_IDX).widget().text()

                tmp_nick_lose = self.teamALayout.itemAt(n).itemAt(TEAM_A_PLAYER_IDX).widget().text()
                champ_lose = self.teamALayout.itemAt(n).itemAt(TEAM_A_CHAMP_IDX).widget().text()

            # kbeekim) 23.02.10 닉네임 변경 대비, subname 추가
            nick_win = tmp_nick_win.splitlines()[0]
            nick_lose = tmp_nick_lose.splitlines()[0]

            self.tableWidget.setItem(n, 1, QTableWidgetItem(nick_win))
            self.tableWidget.setItem(n, 2, QTableWidgetItem(champ_win))

            self.tableWidget.setItem(n, 3, QTableWidgetItem(nick_lose))
            self.tableWidget.setItem(n, 4, QTableWidgetItem(champ_lose))

            self.sh5_upload_list.append([date_text, nick_win, nick_lose])
            self.sh4_upload_win_list.append([nick_win, champ_win])
            self.sh4_upload_lose_list.append([nick_lose, champ_lose])

            if not ((champ_lose in G_CHAMPION) and (champ_win in G_CHAMPION)):
                champ_input_complete = False

        # Check Validation
        if not champ_input_complete:
            tmp_str = "챔피언 입력 필요"
            self.update_champ_ready = False
        elif win_team == WIN_TEAM_A:
            tmp_str = "1팀 승리!\n입력 준비 완료"
            self.update_champ_ready = True
        elif win_team == WIN_TEAM_B:
            tmp_str = "2팀 승리!\n입력 준비 완료"
            self.update_champ_ready = True

        # kb.todo sheet5 우선은 모두 성공으로 판단
        ValvePopup(POPUP_TYPE_OK, "확인창", tmp_str)

        self.update_ready = True
        self.tmp_label.setText("5시트 입력 위치: " + str(excel_data.get_sh5_update_cell_pos()) +
                               " / 4시트 기준 위치: " + str(excel_data.get_sh4_update_cell_pos()))

        if G_DEFINE_DEBUG_MODE:
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
                ValvePopup(POPUP_TYPE_OK, "확인창", "업로드 성공!")

                self.close()
            else:
                if self.sh45_both_upload_radio_btn.isChecked():
                    ValvePopup(POPUP_TYPE_OK, "확인창", "챔피언을 입력해주세요!")
                elif self.sh5_upload_radio_btn.isChecked():
                    # kb.todo 조정 단계로 5시트만 입력 가능하도록 함
                    excel_data.update_5_sheet(self.sh5_upload_list)
                    ValvePopup(POPUP_TYPE_OK, "확인창", "다음부턴 챔피언도 입력해 주세요! \n 업로드 성공!")
                    self.close()
                elif self.sh4_upload_radio_btn.isChecked():
                    ValvePopup(POPUP_TYPE_OK, "확인창", "챔피언을 입력해주세요!")
        else:
            ValvePopup(POPUP_TYPE_OK, "확인창", "승리 버튼을 눌러 데이터를 확인해주세요")

    def clicked_close_btn(self):
        self.close()

    def get_nickname(self, idx):
        return self.player_info[idx]['NICKNAME']

    def get_short_nick(self, idx):
        return self.player_info[idx]['SHORTNICK']

    def get_subnick(self, idx):
        return self.player_info[idx]['SUBNAME']

    def get_mmr(self, idx):
        return self.player_info[idx]['MMR']

# kb.todo next path 설정
import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(BASE_DIR + '/img/ui/team_window.ui')[0]


class TeamWindow(QDialog, form_class):
    def __init__(self, team_info, player_info):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("팀 결과")
        self.setWindowIcon(QIcon(BASE_DIR + '/img/team.png'))

        # windowModality 설정을 NonModal -> ApplicationModal 으로 설정하여 해당 창을 종료 전까지 다른 창 사용 못하게 설정
        self.setWindowModality(Qt.ApplicationModal)

        self.team_info = team_info
        self.player_info = player_info

        self.set_text_ui()
        self.ok_btn.clicked.connect(self.clicked_ok_btn)

    def set_text_ui(self):
        teamA_list = self.team_info[0]
        teamA_mmr = round(self.team_info[1]/5, 1)
        teamB_list = self.team_info[2]
        teamB_mmr = round(self.team_info[3]/5, 1)

        # kb.todo mmr 끝에 space 가 있어보임
        self.teamA_1_btn.setText(self.player_info[teamA_list[0]][1] + "\n( " + self.player_info[teamA_list[0]][3] + ")")
        self.teamA_2_btn.setText(self.player_info[teamA_list[1]][1] + "\n( " + self.player_info[teamA_list[1]][3] + ")")
        self.teamA_3_btn.setText(self.player_info[teamA_list[2]][1] + "\n( " + self.player_info[teamA_list[2]][3] + ")")
        self.teamA_4_btn.setText(self.player_info[teamA_list[3]][1] + "\n( " + self.player_info[teamA_list[3]][3] + ")")
        self.teamA_5_btn.setText(self.player_info[teamA_list[4]][1] + "\n( " + self.player_info[teamA_list[4]][3] + ")")

        self.teamB_1_btn.setText(self.player_info[teamB_list[0]][1] + "\n( " + self.player_info[teamB_list[0]][3] + ")")
        self.teamB_2_btn.setText(self.player_info[teamB_list[1]][1] + "\n( " + self.player_info[teamB_list[1]][3] + ")")
        self.teamB_3_btn.setText(self.player_info[teamB_list[2]][1] + "\n( " + self.player_info[teamB_list[2]][3] + ")")
        self.teamB_4_btn.setText(self.player_info[teamB_list[3]][1] + "\n( " + self.player_info[teamB_list[3]][3] + ")")
        self.teamB_5_btn.setText(self.player_info[teamB_list[4]][1] + "\n( " + self.player_info[teamB_list[4]][3] + ")")

        str_1 = f'1팀: 평균[{teamA_mmr}] {self.player_info[teamA_list[0]][2]} {self.player_info[teamA_list[1]][2]} {self.player_info[teamA_list[2]][2]} {self.player_info[teamA_list[3]][2]} {self.player_info[teamA_list[4]][2]}'
        str_2 = f'2팀: 평균[{teamB_mmr}] {self.player_info[teamB_list[0]][2]} {self.player_info[teamB_list[1]][2]} {self.player_info[teamB_list[2]][2]} {self.player_info[teamB_list[3]][2]} {self.player_info[teamB_list[4]][2]}'

        self.team_edit.setText(str_1 + "\n" + str_2)

    def clicked_ok_btn(self):
        self.close()

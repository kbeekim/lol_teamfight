from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QDialog
from main import resource_path
from main import DEFINE_DEBUG_MODE

UI_FILE_NAME = 'team_window.ui'

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]


class TeamWindow(QDialog, form_class):
    def __init__(self, team_info, player_info):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("팀 결과")
        # self.setWindowIcon(QIcon(BASE_DIR + '/img/team.png'))

        # windowModality 설정을 NonModal -> ApplicationModal 으로 설정하여 해당 창을 종료 전까지 다른 창 사용 못하게 설정
        self.setWindowModality(Qt.ApplicationModal)

        self.team_info = team_info
        self.player_info = player_info
        self.teamA_btn_list = [self.teamA_1_btn, self.teamA_2_btn, self.teamA_3_btn, self.teamA_4_btn, self.teamA_5_btn]
        self.teamB_btn_list = [self.teamB_1_btn, self.teamB_2_btn, self.teamB_3_btn, self.teamB_4_btn, self.teamB_5_btn]

        self.set_text_ui()
        self.ok_btn.clicked.connect(self.clicked_ok_btn)

    def set_text_ui(self):
        teamA_list = self.team_info[0]
        teamA_mmr = round(self.team_info[1] / 5, 1)
        teamB_list = self.team_info[2]
        teamB_mmr = round(self.team_info[3] / 5, 1)

        if DEFINE_DEBUG_MODE:
            print(f"1팀: 평균[{teamA_mmr}] / 합계[{self.team_info[1]}]")
            for i in teamA_list:
                print(f"1팀: [{self.get_short_nick(i)}] / {str(self.get_mmr(i))}")

            print(f"2팀: 평균[{teamB_mmr}]/합계[{self.team_info[3]}]")
            for i in teamB_list:
                print(f"2팀: [{self.get_short_nick(i)}] / {str(self.get_mmr(i))}")

            print(
                f"두 팀 차이: 평균[{round(abs(teamA_mmr - teamB_mmr), 1)}]/합계[{round(abs(self.team_info[3] - self.team_info[1]), 1)}] \n")

        for idx, btn in enumerate(self.teamA_btn_list):
            btn.setText(self.get_nickname(teamA_list[idx]) + "\n(" + str(self.get_mmr(teamA_list[idx])) + ")")
        for idx, btn in enumerate(self.teamB_btn_list):
            btn.setText(self.get_nickname(teamB_list[idx]) + "\n(" + str(self.get_mmr(teamB_list[idx])) + ")")

        str_1 = f"1팀: {self.get_short_nick(teamA_list[0])} {self.get_short_nick(teamA_list[1])} " \
                f"{self.get_short_nick(teamA_list[2])} {self.get_short_nick(teamA_list[3])} {self.get_short_nick(teamA_list[4])}"
        str_2 = f"2팀: {self.get_short_nick(teamB_list[0])} {self.get_short_nick(teamB_list[1])} " \
                f"{self.get_short_nick(teamB_list[2])} {self.get_short_nick(teamB_list[3])} {self.get_short_nick(teamB_list[4])} "

        self.team_edit.setText(str_1 + "\n" + str_2)
        print("===Result===")
        print(str_1 + "\n" + str_2)

    def clicked_ok_btn(self):
        self.close()

    def get_nickname(self, idx):
        return self.player_info[idx]['NICKNAME']

    def get_short_nick(self, idx):
        return self.player_info[idx]['SHORTNICK']

    def get_mmr(self, idx):
        return self.player_info[idx]['MMR']

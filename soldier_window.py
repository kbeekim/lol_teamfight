import os
import sys

from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QDoubleValidator, QIcon
from PyQt5.QtWidgets import QWidget

# kb.todo next path 설정
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
form_class = uic.loadUiType(BASE_DIR + '/img/ui/soldier_window.ui')[0]

MIN_MMR_VALUE = 600
MAX_MMR_VALUE = 2000

DIAMOND_MMR_VALUE = 1150
PLATINUM_MMR_VALUE = 1100
GOLD_MMR_VALUE = 1000
SILVER_MMR_VALUE = 950
BRONZE_MMR_VALUE = 750
IRON_MMR_VALUE = 600

MMR_LIST = [{'tier': "다이아", 'mmr': DIAMOND_MMR_VALUE}
    , {'tier': "플레티넘", 'mmr': PLATINUM_MMR_VALUE}
    , {'tier': "골드", 'mmr': GOLD_MMR_VALUE}
    , {'tier': "실버", 'mmr': SILVER_MMR_VALUE}
    , {'tier': "브론즈", 'mmr': BRONZE_MMR_VALUE}
    , {'tier': "아이언", 'mmr': IRON_MMR_VALUE}]

ALERT_MSG_TYPE_NORMAL = 0
ALERT_MSG_TIMEOUT_NORMAL = 3000

img_path = './img'


# worker_info 와 동일한 구조로 soldier_info 를 만든다
# (excel.py 의 worker_info 양식이 변경 되면 같이 수정 필요)
def make_soldier_info(nickname, mmr):
    soldier_info = [None] * 13

    soldier_info[1] = nickname
    soldier_info[2] = nickname
    soldier_info[3] = mmr # 연계

    return soldier_info


def check_valid_mmr(mmr_str):
    if not mmr_str.isdigit():
        return False

    mmr = int(mmr_str)
    if mmr < MIN_MMR_VALUE:
        return False
    elif mmr > MAX_MMR_VALUE:
        return False
    else:
        return True


def calc_mmr2tier(mmr_str):
    mmr = int(mmr_str)

    # 높은 티어부터 검색
    for i in range(len(MMR_LIST)):
        if mmr >= MMR_LIST[i]['mmr']:
            return MMR_LIST[i]['tier']

    return MMR_LIST[len(MMR_LIST)]['tier']


class SoldierWindow(QWidget, form_class):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        # kb.todo next] exec_() main window 에서 대기 타고 싶은데 안됨.. 뭐가 문제인지 확인해보자
        self.main_window = parent
        self.setWindowTitle("용병 추가")
        self.setWindowIcon(QIcon(BASE_DIR + '/img/add_soldier.png'))

        # windowModality 설정을 NonModal -> ApplicationModal 으로 설정하여 해당 창을 종료 전까지 다른 창 사용 못하게 설정
        self.setWindowModality(Qt.ApplicationModal)

        mmr_refer_str = ""
        # mmr spinner

        for i in range(len(MMR_LIST)):
            str_tier = MMR_LIST[i]['tier']
            str_mmr = str(MMR_LIST[i]['mmr'])
            self.mmr_combo_box.addItem(str_tier)

            mmr_refer_str += str_tier + ":  " + str_mmr
            if i == 2:
                mmr_refer_str += "\n"
            elif i != len(MMR_LIST) - 1:
                mmr_refer_str += " / "

        # kbeekim) 콤보박스의 init 문구를 설정하려했는데 Editable 할 때 setPlaceholderText로 설정 가능하여 그닥..
        # 아니면 마우스 event 로 만들 수 있긴 할 듯한데.. 굳이.. 그냥 비워두는거에 만족하자
        # self.mmr_combo_box.setEditable(True)
        # self.mmr_combo_box.lineEdit().setPlaceholderText("티어 선택")
        # self.mmr_combo_box.setCurrentIndex(-1)
        self.mmr_combo_box.setCurrentIndex(-1)

        # mmr 수동 입력 창
        self.mmr_edit.hide()
        self.mmr_edit.setValidator(QDoubleValidator())  # 실수만 입력 가능

        self.manual_radio.toggled.connect(self.clicked_manual_radio)
        # mmr 참고 라벨
        # self.mmr_label.setIndent(Qt.AlignCenter) # ->Qt_Designer 수정 (가운데 정렬)
        self.mmr_label.setText(mmr_refer_str)
        # 확인 버튼
        self.ok_btn.clicked.connect(self.clicked_ok_btn)
        # nickname_edit 엔터 시, 확인 버튼과 똑같은 행정
        self.nickname_edit.returnPressed.connect(self.clicked_ok_btn)
        # mmr_edit 엔터 시, 확인 버튼과 똑같은 행정
        self.mmr_edit.returnPressed.connect(self.clicked_ok_btn)
        # 취소 버튼
        self.cancel_btn.clicked.connect(self.clicked_cancel_btn)
        # 알람 라벨
        self.alert_label.setText("")
        # 알람 타이머
        self.timer = QTimer()
        self.timer.timeout.connect(self.alert_timeout)

    def clicked_manual_radio(self):
        # radioBtn = self.sender()
        if self.manual_radio.isChecked():
            self.mmr_edit.show()
            self.mmr_combo_box.hide()
        else:
            self.mmr_edit.hide()
            self.mmr_combo_box.show()

    def clicked_ok_btn(self):
        nickname = self.nickname_edit.text()
        tier = ""

        if not nickname:
            self.show_alert_message("적어도 이름은 알아야 영혼을 불 태울 수 있죠", ALERT_MSG_TYPE_NORMAL)
            return
        elif len(nickname.encode("cp949")) > 16:  # 롤 닉네임 제한수 16Byte (한글 2Byte. 영문 1Byte)
            self.show_alert_message("이름이 조금 긴 느낌이 듭니다.", ALERT_MSG_TYPE_NORMAL)
            return

        if self.manual_radio.isChecked():  # mmr 수동 입력이라면
            mmr_str = self.mmr_edit.text()
            if not mmr_str:
                self.show_alert_message("아이언도 mmr은 있답니다.", ALERT_MSG_TYPE_NORMAL)
                return
            elif not check_valid_mmr(mmr_str):
                self.show_alert_message("우리집 고양이가 mmr을 입력했나보군요 ()", ALERT_MSG_TYPE_NORMAL)
                return
            mmr = int(mmr_str)
            tier = calc_mmr2tier(mmr_str)
        else:  # mmr 자동 입력이라면
            idx = self.mmr_combo_box.currentIndex()
            tier = self.mmr_combo_box.currentText()
            if idx == -1:
                self.show_alert_message("mmr 칸이 쓸쓸해 보이네요", ALERT_MSG_TYPE_NORMAL)
                return
            mmr = MMR_LIST[idx]['mmr']
            tier = MMR_LIST[idx]['tier']

        # main_window 와 연계됨.
        ret = self.main_window.insert_soldier_to_player(make_soldier_info(nickname, mmr), tier)

        if ret == self.main_window.SOLDIER_INFO_SUCCESS:
            self.close_soldier_window()
        elif ret == self.main_window.SOLDIER_INFO_ERROR_FULL_PLAYER:
            self.show_alert_message("이대로 가다간 배가 침몰할 수 있어요", ALERT_MSG_TYPE_NORMAL)
        elif ret == self.main_window.SOLDIER_INFO_ERROR_SAME_NAME:
            self.show_alert_message("어디서 많이 본 분이시군요?", ALERT_MSG_TYPE_NORMAL)

    def clicked_cancel_btn(self):
        self.close_soldier_window()

    def close_soldier_window(self):
        self.nickname_edit.clear()
        self.mmr_combo_box.setCurrentIndex(-1)
        self.mmr_edit.clear()
        if self.manual_radio.isChecked():  # mmr 수동 입력이라면
            self.mmr_edit.hide()
            self.mmr_combo_box.show()
            self.manual_radio.setChecked(False)
        self.show_alert_message("", ALERT_MSG_TYPE_NORMAL)
        self.close()

    # kbeekim) 애초에 window 가 아닌 QWidget 로 만들어버려 상태바를 못쓰게되었다.
    # TextLabel 과 QTimer로 대략적인 문구표출 기능을 하게 함
    def show_alert_message(self, msg, alert_type):
        # print("[kb.test] 폰트:  " + self.alert_label.font().family())
        self.timer.stop()

        if alert_type == ALERT_MSG_TYPE_NORMAL:
            self.timer.start(ALERT_MSG_TIMEOUT_NORMAL)
            self.alert_label.setStyleSheet(
                # kb.check 이상하게 연속으로 호출하면 Gulim 으로 바뀜;
                "font-family: Noto Sans Korean Regular;"
                "color: red;"
            )
            self.alert_label.setText(msg)
            # 나중에 type 추가하던지-
        else:
            self.timer.start(ALERT_MSG_TIMEOUT_NORMAL)
            self.alert_label.setText(msg)

    def alert_timeout(self):
        self.alert_label.setText("")

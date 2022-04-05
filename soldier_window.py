# kb.todo path 설정
from PyQt5 import uic
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QWidget

absolute_path = "C:/Users/YS KIM/PycharmProjects/pythonProject/"
form_class = uic.loadUiType(absolute_path + "soldier_window.ui")[0]

MMR_LIST = [{'tier': "다이아", 'mmr': 1150}
    , {'tier': "플레티넘", 'mmr': 1100}
    , {'tier': "골드", 'mmr': 1050}
    , {'tier': "실버", 'mmr': 1000}
    , {'tier': "브론즈", 'mmr': 950}
    , {'tier': "아이언", 'mmr': 900}]

MIN_MMR_VALUE = 600
MAX_MMR_VALUE = 2000

ALERT_MSG_TYPE_NORMAL = 0
ALERT_MSG_TIMEOUT_NORMAL = 3000


# worker_info 와 동일한 구조로 soldier_info 를 만든다
# (excel.py 의 worker_info 양식이 변경 되면 같이 수정 필요)
def make_soldier_info(nickname, mmr):
    soldier_info = [None] * 13

    soldier_info[1] = nickname
    soldier_info[2] = nickname
    soldier_info[7] = mmr

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


class SoldierWindow(QWidget, form_class):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        # kb.todo] exec_() main window 에서 대기 타고 싶은데 안됨.. 뭐가 문제인지 확인해보자
        # kb.todo] init 시 main window 가져와서 여기서 main 쪽 데이터를 set 하고 close 하는 구조.. 두 window 의 biz 가 섞이는게 매우 별로임
        self.main_window = parent
        self.setWindowTitle("용병 추가")
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

        # mmr 수동 입력 창
        self.mmr_edit.hide()

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
        if not nickname:
            self.show_alert_message("적어도 이름은 알아야 영혼을 불 태울 수 있죠", ALERT_MSG_TYPE_NORMAL)
            return

        if self.manual_radio.isChecked():  # mmr 수동 입력이라면
            mmr_str = self.mmr_edit.text()
            if not mmr_str:
                self.show_alert_message("아이언도 mmr은 있답니다.", ALERT_MSG_TYPE_NORMAL)
                return
            elif not check_valid_mmr(mmr_str):
                self.show_alert_message("우리집 고양이가 mmr을 입력했나보군요", ALERT_MSG_TYPE_NORMAL)
                return
            mmr = int(mmr_str)
        else:
            idx = self.mmr_combo_box.currentIndex()
            mmr = MMR_LIST[idx]['mmr']

        self.main_window.insert_soldier_to_player(nickname, make_soldier_info(nickname, mmr))
        self.close_soldier_window()

    def clicked_cancel_btn(self):
        self.close_soldier_window()

    def close_soldier_window(self):
        self.nickname_edit.clear()
        self.mmr_combo_box.setCurrentIndex(0)
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
        print("[kb.test] 폰트:  " + self.alert_label.font().family())
        self.timer.stop()

        if alert_type == ALERT_MSG_TYPE_NORMAL:
            self.timer.start(ALERT_MSG_TIMEOUT_NORMAL)
            self.alert_label.setStyleSheet(
                # kb.check 이상하게 연속으로 호출하면 Gulim 으로 바뀜;
                "font-family: Noto Sans Korean;"
                "color: red;"
            )
            self.alert_label.setText(msg)
            # 나중에 type 추가하던지-
        else:
            self.timer.start(ALERT_MSG_TIMEOUT_NORMAL)
            self.alert_label.setText(msg)

    def alert_timeout(self):
        self.alert_label.setText("")

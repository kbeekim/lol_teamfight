from functools import partial

from PyQt5.QtCore import Qt, pyqtSlot
from PyQt5.QtGui import QFont, QIcon
from PyQt5.QtWidgets import QPushButton
from PyQt5 import uic
from PyQt5.QtWidgets import *
import excel
import main_second_window
import soldier_window
import team_window
from playerinfo import *
from popup import ValvePopup, POPUP_TYPE_OK
from global_settings import *
from thread import Thread

WORKER_ORDER_FREQUENCY = 0
WORKER_ORDER_ALPHABET = 1
WORKER_ORDER_REVERSE_ALPHABET = 2

STATUS_BAR_TIMEOUT_DEFAULT = 2000
STATUS_BAR_TIMEOUT_SHORT = 1000
STATUS_BAR_TIMEOUT_WARN_SHORT = 1000
STATUS_BAR_TIMEOUT_WARN_LONG = 3000

STATUS_BAR_TYPE_NORMAL = 0
STATUS_BAR_TYPE_WARN = 1

UI_FILE_NAME = 'main_window.ui'

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]
excel_data = excel.ExcelClass()


class WindowClass(QMainWindow, form_class):
    SOLDIER_INFO_SUCCESS = 0
    SOLDIER_INFO_ERROR_FULL_PLAYER = PLAYER_INFO_ERROR_FULL_PLAYER
    SOLDIER_INFO_ERROR_SAME_NAME = PLAYER_INFO_ERROR_SAME_NAME

    def __init__(self):
        super().__init__()
        self.pd = None
        self.excel_thread = None
        self.setupUi(self)

        version = f'v{G_MAJOR_VERSION}.{G_MINOR_VERSION}'
        self.setWindowTitle("롤 인력사무소 " + version)

        # # excel data load
        if not excel_data.read_gspread_sheet8():
            self.show_message("MMR 로드 실패!\n(엑셀 sheet8 확인 필요)", STATUS_BAR_TYPE_WARN, 0)

        # 10명의 참가자 정보 List
        self.pl = PlayerInfoClass()
        self.player_btn_list = [None] * MAX_PLAYER_CNT

        # 인력 목록
        # SelectionMode = 0 = > NoSelection        # SelectionMode = 1 = > SingleSelection
        # SelectionMode = 2 = > MultiSelection     # SelectionMode = 3 = > ExtendedSelection
        # SelectionMode = 4 = > ContiguousSelection
        self.worker_list_widget.setSelectionMode(3)
        self.nick_list = None

        # 정렬 default 는 출석순
        self.load_worker_list(WORKER_ORDER_FREQUENCY)

        # 10명 GridLayout 안 player 버튼
        for x in range(5):
            for y in range(2):
                turn = (2 * x) + y
                self.player_btn_list[turn] = (QPushButton())
                self.set_style_player_btn(turn, str(turn + 1), PLAYER_FLAG_DEFAULT)

                self.player_btn_list[turn].setMaximumHeight(70)  # 버튼 높이 강제 조절
                self.player_btn_list[turn].setFont(QFont(G_FONT, 15))  # 폰트,크기 조절

                # 버튼의 idx를 알기위해 ObjectName으로 정함
                self.player_btn_list[turn].setObjectName(str(turn))
                # player 버튼
                self.player_btn_list[turn].clicked.connect(self.clicked_player_btn)
                self.gridLayout.addWidget(self.player_btn_list[turn], x, y)

        tab2 = main_second_window.SecondWindow(self, excel_data)
        self.tabWidget.addTab(tab2, '데이터 확인')
        
        # 초기화 버튼
        self.clear_btn.clicked.connect(self.clicked_clear_btn)
        self.clear_btn.setStyleSheet(
            "color: black;"
            "background-color: white;"
            "border: 1px solid white;"
        )

        # 데이터 로드 버튼
        self.load_btn.clicked.connect(self.clicked_load_btn)
        self.load_btn.setStyleSheet(
            "color: black;"
            "background-color: white;"
            "border: 1px solid white;"
        )

        # 투입 버튼
        self.insert_worker_btn.clicked.connect(self.clicked_insert_worker_btn)
        # 그룹 투입 버튼
        self.insert_group_btn.clicked.connect(self.clicked_insert_group_btn)
        # 분할 투입 버튼
        self.insert_division_btn.clicked.connect(self.clicked_insert_division_btn)
        # 용병 추가 버튼
        self.insert_soldier_btn.clicked.connect(self.clicked_insert_soldier_btn)
        self.soldier = None
        # 인력 리스트 더블 클릭 시
        self.worker_list_widget.itemDoubleClicked.connect(self.double_clicked_worker)
        # 검색 엔진
        self.search_edit.textChanged.connect(self.search_worker_filter)
        self.search_edit.setPlaceholderText("인력 검색")
        # 비우기 버튼
        self.search_clear_btn.clicked.connect(self.clicked_search_clear_btn)

        # 출발 (팀짜기) 버튼
        self.make_team_btn.setStyleSheet(
            "color: black;"
            "background-color: white;"
            "border: 2px solid rgb(255, 0, 110);"
            "border-radius: 5px;"
        )
        self.make_team_btn.hide()
        self.team = None
        self.make_team_btn.clicked.connect(self.clicked_make_team_btn)

        # 팀짜기 radio 버튼
        # 기본은 최소차이 방식
        self.team_min_diff_radio_btn.click()
        self.team_rank_radio_btn.hide()
        self.team_min_diff_radio_btn.hide()

        # 인력 정렬 radio 버튼
        # 기본은 엑셀 데이터 그대로 (출석순)
        self.frequency_order_radio_btn.click()
        self.frequency_order_radio_btn.clicked.connect(self.clicked_order_radbtn)
        self.alphabet_order_radio_btn.clicked.connect(self.clicked_order_radbtn)
        self.reverse_order_radio_btn.clicked.connect(self.clicked_order_radbtn)

        # ( x / 10 ) label
        self.refresh_player_cnt()

        # 상태바
        self.statusBar().setFont(QFont(G_FONT, 12))

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    def clicked_order_radbtn(self):
        if self.frequency_order_radio_btn.isChecked():
            self.load_worker_list(WORKER_ORDER_FREQUENCY)
        elif self.alphabet_order_radio_btn.isChecked():
            self.load_worker_list(WORKER_ORDER_ALPHABET)
        elif self.reverse_order_radio_btn.isChecked():
            self.load_worker_list(WORKER_ORDER_REVERSE_ALPHABET)
        else:
            self.load_worker_list(WORKER_ORDER_FREQUENCY)

        self.clicked_search_clear_btn()
        self.refresh_worker_list()

    def clicked_load_btn(self):
        # kbeekim) 기존의 그룹/분할은 취소되며 idx 도 변경될 수 있음

        # 데이터 로드 성공 시, 기존 리스트 유지를 위해 tmp_list
        tmp_list = []
        for idx in self.pl.get_all_player_info():
            if idx is None:
                continue
            # kbeekim) 23.02.10 닉네임 변경 대비, subname 추가
            if len(idx['SUBNAME']) != 0:
                tmp_list.append(idx['SUBNAME']) #연계
            else:
                tmp_list.append(idx['NICKNAME']) #연계

        if G_DEFINE_DEBUG_MODE:
            print("[kb.debug] load btn 시, 기존 tmp list : " + str(tmp_list))

        self.pd = QProgressDialog("데이터를 로딩 중 입니다.", None, 0, 0)
        self.pd.setWindowModality(Qt.ApplicationModal)

        self.pd.setWindowTitle(g_get_lol_random_speech_str())
        self.pd.setMinimumWidth(600)
        self.pd.show()

        self.excel_thread = Thread(excel_data, G_THREAD_READ_8)
        self.excel_thread.start()
        self.excel_thread.end_thread_signal.connect(partial(self.after_end_excel_thread, tmp_list))

    @pyqtSlot(bool)
    def after_end_excel_thread(self, tmp_list, excel_result):
        # kbeekim) 굳이 소멸 시키지 않아도 다음번 thread 생성 시, 자동 소멸이 된다.
        # 오히려 두 번 소멸 된다고 떠서 주석 처리..
        # self.excel_thread.delete()

        # progress dialog 취소
        self.pd.cancel()

        if excel_result:
            self.clicked_clear_btn()
            if self.frequency_order_radio_btn.isChecked():
                self.load_worker_list(WORKER_ORDER_FREQUENCY)
            elif self.alphabet_order_radio_btn.isChecked():
                self.load_worker_list(WORKER_ORDER_ALPHABET)
            elif self.reverse_order_radio_btn.isChecked():
                self.load_worker_list(WORKER_ORDER_REVERSE_ALPHABET)
            else:
                self.load_worker_list(WORKER_ORDER_FREQUENCY)

            for tmp_name in tmp_list:
                item = self.worker_list_widget.findItems(tmp_name, Qt.MatchExactly)
                if len(item) > 0:
                    self.insert_worker_to_player(item, PLAYER_FLAG_NORMAL)

            ValvePopup(POPUP_TYPE_OK, "확인창", "MMR 로드 성공!")
            self.show_message("", STATUS_BAR_TYPE_WARN, 0)
        else:
            # work_info는 갱신 이전 것으로 그냥 쓰는걸로!
            ValvePopup(POPUP_TYPE_OK, "확인창", "MMR 로드 실패!")
            self.show_message("MMR 로드 실패!\n(엑셀 sheet8 확인 필요)", STATUS_BAR_TYPE_WARN, 0)

    def clicked_search_clear_btn(self):
        self.search_edit.setText("")

    def refresh_player_cnt(self):
        cnt = self.pl.get_player_cnt()
        if G_DEFINE_EVENT_MODE:  # 싸베 버그
            self.player_cnt_label.setText(str(8) + "/" + str(MAX_PLAYER_CNT))
            self.player_cnt_label.setStyleSheet(
                "color: red;"
            )
        else:
            self.player_cnt_label.setText(str(cnt) + "/" + str(MAX_PLAYER_CNT))

        if cnt == MAX_PLAYER_CNT:
            self.make_team_btn.show()
            self.team_min_diff_radio_btn.show()
            self.team_rank_radio_btn.show()
        elif self.make_team_btn.isEnabled():
            self.make_team_btn.hide()
            self.team_min_diff_radio_btn.hide()
            self.team_rank_radio_btn.hide()

    def double_clicked_worker(self):
        self.clicked_insert_worker_btn()

    def search_worker_filter(self, filter_text):
        self.worker_list_widget.clear()

        for nl in self.nick_list:
            # kbeekim) 대소문자 구분 없이 검색하도록 한다.
            if filter_text.casefold() in nl.casefold():
                self.worker_list_widget.addItem(nl)

        self.refresh_worker_list()

    def clicked_make_team_btn(self):
        if not self.pl.get_player_cnt() == MAX_PLAYER_CNT:
            self.show_message("모든 정원이 차지 않았습니다.", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
            return

        if self.team_rank_radio_btn.isChecked():
            ret = self.pl.build_team_rank()
        elif self.team_min_diff_radio_btn.isChecked():
            ret = self.pl.build_team_min_diff()
        else:
            self.show_message("팀 선택 방식 오류", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
            return

        if ret == PLAYER_INFO_TEAM_BUILD_SUCCESS:
            self.show_message("성공!!!", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
            self.team = team_window.TeamWindow(self.pl.get_team_info(), self.pl.get_all_player_info())

            self.team.show()
            # kbeekim) team window 종료 후, 행정
            self.team.team_window_closed.connect(self.after_team_window)
        else:
            self.check_error_code_to_msg(ret)

    def after_team_window(self):
        del self.team

    def clicked_insert_soldier_btn(self):
        if self.pl.get_player_cnt() == MAX_PLAYER_CNT:
            self.show_message("더 이상 들어갈 자리가 없어보입니다.", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
            return

        # if not self.soldier:
        self.soldier = soldier_window.SoldierWindow(self)
        self.soldier.show()

    def clicked_clear_btn(self):
        for idx in range(MAX_PLAYER_CNT):
            self.pl.clear_player_info(idx)
            self.set_style_player_btn(idx, str(idx + 1), PLAYER_FLAG_DEFAULT)

        self.refresh_player_cnt()
        self.search_edit.setText("")
        self.refresh_worker_list()

    def clicked_player_btn(self):
        player_btn = self.sender()
        btn_idx = int(player_btn.objectName())

        # 해당 idx 에 해당하는 player_info 존재한다면 btn text 변환 및 list 초기화
        ret = self.pl.clear_player_info(btn_idx)

        if isinstance(ret, list):
            with_idx_list = ret
            if (len(with_idx_list)) != 0: # 같이 지워야 할게 있을 때
                for i in with_idx_list:
                    self.set_style_player_btn(i, str(i + 1), PLAYER_FLAG_DEFAULT)

            self.set_style_player_btn(btn_idx, str(btn_idx + 1), PLAYER_FLAG_DEFAULT)

            self.refresh_player_cnt()
            self.refresh_worker_list()
        elif isinstance(ret, int):
            self.check_error_code_to_msg(ret)
        else:
            self.show_message("[clicked_player_btn] UNKNOWN ERROR", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
            return

    def clicked_insert_worker_btn(self):
        self.insert_worker_to_player(self.worker_list_widget.selectedItems(), PLAYER_FLAG_NORMAL)

    def clicked_insert_group_btn(self):
        self.insert_worker_to_player(self.worker_list_widget.selectedItems(), PLAYER_FLAG_GROUP)

    def clicked_insert_division_btn(self):
        self.insert_worker_to_player(self.worker_list_widget.selectedItems(), PLAYER_FLAG_DIVISION)
        return

    def insert_worker_to_player(self, workers, player_flag):
        worker_info_list = []
        for i in range(len(workers)):
            worker_info_list.append(excel_data.get_worker_info_by_name(workers[i].text()))
        ret = self.pl.set_player_info(worker_info_list, player_flag)

        if isinstance(ret, list):
            player_idx_list = ret
            # return 값으로 player_list 의 idx를 받아 온다.
            for i, player_idx in enumerate(player_idx_list):
                # kbeekim) 23.02.10 닉네임 변경 대비, subname 추가
                nickname = worker_info_list[i]['NICKNAME']  # 연계
                subname = worker_info_list[i]['SUBNAME']  # 연계
                if len(subname) != 0:
                    tmp = f'{nickname}\n({subname})'
                else:
                    tmp = f'{nickname}'

                self.set_style_player_btn(player_idx, tmp, player_flag)

            # 성공했으니 list 비활성화
            for i in range(len(workers)):
                workers[i].setFlags(Qt.NoItemFlags)
            self.refresh_player_cnt()

        elif isinstance(ret, int):
            self.check_error_code_to_msg(ret)
        else:
            self.show_message("[insert_worker_to_player] UNKNOWN ERROR", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
            return

    def insert_soldier_to_player(self, soldier_info, tier):
        soldier_info_list = []
        soldier_name = soldier_info['NICKNAME']  # 연계
        soldier_mmr = soldier_info['MMR']  # 연계
        soldier_info_list.append(soldier_info)
        # return 값으로 player_list 의 idx를 받아 온다.

        ret = self.pl.set_player_info(soldier_info_list, PLAYER_FLAG_SOLDIER)

        if isinstance(ret, list): # 성공한 경우
            player_idx_list = ret
            if player_idx_list:
                player_idx = player_idx_list[0]  # 용병은 1명 추가이므로
                self.set_style_player_btn(player_idx, f'{soldier_name}\n({soldier_mmr})', PLAYER_FLAG_SOLDIER)
            self.refresh_player_cnt()
            # soldier window 로 결과값 전송
            return self.SOLDIER_INFO_SUCCESS
        elif isinstance(ret, int):  # 실패한 경우
            # soldier window 로 결과값 전송
            return ret
        else:
            self.show_message("[insert_soldier_to_player] UNKNOWN ERROR", STATUS_BAR_TYPE_WARN,
                              STATUS_BAR_TIMEOUT_WARN_SHORT)

    def set_style_player_btn(self, btn_idx, text, style):
        if style == PLAYER_FLAG_NORMAL:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 2px solid black;"
            )
        elif style == PLAYER_FLAG_GROUP:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 2px solid rgb(58, 134, 255);"
            )
        elif style == PLAYER_FLAG_DIVISION:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 2px solid rgb(251, 86, 7);"
            )
        elif style == PLAYER_FLAG_SOLDIER:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 2px solid rgb(0, 120, 62);"
            )
        else:
            self.player_btn_list[btn_idx].setStyleSheet(
                "color: black;"
                "background-color: white;"
                "border: 1px solid black;"
            )

        self.player_btn_list[btn_idx].setText(text)

    def refresh_worker_list(self):
        """ worker_list_widget 의 Flag (활성/비활성화) 를 갱신하는 함수
          - worker_list_widget 안 items 들의 닉네임과 player_list 를 비교하여
          - 이미 등록된 player 의 경우 Flag 를 비활성화한다.
          - worker_list_widget 이 변경되거나 player_list 가 변경될 때 호출해주면 된다.
        Args:
            -
        Returns:
            -
        """
        for idx in range(self.worker_list_widget.count()):
            item = self.worker_list_widget.item(idx)
            if self.pl.is_player_already_in(item.text()):
                item.setFlags(Qt.NoItemFlags)
            else:
                item.setFlags(Qt.ItemIsEnabled |
                              Qt.ItemIsSelectable)

    def load_worker_list(self, order):
        self.worker_list_widget.clear()
        tmp_list = excel_data.get_worker_name(0)

        if order == WORKER_ORDER_FREQUENCY:
            self.nick_list = tmp_list
        elif order == WORKER_ORDER_ALPHABET:
            self.nick_list = sorted(tmp_list)
        elif order == WORKER_ORDER_REVERSE_ALPHABET:
            self.nick_list = sorted(tmp_list, reverse=True)
        else:
            self.nick_list = tmp_list

        for nl in self.nick_list:
            self.worker_list_widget.addItem(str(nl))

    def check_error_code_to_msg(self, error_code):
        if error_code == PLAYER_INFO_ERROR_WRONG_IDX:
            self.show_message("IDX 가 이상합니다.", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
        elif error_code == PLAYER_INFO_ERROR_INFO_IS_EMPTY:
            self.show_message("해당하는 사용자 정보가 없습니다.", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
        elif error_code == PLAYER_INFO_ERROR_FULL_PLAYER:
            self.show_message("이대로 가다간 배가 침몰할 거 깉이요!   (10명 정원 초과)", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
        elif error_code == PLAYER_INFO_ERROR_NO_WORKER:
            self.show_message("인력 선택이 안되어있습니다.", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
        elif error_code == PLAYER_INFO_ERROR_GROUP_LESS_THEN_2:
            self.show_message("그룹이라면 적어도 두 명은 선택하셔야죠!", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
        elif error_code == PLAYER_INFO_ERROR_GROUP_MORE_THEN_5:
            self.show_message("한 팀에 최대 5명 입니다!", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
        elif error_code == PLAYER_INFO_ERROR_DIV_LESS_THEN_2:
            self.show_message("나 자신과의 싸움은 나중으로 미루죠   (2명 선택)", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
        elif error_code == PLAYER_INFO_ERROR_DIV_MORE_THEN_2:
            self.show_message("적을 많이 만들어서 좋을 건 없죠   (2명 선택)", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_SHORT)
        elif error_code == PLAYER_INFO_ERROR_TEAM_BUILD_FAIL:
            self.show_message("팀 결성 실패 (해당 조건을 만족할 순 없습니다)", STATUS_BAR_TYPE_WARN, STATUS_BAR_TIMEOUT_WARN_LONG)

    def show_message(self, msg, msg_type, timeout):
        if msg_type == STATUS_BAR_TYPE_NORMAL:
            self.statusBar().setStyleSheet(
                "color: black;"
            )
        elif msg_type == STATUS_BAR_TYPE_WARN:
            self.statusBar().setStyleSheet(
                "color: red;"
            )

        self.statusBar().showMessage(msg, timeout)

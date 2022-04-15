import os
from main import resource_path, DEFINE_DEBUG_MODE
import gspread

KEY_FILE_NAME = 'key.json'
PATH = resource_path(KEY_FILE_NAME, '/key/')


def next_available_row(sh, row):
    # row 시작은 1부터!
    str_list = list(filter(None, sh.col_values(row)))
    return str(len(str_list) + 1)


def is_float(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


class ExcelClass:
    def __init__(self):
        super().__init__()
        #   순번     닉네임        줄임말    MMR   참여 횟수
        #   NUM   NICKNAME    SHORTNICK   MMR    ENTRY
        self.worker_info = []
        self.total_member = 0

        self.read_gspread()

    def read_gspread(self):
        gc = gspread.service_account(filename= PATH)
        # self.doc = gc.open('Season.2022.SPRING')
        spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1DI5VKpTVu96r4gdvGvTeQOA5GArmhT-uUFDIR4fmdi0/edit#gid=352469473'
        doc = gc.open_by_url(spreadsheet_url)
        sheet8 = doc.worksheet("8.data")

        # sheet.get_all_records()는 개별 시트안에 있는 모든 데이터를 key, value값으로 반환 합니다. -> list of dicts
        # key는 스프레드 시트에서 첫번째 row가 key값이 되며, 2번째 row부터는 value값으로 가져 옮니다.
        # self.worker_info = sheet8.get_all_values()
        self.worker_info = sheet8.get_all_records()

        # 멤버 총원
        self.total_member = len(self.worker_info)

        if DEFINE_DEBUG_MODE:
            self.data_validation(sheet8)

    def get_worker_nickname(self):
        worker_nickname = []
        for i in range(0, self.total_member):
            worker_nickname.append(self.worker_info[i]['NICKNAME'])     # 연계

        # kbeekim) 엑셀에서 참여율 순으로 sort 하기로 함 22.04.12 (기획팀 협의)
        #return sorted(worker_nickname)
        return worker_nickname

    def get_worker_info_by_nickname(self, nickname):
        for i in range(0, self.total_member):
            if self.worker_info[i]['NICKNAME'] == nickname:            # 연계
                return self.worker_info[i]
        return None

    def get_worker_info_total_member(self):
        return self.total_member

    def data_validation(self, sh):
        ret = True
        next_row = next_available_row(sh, 1)  # 엑셀 1열은 NUM 값

        if int(next_row) < self.total_member:
            print("엑셀 행 수 일치하지 않음")
            ret = False
        elif sh.cell(next_row, 2).value is not None:
            print("2열에 뭔가 있음")
            ret = False
        elif sh.cell(next_row, 3).value is not None:
            print("3열에 뭔가 있음")
            ret = False
        elif sh.cell(next_row, 4).value is not None:
            print("4열에 뭔가 있음")
            ret = False
        elif sh.cell(next_row, 5).value is not None:
            print("5열에 뭔가 있음")
            ret = False

        mmr_value_list = sh.col_values(4) # 엑셀 4열이 MMR 값
        print("[kb.test] mmr_value_list :  " + str(mmr_value_list))
        for idx, mmr in enumerate(mmr_value_list):
            if idx == 0:
                continue
            if not is_float(mmr):
                print("mmr 값 이상 발견! : " + mmr)
                ret = False
                break
        return ret


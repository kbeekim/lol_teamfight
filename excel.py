import os
from datetime import date, timedelta, datetime

from main import resource_path, DEFINE_DEBUG_MODE
import gspread

SHEET5 = "5.MMR(복사)"
SHEET8 = "8.data"
KEY_FILE_NAME = 'key.json'
PATH = resource_path(KEY_FILE_NAME, '/key/')


def next_available_row(sh, col):
    # row/col 시작은 1부터!
    # str_list = list(filter(None, sh.col_values(col)))
    str_list = list(sh.col_values(col))
    return len(str_list) + 1


def is_float(num):
    try:
        float(num)
        return True
    except ValueError:
        return False


class ExcelClass:
    def __init__(self):
        super().__init__()

        self.end_row = None
        self.final_date_text = None
        self.worker_info = []
        self.total_member = 0

        self.sheet = None

    def read_gspread(self, sh_name):
        gc = gspread.service_account(filename=PATH)

        # fill in your gspread url
        spreadsheet_url = ''
        doc = gc.open_by_url(spreadsheet_url)

        try:
            self.sheet = doc.worksheet(sh_name)
        except Exception as e:
            print("오류 발생 - sheet 명칭 확인", e)
            return

        #   순번     닉네임        줄임말    MMR   참여 횟수
        #   NUM   NICKNAME    SHORTNICK   MMR    ENTRY
        if sh_name == SHEET8:
            # sheet.get_all_records()는 개별 시트안에 있는 모든 데이터를 key, value값으로 반환 합니다. -> list of dicts
            # key는 스프레드 시트에서 첫번째 row가 key값이 되며, 2번째 row부터는 value값으로 가져 옮니다.
            # self.worker_info = sheet8.get_all_values()
            self.worker_info = self.sheet.get_all_records()

            # 멤버 총원
            self.total_member = len(self.worker_info)
            self.data_validation(self.sheet)

        elif sh_name == SHEET5:
            self.end_row = next_available_row(self.sheet, 5) - 1  # 5 = E열

            # 마지막 행에 적혀 있는 문구 (ex] 4.24 내전50)
            last_text = self.sheet.cell(self.end_row, 5).value
            tmp = last_text.split('내전')

            last_cnt = tmp[1]

            now = datetime.now()
            # if now.hour < 6:
            #     base_date = date.today() - timedelta(1)
            # else:
            #     base_date = date.today()

            # kbeekim) 그냥 당일 날짜로 하자
            base_date = date.today()

            final_date = base_date.strftime('%m.%d')
            final_cnt = str(int(last_cnt) + 1)

            self.final_date_text = f'{final_date} 내전{final_cnt}.'

    def get_update_cell_pos(self):
        final_row = self.end_row + 1

        start_pos = f'E{final_row}'
        end_pos = f'G{final_row + 4}'

        return [start_pos, end_pos]

    def update_5_sheet(self, in_data):
        final_row = self.end_row + 1

        start_pos = f'E{final_row}'
        end_pos = f'G{final_row + 4}'
        self.sheet.update(f'{start_pos}:{end_pos}', in_data)

    def get_worker_nickname(self):
        worker_nickname = []
        for i in range(0, self.total_member):
            worker_nickname.append(self.worker_info[i]['NICKNAME'])  # 연계

        # kbeekim) 엑셀에서 참여율 순으로 sort 하기로 함 22.04.12 (기획팀 협의)
        # return sorted(worker_nickname)
        return worker_nickname

    def get_worker_info_by_nickname(self, nickname):
        for i in range(0, self.total_member):
            if self.worker_info[i]['NICKNAME'] == nickname:  # 연계
                return self.worker_info[i]
        return None

    def get_worker_info_total_member(self):
        return self.total_member

    def data_validation(self, sh):
        ret = True
        next_row = next_available_row(sh, 1)  # 엑셀 1열

        if next_row < self.total_member:
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

        mmr_value_list = sh.col_values(4)  # 엑셀 4열이 MMR 값

        if DEFINE_DEBUG_MODE:
            print("[kb.debug] mmr_value_list")
            for i in mmr_value_list:
                print(i)

        for idx, mmr in enumerate(mmr_value_list):
            # 첫 행은 "MMR" 문자이므로 제외
            if idx == 0:
                continue
            if not is_float(mmr):
                print("mmr 값 이상 발견! : " + mmr)
                ret = False
                break
        return ret

    def get_last_date_text(self):
        return self.final_date_text

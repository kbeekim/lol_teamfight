from datetime import date, timedelta, datetime

import gspread
from global_settings import *

SHEET4 = "4.게임결과(입력)"
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

        self.sh4_end_row = None
        self.sh5_end_row = None
        self.sh4_last_date_text = None
        self.sh5_last_date_text = None

        self.worker_info = []
        self.total_member = 0

        self.sheet4 = None
        self.sheet5 = None
        self.sheet8 = None

    # SHEET8 과 관련 함수들
    def read_gspread_sheet8(self):
        ret = False
        gc = gspread.service_account(filename=PATH)
        # self.doc = gc.open('파일 이름')
        spreadsheet_url = G_GSPREAD_URL
        doc = gc.open_by_url(spreadsheet_url)
        try:
            self.sheet8 = doc.worksheet(SHEET8)
        except Exception as e:
            print("오류 발생 - sheet 명칭 확인", e)
            return ret

        #   순번     닉네임        줄임말    MMR   참여 횟수
        #   NUM   NICKNAME    SHORTNICK   MMR    ENTRY

        # sheet.get_all_records()는 개별 시트안에 있는 모든 데이터를 key, value값으로 반환 합니다. -> list of dicts
        # key는 스프레드 시트에서 첫번째 row가 key값이 되며, 2번째 row부터는 value값으로 가져 옮니다.
        # self.worker_info = sheet8.get_all_values()
        self.worker_info = self.sheet8.get_all_records()

        # 멤버 총원
        self.total_member = len(self.worker_info)
        ret = self.data_validation(self.sheet8)
        return ret

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

        if G_DEFINE_DEBUG_MODE:
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

    # SHEET5 와 관련 함수들
    def read_gspread_sheet5(self):
        gc = gspread.service_account(filename=PATH)
        # self.doc = gc.open('Season.2022.SPRING')
        spreadsheet_url = G_GSPREAD_URL
        doc = gc.open_by_url(spreadsheet_url)
        try:
            self.sheet5 = doc.worksheet(SHEET5)
        except Exception as e:
            print("오류 발생 - sheet 명칭 확인", e)
            return

        self.sh5_end_row = next_available_row(self.sheet5, 5) - 1  # 5 => E열
        # 마지막 행에 적혀 있는 문구 (ex] 4.24 내전50)
        last_text = self.sheet5.cell(self.sh5_end_row, 5).value
        tmp = last_text.split('내전')
        last_cnt = tmp[1]
        if last_cnt.isdigit():
            final_cnt = str(int(last_cnt) + 1)
        else:
            final_cnt = "xx"

        # now = datetime.now()
        # if now.hour < 6:
        #     base_date = date.today() - timedelta(1)
        # else:
        #     base_date = date.today()

        # kbeekim) 그냥 당일 날짜로 하자
        base_date = date.today()
        final_date = base_date.strftime('%m.%d')

        self.sh5_last_date_text = f'{final_date} 내전{final_cnt}'

        #kb.todo sheet5 우선 무조건 True
        return True

    def get_sh5_update_cell_pos(self):
        final_row = self.sh5_end_row + 1

        start_pos = f'E{final_row}'
        end_pos = f'G{final_row + 4}'

        return [start_pos, end_pos]

    def update_5_sheet(self, in_data):
        final_row = self.sh5_end_row + 1

        start_pos = f'E{final_row}'
        end_pos = f'G{final_row + 4}'

        self.sheet5.update(f'{start_pos}:{end_pos}', in_data)

    def get_sh5_last_date_text(self):
        return self.sh5_last_date_text

    # SHEET4 와 관련 함수들
    def read_gspread_sheet4(self):
        gc = gspread.service_account(filename=PATH)
        # self.doc = gc.open('Season.2022.SPRING')
        spreadsheet_url = G_GSPREAD_URL
        doc = gc.open_by_url(spreadsheet_url)
        try:
            self.sheet4 = doc.worksheet(SHEET4)
        except Exception as e:
            print("오류 발생 - sheet 명칭 확인", e)
            return False

        # 연계) 엑셀 시트 4의 L열 "here"문구로 마지막 행을 찾는다.
        val = self.sheet4.col_values(12)
        try:
            self.sh4_end_row = val.index("here")
        except Exception as e:
            print("오류 발생 - sheet4 here 없음", e)
            top_list = self.sheet4.col_values(2)
            for cnt in range(len(top_list)):
                top_row = cnt * 8 + 2
                if len(top_list[top_row]) == 0:
                    self.sh4_end_row = top_row - 1
                    break


        if G_DEFINE_DEBUG_MODE:
            print(f"sheet4 base row: {self.sh4_end_row} 행")

        # 연계) A열에서 end_row - 8 (시트 4는 8행씩 반복됨) 하여 전 내전 문자열을 확인
        # (ex] 05.08 내전85)
        last_text = self.sheet4.cell(self.sh4_end_row - 8, 1).value
        if G_DEFINE_DEBUG_MODE:
            print(f"sheet4 before : {last_text}")
        tmp = last_text.split('내전')
        last_cnt = tmp[1]
        if last_cnt.isdigit():
            final_cnt = str(int(last_cnt) + 1)
        else:
            final_cnt = "xx"

        # kbeekim) 그냥 당일 날짜로 하자
        base_date = date.today()
        final_date = base_date.strftime('%m.%d')

        self.sh4_last_date_text = f'{final_date} 내전{final_cnt}'
        if G_DEFINE_DEBUG_MODE:
            print(f"sheet4 after : {self.sh4_last_date_text}")

        # kb.todo sheet4 우선 무조건 True
        return True

    def update_4_sheet(self, win_data, lose_data):
        final_row = self.sh4_end_row

        # 05.24 내전xx 입력
        self.sheet4.update(f'A{final_row}', self.sh4_last_date_text)

        # 승리 부분 입력
        start_pos = f'B{final_row + 2}'
        end_pos = f'C{final_row + 6}'
        self.sheet4.update(f'{start_pos}:{end_pos}', win_data)

        # 패배 부분 입력
        start_pos = f'H{final_row + 2}'
        end_pos = f'I{final_row + 6}'
        self.sheet4.update(f'{start_pos}:{end_pos}', lose_data)

    def get_sh4_update_cell_pos(self):
        return f"L{self.sh4_end_row}"

    def get_sh4_last_date_text(self):
        return self.sh5_last_date_text

        # champ_1 = self.sheet4.col_values(3)
        # blue_champs = list(filter(None, champ_1))
        #
        # champ_2 = self.sheet4.col_values(9)
        # red_champs = list(filter(None, champ_2))
        #
        # return blue_champs, red_champs
        # sheet4_data = self.sheet4get_all_values()

from datetime import date, timedelta, datetime

import gspread
from global_settings import *

SHEET4 = "4.게임결과(입력)"
SHEET5 = "5.MMR(복사)"
SHEET8 = "8.data"
KEY_FILE_NAME = 'key.json'
PATH = resource_path(KEY_FILE_NAME, '/key/')


def last_string_row(sh, col):
    """ 해당 열에서 글자가 있는 마지막 행의 값을 찾는다
    Args:
        - sh: 구글스프레드 시트 객체
        - col: 구글스프레드 열

    Returns:
        - 글자가 있는 마지막 행의 값
    """
    # row/col 시작은 1부터!
    # str_list = list(filter(None, sh.col_values(col)))
    str_list = list(sh.col_values(col))

    return len(str_list)


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
        """ gspread sheet8 을 읽어와  self.worker_info 를 설정한다.
        Args:
        Returns:
            - 결과 성공/실패
        """
        ret = True
        gc = gspread.service_account(filename=PATH)
        # self.doc = gc.open('파일 이름')
        spreadsheet_url = G_GSPREAD_URL
        doc = gc.open_by_url(spreadsheet_url)

        try:
            self.sheet8 = doc.worksheet(SHEET8)
        except Exception as e:
            print("오류 발생 - sheet 명칭 확인", e)
            return False

        prev_worker_info = self.worker_info
        #   순번     닉네임        줄임말    MMR   참여 횟수    부계정/닉변
        #   NUM   NICKNAME    SHORTNICK   MMR    ENTRY     SUBNAME

        # sheet.get_all_records()는 개별 시트안에 있는 모든 데이터를 key, value값으로 반환 합니다. -> list of dicts
        # key는 스프레드 시트에서 첫번째 row가 key값이 되며, 2번째 row부터는 value값으로 가져 옮니다.
        # self.worker_info = sheet8.get_all_values()
        tmp_worker_info = self.sheet8.get_all_records()

        # 총원
        tmp_total_member = len(tmp_worker_info)

        # sheet8 정합성 검증 1 (불필요 데이터 검출)
        for n in range(1, 5):
            final_row = last_string_row(self.sheet8, n) + 1  # 엑셀 n열의 마지막 행 + 1
            if not final_row - 2 == tmp_total_member:
                print(f"Sheet8 총 인원수({tmp_total_member})와 {n}열의 행 수({final_row - 2}) 일치하지 않음")
                ret = False
                break

        # sheet8 정합성 검증 2 (mmr 값)
        if ret:
            mmr_value_list = self.sheet8.col_values(4)  # 엑셀 4열이 MMR 값
            for idx, mmr in enumerate(mmr_value_list):
                # 첫 행은 "MMR" 문자이므로 제외
                if idx == 0:
                    continue
                if not is_float(mmr):
                    print("mmr 값 이상 발견! : " + mmr)
                    ret = False
                    break

        if ret:
            self.worker_info = tmp_worker_info
        else:
            self.worker_info = prev_worker_info

        # 멤버 총원
        self.total_member = len(self.worker_info)
        return ret

    def get_worker_name(self):
        """ self.work_info 리스트 에서 이름 리스트를 리턴한다.
        Args:
        Returns:
            - worker 이름 리스트
        """
        worker_name = []
        for i in range(0, self.total_member):
            # kbeekim) 23.02.10 닉네임 변경 대비, subname 추가
            if len(self.worker_info[i]['SUBNAME']) != 0:
                worker_name.append(self.worker_info[i]['SUBNAME'])  # 연계
            else:
                worker_name.append(self.worker_info[i]['NICKNAME'])  # 연계

        # kbeekim) 엑셀에서 참여율 순으로 sort 하기로 함 22.04.12 (기획팀 협의)
        # return sorted(worker_nickname)
        return worker_name

    def get_worker_info_by_name(self, name):
        """ self.work_info 의 네임(nickname or subname)과 일치하는 값이 있다면
        해당 worker_info 를 리턴한다.
        Args: name
        Returns: 네임과 일치하는 worker_info
                 없다면 None
        """
        # kbeekim) 23.02.10 닉네임 변경 대비, subname 추가
        for i in range(0, self.total_member):
            if len(self.worker_info[i]['SUBNAME']) != 0:
                if self.worker_info[i]['SUBNAME'] == name:  # 연계
                    return self.worker_info[i]
            else:
                if self.worker_info[i]['NICKNAME'] == name:  # 연계
                    return self.worker_info[i]
        return None

    def get_worker_info_total_member(self):
        """ worker_info 리스트의 길이(=총 인원) 리턴 
        Args: 
        Returns: 총 인원 수
        """
        return self.total_member

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    # SHEET5 와 관련 함수들
    def read_gspread_sheet5(self):
        """ gspread sheet5 을 읽어와  self.sh5_end_row/self.sh5_last_date_text 를 설정한다.
        Args:
        Returns:
            - 결과 성공/실패
        """
        gc = gspread.service_account(filename=PATH)
        # self.doc = gc.open('Season.2022.SPRING')
        spreadsheet_url = G_GSPREAD_URL
        doc = gc.open_by_url(spreadsheet_url)
        try:
            self.sheet5 = doc.worksheet(SHEET5)
        except Exception as e:
            print("오류 발생 - sheet 명칭 확인", e)
            return False

        self.sh5_end_row = last_string_row(self.sheet5, 5)  # 5 => E열
        # 마지막 행에 적혀 있는 문구 ([ex] 4.24 내전50)
        last_text = self.sheet5.cell(self.sh5_end_row, 5).value

        final_cnt = ""
        if '내전' in last_text:
            tmp = last_text.split('내전')
            last_cnt = tmp[1]

            if last_cnt.isdigit():
                final_cnt = str(int(last_cnt) + 1)
        else:
            final_cnt = "xx"

        # kbeekim) 그냥 당일 날짜로 하자
        base_date = date.today()
        final_date = base_date.strftime('%m.%d')

        self.sh5_last_date_text = f'{final_date} 내전{final_cnt}'

        # kbeekim) sheet5 우선 True
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

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    # SHEET4 와 관련 함수들
    def read_gspread_sheet4(self):
        """ gspread sheet4 을 읽어와  self.sh4_end_row/self.sh4_last_date_text 를 설정한다.
        Args:
        Returns:
            - 결과 성공/실패
        """
        gc = gspread.service_account(filename=PATH)
        # self.doc = gc.open('Season.2022.SPRING')
        spreadsheet_url = G_GSPREAD_URL
        doc = gc.open_by_url(spreadsheet_url)
        try:
            self.sheet4 = doc.worksheet(SHEET4)
        except Exception as e:
            print("오류 발생 - sheet 명칭 확인", e)
            return False

        # 엑셀 시트 4의 L열 "here"문구로 마지막 행을 찾는다. -> 제거
        # val = self.sheet4.col_values(12)
        
        # 연계) 엑셀 시트 4의 A1 기준 8칸마다 {날짜}+내전{순번} 문구가 빈 곳을 찾는다
        top_list = self.sheet4.col_values(1)
        for cnt in range(len(top_list)):
            row = cnt * 8
            if len(top_list[row]) == 0:
                self.sh4_end_row = row + 1
                break

        if G_DEFINE_DEBUG_MODE:
            print(f"sheet4 base row: {self.sh4_end_row} 행")
        if self.sh4_end_row is None:
            return False

        # 연계) A열에서 end_row - 8 (시트 4는 8행씩 반복됨) 하여 전 내전 문자열을 확인
        # ([ex] 05.08 내전85)
        final_cnt = "xx"
        if self.sh4_end_row - 8 < 1:
            final_cnt = "01"
        else:
            last_text = self.sheet4.cell(self.sh4_end_row - 8, 1).value
            if G_DEFINE_DEBUG_MODE:
                print(f"sheet4 before : {last_text}")
            if '내전' in last_text:
                tmp = last_text.split('내전')
                last_cnt = tmp[1]
                if last_cnt.isdigit():
                    final_cnt = str(int(last_cnt) + 1)

        # kbeekim) 그냥 당일 날짜로 하자
        base_date = date.today()
        final_date = base_date.strftime('%m.%d')

        self.sh4_last_date_text = f'{final_date} 내전{final_cnt}'
        if G_DEFINE_DEBUG_MODE:
            print(f"sheet4 after : {self.sh4_last_date_text}")

        # kbeekim) sheet4 우선 True
        return True

    def update_4_sheet(self, win_data, lose_data):
        if self.sh4_end_row is None:
            return False
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
        return self.sh4_last_date_text

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

    def get_analysis_data(self):
        # self.sh4_end_row 를 알고 있어야함! (sh4 read first)
        row = self.sh4_end_row - 1

        if G_DEFINE_DEBUG_MODE:
            print(f"sh4 마지막 row {row}")

        win_excel_range = f"B1:C{row}"
        win_list = []
        tmp_list = []
        win_data = self.sheet4.range(win_excel_range)

        #kb.todo 정합성 검증
        for n, cell in enumerate(win_data):
            if 4 <= n % (8*2) < 14:
                tmp_list.append(cell.value)
            elif n % (8*2) == 15:
                win_list.append(tmp_list)
                tmp_list = []

        lose_excel_range = f"H1:I{row}"
        lost_list = []
        tmp_list = []
        lose_data = self.sheet4.range(lose_excel_range)
        for n, cell in enumerate(lose_data):
            if 4 <= n % (8*2) < 14:
                tmp_list.append(cell.value)
            elif n % (8*2) == 15:
                lost_list.append(tmp_list)
                tmp_list = []

        if G_DEFINE_DEBUG_MODE:
            print(f"Win List {win_list}")
            print(f"Lost List {lost_list}")

        return win_list, lost_list

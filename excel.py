from asyncio.windows_events import NULL

import gspread
import pandas as pd


class ExcelClass:
    def __init__(self):
        super().__init__()
        #   [0]    [1]     [2]     [3]
        #   순번   닉네임    줄임말   MMR
        self.worker_info = []
        self.total_member = 0

        self.read_gspread()

    def read_gspread(self):
        gc = gspread.service_account(filename="./key/key.json")
        # self.doc = gc.open('Season.2022.SPRING')
        spreadsheet_url = 'https://docs.google.com/spreadsheets/d/1DI5VKpTVu96r4gdvGvTeQOA5GArmhT-uUFDIR4fmdi0/edit#gid=352469473'
        doc = gc.open_by_url(spreadsheet_url)
        sheet1 = doc.worksheet("8.data")

        # sheet.get_all_records()는 개별 시트안에 있는 모든 데이터를 key, value값으로 반환 합니다. -> list of dicts
        # key는 스프레드 시트에서 첫번째 row가 key값이 되며, 2번째 row부터는 value값으로 가져 옮니다.
        self.worker_info = sheet1.get_all_values()

        # 정규 멤버 총원
        self.total_member = len(self.worker_info) - 1

    def get_data(self):
        print(self.worker_info[1])
        return self.worker_info[1]

    def get_worker_nickname(self):
        worker_nickname = []
        for i in range(1, self.total_member + 1):
            # print(self.worker_info[i][1])
            worker_nickname.append(self.worker_info[i][1]) # 연계

        return sorted(worker_nickname)

    def get_worker_info_by_nickname(self, nickname):
        for i in range(1, self.total_member + 1):
            if self.worker_info[i][1] == nickname:
                return self.worker_info[i]
        return NULL

    def get_worker_info_total_member(self):
        return self.total_member



    # pandas 이용하기
        # values = sheet.get_all_values()
        # header, rows = values[0], values[1:]
        # df = pd.DataFrame(rows, columns=header)
        # print(df)

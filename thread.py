from concurrent.futures import thread
from time import sleep

from PyQt5.QtCore import QThread, QMutex, pyqtSignal
from global_settings import *


class Thread(QThread):
    dataLock = QMutex()
    end_thread_signal = pyqtSignal(bool, name='Thread')

    def __init__(self, excel_data, read_type):
        super().__init__()
        if G_DEFINE_DEBUG_MODE:
            print(f'Thread 생성 {self}')

        self.excel = excel_data
        self.read_type = read_type
        self.result = False

    def __del__(self):
        if G_DEFINE_DEBUG_MODE:
            print(f'Thread 소멸 {self}')

    def run(self):
        if self.read_type == G_THREAD_READ_8:
            self.result = self.excel.read_gspread_sheet8()
        elif self.read_type == G_THREAD_READ_5:
            self.result = self.excel.read_gspread_sheet5()
        elif self.read_type == G_THREAD_READ_4:
            self.result = self.excel.read_gspread_sheet4()
        elif self.read_type == G_THREAD_READ_4_5:
            #kb.todo 어차피 결과를 보진 않음
            self.excel.read_gspread_sheet5()
            self.result = self.excel.read_gspread_sheet4()

        self.end_thread_signal.emit(self.result)

    def delete(self):
        # Thread 소멸
        self.__del__()






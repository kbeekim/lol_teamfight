import excel
import main_window


class WorkerInfo():

    def __init__(self):
        super(WorkerInfo, self).__init__()

    def load_worker_info(self):
        ex = excel.ExcelClass()
        ex.get_data()
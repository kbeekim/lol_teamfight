from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget

import excel
from main import resource_path

UI_FILE_NAME = 'champ_window.ui'

PATH = resource_path(UI_FILE_NAME, '/img/ui/')
form_class = uic.loadUiType(PATH)[0]
excel_data = excel.ExcelClass()

champion = ["가렌", "갈리오", "갱플랭크", "그라가스", "그레이브즈", "그웬", "나르", "나미", "나서스", "노틸러스", "녹턴", "누누", "니달리", "니코", "다리우스", "다이애나", "드레이븐",
            "라이즈", "라칸", "람머스", "럭스", "럼블", "레나타글라스크", "레넥톤", "레오나", "렉사이", "렐", "렝가", "루시안", "룰루", "르블랑", "리븐", "리산드라", "리신", "릴리아",
            "마스터이", "마오카이", "말자하", "말파이트", "모데카이저", "모르가나", "문도박사", "미스포츈", "바드", "바루스", "바이", "베이가", "베인", "벡스", "벨코즈", "볼리베어",
            "브라움", "브랜드", "블라디미르", "블리츠크랭크", "비에고", "빅토르", "뽀삐", "사미라", "사이온", "사일러스", "샤코", "세나", "세라핀", "세주아니", "세트", "소나", "소라카",
            "쉔", "쉬바나", "스웨인", "스카너", "시비르", "신드라", "신지드", "신짜오", "쓰레쉬", "아리", "아무무", "아우렐리온솔", "아이번", "아지르", "아칼리", "아크샨", "아트록스", "아펠리우스",
            "알리스타", "애니", "애니비아", "애쉬", "야스오", "에코", "엘리스", "오공", "오른", "오리아나", "올라프", "요네", "요릭", "우디르", "우르곳", "워윅", "유미", "이렐리아",
            "이블린", "이즈리얼", "일라오이", "자르반4세", "자야", "자이라", "자크", "잔나", "잭스", "제드", "제라스", "제리", "제이스", "조이", "직스", "진", "질리언", "징크스",
            "초가스", "카르마", "카밀", "카사딘", "카서스", "카시오페아", "카이사", "카직스", "카타리나", "칼리스타", "케넨", "케이틀린", "케인", "케일", "코그모", "코르키", "퀸", "클레드",
            "키아나", "킨드레드", "타릭", "탈론", "탈리야", "탐켄치", "트런들", "트리스타나", "트린다미어", "트위스티드페이트", "트위치", "티모", "파이크", "판테온", "피들스틱", "피오라", "피즈",
            "하이머딩거", "헤카림"]

except_list = ["CHAMP", "게임시간"]

class ChampWindow(QWidget, form_class):
    def __init__(self, btn):
        super().__init__()
        self.setupUi(self)
        # windowModality 설정을 NonModal -> ApplicationModal 으로 설정하여 해당 창을 종료 전까지 다른 창 사용 못하게 설정
        self.setWindowModality(Qt.ApplicationModal)

        self.out_btn = btn
        self.champ_list = champion
        self.load_champ_list()

        # 검색 엔진
        self.search_champ_edit.textChanged.connect(self.search_champ_filter)
        self.search_champ_edit.setPlaceholderText("챔피언 검색")

        # 챔피언 목록
        # SelectionMode = 0 = > NoSelection        # SelectionMode = 1 = > SingleSelection
        # SelectionMode = 2 = > MultiSelection     # SelectionMode = 3 = > ExtendedSelection
        # SelectionMode = 4 = > ContiguousSelection
        self.champ_list_widget.setSelectionMode(1)
        # 인력 리스트 더블 클릭 시
        self.champ_list_widget.itemDoubleClicked.connect(self.double_clicked_champ)
        self.champ_ok_btn.clicked.connect(self.clicked_ok_btn)

        print(f"챔피언 숫자 : {len(self.champ_list)}")

        ex = excel.ExcelClass()
        check_champ, check_champ2 = ex.read_gspread_sheet4()
        print("***챔피언 오타 검사기***")

        for idx, n in enumerate(check_champ):
            if n in champion or n in except_list:
                continue
            else:
                print(f"오타 발견! (파랑) : {n} {idx}행")

        for idx, n in enumerate(check_champ2):
            if n in champion or n in except_list:
                continue
            else:
                print(f"오타 발견! (빨강) : {n} {idx}행")


    def search_champ_filter(self, filter_text):
        self.champ_list_widget.clear()

        print("")
        for cl in self.champ_list:
            # kbeekim) 대소문자 구분 없이 검색하도록 한다.
            if filter_text.casefold() in cl.casefold():
                self.champ_list_widget.addItem(cl)

    def load_champ_list(self):
        self.champ_list_widget.clear()

        for cl in self.champ_list:
            self.champ_list_widget.addItem(str(cl))

    def double_clicked_champ(self):
        champ_str = self.champ_list_widget.selectedItems()[0].text()
        player_str = self.out_btn.text().splitlines()[0]

        self.out_btn.setText(player_str + "\n" + champ_str)
        self.close()

    def clicked_ok_btn(self):
        if len(self.champ_list_widget.selectedItems()) != 1:
            print("이상해요")
            return

        champ_str = self.champ_list_widget.selectedItems()[0].text()
        player_str = self.out_btn.text().splitlines()[0]

        self.out_btn.setText(player_str + "\n" + champ_str)
        self.close()
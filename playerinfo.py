from global_settings import *

MAX_PLAYER_CNT = 10
MAX_TEAM_MEMBER = 5

PLAYER_FLAG_DEFAULT = 0
PLAYER_FLAG_NORMAL = 1
PLAYER_FLAG_GROUP = 2
PLAYER_FLAG_DIVISION = 3
PLAYER_FLAG_SOLDIER = 4

PLAYER_INFO_TEAM_BUILD_SUCCESS = 0
PLAYER_INFO_ERROR_WRONG_IDX = -1
PLAYER_INFO_ERROR_INFO_IS_EMPTY = -2
PLAYER_INFO_ERROR_FULL_PLAYER = -3
PLAYER_INFO_ERROR_NO_WORKER = -4
PLAYER_INFO_ERROR_GROUP_LESS_THEN_2 = -5
PLAYER_INFO_ERROR_GROUP_MORE_THEN_5 = -6
PLAYER_INFO_ERROR_DIV_LESS_THEN_2 = -7
PLAYER_INFO_ERROR_DIV_MORE_THEN_2 = -8
PLAYER_INFO_ERROR_SAME_NAME = -9
PLAYER_INFO_ERROR_TEAM_BUILD_FAIL = -10


def is_included_list(base_list, comp_list):
    """ base_list 안에 comp_list 가 포함되는지 확인하는 함수
    """
    for i in comp_list:
        if i in base_list:
            continue
        else:
            return False
    return True


def except_group_case(input_list, group_list):
    """ 팀 결성 경우의 수 중, 그룹 조건을 만족하는 경우를 찾는 함수
    Args:
        - input_list: 팀 결성 경우의 수에 대한 리스트 (3차 list)
            ex) [[[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]],   [[0, 1, 2, 3, 5], [4, 6, 7, 8, 9]], ..
            [[첫번째 경우의 수 A팀,  첫번째 경우의 수 B팀]], [[두번째 경우의 수 A팀,  두번째 경우의 수 B팀]] ..
            
        - group_list: 그룹 조건으로 묶인 player idx list
           ex) [8, 9]  : 8번 9번 참여자는 같은 팀이여야함

    Returns:
        - input_list 에서 그룹 조건을 제외하고 남은 list
    """
    ret_list = []
    for i in input_list:
        teamA_list = i[0]
        teamB_list = i[1]

        if is_included_list(teamA_list, group_list):
            ret_list.append(i)
        elif is_included_list(teamB_list, group_list):
            ret_list.append(i)

    return ret_list


def except_division_case(input_list, div_list):
    """ 팀 결성 경우의 수 중, 분할 조건을 만족하는 경우를 찾는 함수
    Args:
        - input_list: 팀 결성 경우의 수에 대한 리스트 (3차 list)
            ex) [[[0, 1, 2, 3, 4], [5, 6, 7, 8, 9]],   [[0, 1, 2, 3, 5], [4, 6, 7, 8, 9]], ..
              [[첫번째 경우의 수 A팀,  첫번째 경우의 수 B팀]], [[두번째 경우의 수 A팀,  두번째 경우의 수 B팀]] ..

        - div_list: 분할 조건으로 묶인 player idx list
           ex) [8, 9]  : 8번 9번 참여자는 다른 팀이여야함
    Returns:
        - input_list 에서 분할 조건을 제외하고 남은 list
    """
    ret_list = []

    for i in input_list:
        teamA_list = i[0]
        teamB_list = i[1]

        if is_included_list(teamA_list, [div_list[0]]):
            if is_included_list(teamB_list, [div_list[1]]):
                ret_list.append(i)
        elif is_included_list(teamB_list, [div_list[0]]):
            if is_included_list(teamA_list, [div_list[1]]):
                ret_list.append(i)

    return ret_list


class PlayerInfoClass:
    def __init__(self):
        self.player_info = [None] * MAX_PLAYER_CNT
        #     [Flag / Number / cnt ]
        # ex) [Group / 1 / 3 ] : 3명이 동시에 그룹 투입이 되어서 온 그룹1 인 참여자
        self.player_type = [None] * MAX_PLAYER_CNT

        # [A팀 idx, A팀 mmr 합, B팀 idx, B팀 mmr 합]
        self.team_info = []

        self.player_cnt = 0
        self.normal_number = 0
        self.group_number = 0
        self.division_number = 0

    def set_player_info(self, worker_info_list, flag):
        """ player_info 를 set 하는 함수
            - 10명의 player 의 info 를 set 한다. (player_info 는 worker_info 의 파생)
            - worker_list_widget 이 변경되거나 player_list 가 변경될 때 호출해주면 된다.
        Args:
            - worker_info_list: 요소가 worker_info 형식인 List
            - flag : 일반 / 그룹 / 분할 / 용병
        Returns:
            - 성공 시, 설정한 IDX 들의 List 를 반환
            - 실패 시, Int 형 ERROR CODE 반환
        """
        ret_idx_list = []
        worker_cnt = len(worker_info_list)
        # 예외처리 부분===================================================
        if worker_cnt == 0:
            return PLAYER_INFO_ERROR_NO_WORKER
        elif not self.get_player_cnt() + worker_cnt <= MAX_PLAYER_CNT:
            return PLAYER_INFO_ERROR_FULL_PLAYER

        if flag == PLAYER_FLAG_GROUP:
            if worker_cnt < 2:
                return PLAYER_INFO_ERROR_GROUP_LESS_THEN_2
            elif worker_cnt > MAX_TEAM_MEMBER:
                return PLAYER_INFO_ERROR_GROUP_MORE_THEN_5

        elif flag == PLAYER_FLAG_DIVISION:
            if worker_cnt < 2:
                return PLAYER_INFO_ERROR_DIV_LESS_THEN_2
            if worker_cnt > 2:
                return PLAYER_INFO_ERROR_DIV_MORE_THEN_2

        elif flag == PLAYER_FLAG_SOLDIER:
            if self.is_player_already_in(worker_info_list[0]['NICKNAME']):  # 용병 이름 연계
                return PLAYER_INFO_ERROR_SAME_NAME
        # 예외처리 부분===================================================

        if flag == PLAYER_FLAG_GROUP:
            self.group_number += 1
            number = self.group_number
        elif flag == PLAYER_FLAG_DIVISION:
            self.division_number += 1
            number = self.division_number
        else:
            self.normal_number += 1
            number = self.normal_number

        for worker_idx in range(worker_cnt):
            for idx in range(MAX_PLAYER_CNT):
                if self.is_empty_player_info(idx):
                    self.player_info[idx] = worker_info_list[worker_idx]
                    self.player_type[idx] = [flag, number, worker_cnt]

                    ret_idx_list.append(idx)
                    break

        self.player_cnt += worker_cnt

        return ret_idx_list

    def get_player_info(self, idx):
        """ player_info 를 get 하는 함수
        Args:
            - idx: 해당 idx 에 해당하는 player_info 반환
        Returns:
            - player_info
        """
        if not 0 <= idx < MAX_PLAYER_CNT:
            return PLAYER_INFO_ERROR_WRONG_IDX
        elif self.is_empty_player_info(idx):
            return PLAYER_INFO_ERROR_INFO_IS_EMPTY

        return self.player_info[idx]

    def get_all_player_info(self):
        return self.player_info

    def clear_player_info(self, idx):
        """ player_info 를 clear 하는 함수
        Args:
            - idx: 해당 idx 에 해당하는 player_info 를 제거함
            -      추가로 같은 그룹이거나 분할 flag 도 같이 제거한다.
        Returns:
            - 성공 시, 제거한 IDX 들의 List 를 반환
            - 실패 시, Int 형 ERROR CODE 반환
        """
        with_idx_list = []
        # 예외처리 부분===================================================
        if not 0 <= idx < MAX_PLAYER_CNT:
            return PLAYER_INFO_ERROR_WRONG_IDX

        if self.is_empty_player_info(idx):
            return []
        # 예외처리 부분===================================================

        need_more_clear = False
        if self.player_type[idx] is not None:
            if self.player_type[idx][0] == PLAYER_FLAG_GROUP:
                need_more_clear = True
                self.group_number -= 1
            elif self.player_type[idx][0] == PLAYER_FLAG_DIVISION:
                need_more_clear = True
                self.division_number -= 1
            else:
                self.normal_number -= 1

        # kbeekim) 그룹/분할 의 경우에는 같은 Flag 도 같이 지우자
        if need_more_clear:
            with_idx_list = self.get_same_flag_player_list(idx, False)
            for with_idx in with_idx_list:
                self.player_info[with_idx] = None
                self.player_type[with_idx] = None
                if not self.player_cnt == 0:
                    self.player_cnt -= 1

        # 본인 idx 정보 지우기
        self.player_info[idx] = None
        self.player_type[idx] = None
        if not self.player_cnt == 0:
            self.player_cnt -= 1

        return with_idx_list

    def get_same_flag_player_list(self, idx, include_self):
        """ 같은 flag 를 가진 IDX List 를 찾는 함수
        Args:
            - idx: 해당 idx 의 flag 와 동일한 것을 찾는다.
            - flag: return list 에 본인 idx 를 포함할 지 안할 지
        Returns:
            - IDX 들의 List 를 반환
        """
        ret_idx = []

        for i in range(MAX_PLAYER_CNT):
            try:
                if self.player_type[i] is not None:  # 주의! None 이면..
                    if i != idx:
                        if self.player_type[idx][0] == self.player_type[i][0]:
                            if self.player_type[idx][1] == self.player_type[i][1]:
                                if self.player_type[idx][2] == self.player_type[i][2]:
                                    ret_idx.append(i)
            except Exception as e:
                print("오류 발생 - player_type 확인 필요", e)

        if include_self:
            ret_idx.append(idx)
        ret_idx.sort()
        return ret_idx

    def is_player_already_in(self, in_text):
        """ 같은 닉네임을 가진 player 가 있는지 확인하는 함수
        Args:
            - in_text: 해당 문자열과 동일한 player 를 찾는다.
        Returns:
            - True / False
        """
        # worker_info 와 연계
        for idx in range(len(self.player_info)):
            try:
                if self.player_info[idx] is not None:  # 주의! None 이면..
                    # kbeekim) 23.02.10 닉네임 변경 대비, subname 추가
                    if len(self.player_info[idx]['SUBNAME']) != 0:
                        tmp_name = self.player_info[idx]['SUBNAME']   # 연계
                    else:
                        tmp_name = self.player_info[idx]['NICKNAME']  # 연계

                    if tmp_name == in_text:
                        return True
            except Exception as e:
                print("오류 발생 - player_info 확인 필요", e)

        return False

    def get_player_cnt(self):
        """ 총 참가자 수를 반환한다.
        """
        return self.player_cnt

    def is_empty_player_info(self, idx):
        """ 해당 idx 에 해당하는 참가자 정보가 비어있는지 확인하는 함수
        """
        if self.player_info[idx] is not None:
            return False
        else:
            return True

    def get_flag_cnt(self, flag):
        """ 해당 flag 에 해당하는 cnt 를 반환하는 함수
        """
        if flag == PLAYER_FLAG_GROUP:
            return self.group_number
        elif flag == PLAYER_FLAG_DIVISION:
            return self.division_number
        else:
            return self.normal_number

    def build_team_rank(self):
        """  mmr 순위 순서대로 팀을 짜는 함수
        * 1, 3, 6, 8, 10 vs 2, 4, 5, 7, 9 mmr 순위대로 팀을 짬
        * 그룹/분할 조건은 무시된다
        """
        self.clear_team_info()

        mmr_list = []
        teamA_list = []
        teamB_list = []

        for i in range(MAX_PLAYER_CNT):
            # mmr_list -> [idx, mmr 값], ...
            mmr_list.append([i, float(self.player_info[i]['MMR'])])  # MMR 연계

        # mmr 높은 순으로 정렬
        mmr_list.sort(key=lambda x: x[1], reverse=True)

        if G_DEFINE_DEBUG_MODE:
            print("[kb.debug] 순위 방식 팀짜기 mmr list")
            print(mmr_list)

        for idx, mlist in enumerate(mmr_list):
            if (idx == 0) | (idx == 2) | (idx == 5) | (idx == 7) | (idx == 9):
                teamA_list.append(mlist[0])  # player info 의 idx
            elif (idx == 1) | (idx == 3) | (idx == 4) | (idx == 6) | (idx == 8):
                teamB_list.append(mlist[0])  # player info 의 idx

        teamA_mmr = self.calc_team_mmr(teamA_list)
        teamB_mmr = self.calc_team_mmr(teamB_list)

        if G_DEFINE_DEBUG_MODE:
            print("[kb.debug] 순위 방식 팀짜기 team info (1, 2팀 나누기 전)")
            print(teamA_list)
            print(teamB_list)
            print(teamA_mmr)
            print(teamB_mmr)

        if teamA_mmr > teamB_mmr:
            self.team_info.append(teamB_list)
            self.team_info.append(teamB_mmr)
            self.team_info.append(teamA_list)
            self.team_info.append(teamA_mmr)
        else:
            self.team_info.append(teamA_list)
            self.team_info.append(teamA_mmr)
            self.team_info.append(teamB_list)
            self.team_info.append(teamB_mmr)

        return PLAYER_INFO_TEAM_BUILD_SUCCESS

    def build_team_min_diff(self):
        """ mmr 평균 차이가 가장 적도록 팀을 짜는 함수

        1) 10명 중에 5명을 뽑는 경우의 수 252 가지를 만든다. -- ret
        2) A팀 idx 와 B팀 idx 를 묶어 list 화  -- all_case_list (만들어 질 수 있는 모든 팀의 경우의 수 126가지)
        3) 그룹/분할 조건에 해당하는 경우의 수 만 남긴다.
        4) 남은 list 중에 팀별 mmr 값을 합산하여 가장 차이가 적은 경우의 수를 추출한다.
        5) 해당 팀 정보를 team_info 에 append 한다. -- team_info [1팀 팀원 idx, 1팀 mmr 합계, 2팀 팀원 idx, 2팀 mmr 합계]

        """
        all_case_list = []
        # ret = list(itertools.combinations(tmp, 5))
        ret = self.gen_comb([0, 1, 2, 3, 4, 5, 6, 7, 8, 9], 5)  # 10C5 경우의 수 -> 252 가지
        case_cnt = len(ret)  # 252  가지 경우의 수
        self.clear_team_info()  # kbeekim team_info 를 초기화 안하여 기존 team idx 를 유지하는 오류가 있었음.. 22.04.18

        #  all_case_list [[TeamA_idx_list_1, TeamB_idx_list_1], [TeamA_idx_list_2, TeamB_idx_list_2],...] 126 가지 경우의 수
        for idx in range(int(case_cnt / 2)):
            all_case_list.append([ret[idx], ret[case_cnt - 1 - idx]])
        ######################################################################################
        if G_DEFINE_DEBUG_MODE:
            print("[kb.debug] 팀짜기 시작 10명의 play_info")
            for i in self.player_info:
                print(i)

        group_list = []
        div_list = []
        for i in range(MAX_PLAYER_CNT):
            try:    # 주의
                if self.player_type[i][0] == PLAYER_FLAG_GROUP:
                    group_list.append(self.get_same_flag_player_list(i, True))
                elif self.player_type[i][0] == PLAYER_FLAG_DIVISION:
                    div_list.append(self.get_same_flag_player_list(i, True))
            except Exception as e:
                print("player_type 확인", e)

        group_list = list(set(list(map(tuple, group_list))))  # 2차 list 중복 제거 - 문제점: 안에 항목이 tuple 로 바뀜.
        tmp_list = all_case_list
        for g in group_list:
            # list(g) : 2차 list 중복 제거 - tuple 로 바뀌어 있어 list 로 변환해야함
            tmp_list = except_group_case(tmp_list, list(g))

        div_list = list(set(list(map(tuple, div_list))))  # 2차 list 중복 제거 - 문제점: 안에 항목이 tuple 로 바뀜.
        for d in div_list:
            # list(d) : 2차 list 중복 제거 - tuple 로 바뀌어 있어 list 로 변환해야함
            tmp_list = except_division_case(tmp_list, list(d))

        left_case_cnt = len(tmp_list)

        ######################################################################################

        if left_case_cnt > 0:
            mmr_diff = []
            for case in tmp_list:  # case : [ A팀 idx list, B팀 idx list]
                # 두 팀의 mmr 차이 절대값
                mmr_diff.append(abs(self.calc_team_mmr(case[0]) - self.calc_team_mmr(case[1])))

            final_idx = mmr_diff.index(min(mmr_diff))

            if self.calc_team_mmr(tmp_list[final_idx][0]) > self.calc_team_mmr(tmp_list[final_idx][1]):
                first_team_idx, second_team_idx = 1, 0
            else:
                first_team_idx, second_team_idx = 0, 1

            # 팀1 idx / 팀1 mmr 합계 / 팀2 idx / 팀2 mmr 합계
            self.team_info.append(tmp_list[final_idx][first_team_idx])
            self.team_info.append(self.calc_team_mmr(tmp_list[final_idx][first_team_idx]))
            self.team_info.append(tmp_list[final_idx][second_team_idx])
            self.team_info.append(self.calc_team_mmr(tmp_list[final_idx][second_team_idx]))

            return PLAYER_INFO_TEAM_BUILD_SUCCESS

        else:
            return PLAYER_INFO_ERROR_TEAM_BUILD_FAIL

    def calc_team_mmr(self, team_list):
        ret = 0
        for ele in team_list:
            try:    # 주의
                ret += (self.player_info[ele]['MMR'])  # mmr 연계
            except Exception as e:
                print("예외가 발생하였습니다." , e)

        return round(ret, 2)

    def gen_comb(self, arr, n):
        result = []
        if n == 0:
            return [[]]

        for i in range(0, len(arr)):
            elem = arr[i]
            rest_arr = arr[i + 1:]

            for C in self.gen_comb(rest_arr, n - 1):
                result.append([elem] + C)

        return result

    def get_team_info(self):
        return self.team_info

    def clear_team_info(self):
        self.team_info = []

import unittest
import pandas as pd
from src.core.searcher import DataSearcher

class TestDataSearcher(unittest.TestCase):
    def setUp(self):
        # [KR] 테스트용 데이터프레임 생성
        self.data = {
            'Name': ['Alice', 'Bob', 'Charlie', 'Alice'],
            'Role': ['Engineer', 'Manager', 'Designer', 'Intern'],
            'ID': [101, 102, 103, 104]
        }
        self.df = pd.DataFrame(self.data)

    def test_search_by_row_basic(self):
        """
        [KR] 기본 행 검색 테스트 (Case Insensitive)
        """
        # 'ali' 검색 -> Alice가 포함된 행 2개
        result = DataSearcher.search_dataframe(self.df, 'ali', by_column=False, case_sensitive=False)
        self.assertEqual(len(result), 2)
        self.assertTrue(all(result['Name'] == 'Alice'))

    def test_search_by_row_case_sensitive(self):
        """
        [KR] 대소문자 구분 행 검색 테스트
        """
        # 'ali' 검색 (Case Sensitive) -> 0개
        result = DataSearcher.search_dataframe(self.df, 'ali', by_column=False, case_sensitive=True)
        self.assertEqual(len(result), 0)

        # 'Ali' 검색 -> 2개
        result = DataSearcher.search_dataframe(self.df, 'Ali', by_column=False, case_sensitive=True)
        self.assertEqual(len(result), 2)

    def test_search_by_column_transpose(self):
        """
        [KR] 열 검색 (Transpose) 테스트
        """
        # 열 이름이 아닌 열의 '값'을 기준으로, 그 열 전체를 하나의 Row로 취급하여 검색
        # 원본:
        #   Name     Role      ID
        # 0 Alice    Engineer  101
        # 1 Bob      Manager   102
        # ...

        # Transposed:
        #       0       1       2         3
        # Name  Alice   Bob     Charlie   Alice
        # Role  Engineer Manager Designer Intern
        # ID    101     102     103       104

        # 'Manager' 검색 -> Role 행(원본의 열)이 나와야 함
        result = DataSearcher.search_dataframe(self.df, 'Manager', by_column=True, case_sensitive=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.index[0], 'Role') # 결과의 인덱스는 원본 컬럼명이어야 함

    def test_search_numeric(self):
        """
        [KR] 숫자 데이터 검색 테스트
        """
        # '102' 검색
        result = DataSearcher.search_dataframe(self.df, '102', by_column=False, case_sensitive=False)
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Name'], 'Bob')

    def test_empty_search(self):
        """
        [KR] 빈 검색어 처리 테스트
        """
        result = DataSearcher.search_dataframe(self.df, '', by_column=False)
        self.assertTrue(result.empty)

if __name__ == '__main__':
    unittest.main()

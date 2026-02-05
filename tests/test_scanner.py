import unittest
import os
import shutil
import pandas as pd
from pathlib import Path
from src.core.scanner import FileScanner

class TestFileScanner(unittest.TestCase):
    def setUp(self):
        # [KR] 테스트용 임시 디렉토리 및 파일 생성
        self.test_dir = Path("test_env_scanner")
        self.test_dir.mkdir(exist_ok=True)

        # [KR] CSV 파일 생성
        self.csv_path = self.test_dir / "data.csv"
        df_csv = pd.DataFrame({'col1': range(10), 'col2': range(10)})
        df_csv.to_csv(self.csv_path, index=False, encoding='utf-8-sig')

        # [KR] 엑셀 파일 생성
        self.xlsx_path = self.test_dir / "data.xlsx"
        df_xlsx = pd.DataFrame({'colA': ['A', 'B'], 'colB': [1, 2]})
        df_xlsx.to_excel(self.xlsx_path, index=False)

        # [KR] 지원되지 않는 파일 (.txt)
        (self.test_dir / "ignore.txt").write_text("ignore me")

        self.scanner = FileScanner()

    def tearDown(self):
        # [KR] 테스트 후 임시 디렉토리 삭제
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_get_supported_files(self):
        """
        [KR] 지원되는 확장자만 필터링하여 스캔하는지 테스트
        """
        paths = [str(self.test_dir)]
        found = self.scanner.get_supported_files(paths)

        found_names = [Path(f).name for f in found]
        self.assertIn("data.csv", found_names)
        self.assertIn("data.xlsx", found_names)
        self.assertNotIn("ignore.txt", found_names)
        self.assertEqual(len(found), 2)

    def test_read_csv_chunks(self):
        """
        [KR] CSV 파일 청크 로딩 테스트
        """
        chunks = list(self.scanner.read_file_chunks(str(self.csv_path), chunksize=5))
        # 10 rows / 5 chunksize = 2 chunks
        self.assertEqual(len(chunks), 2)
        self.assertIn('data', chunks[0])
        self.assertIn('sheet_name', chunks[0])
        self.assertEqual(chunks[0]['sheet_name'], "data.csv")
        self.assertEqual(len(chunks[0]['data']), 5)

    def test_read_excel_chunks(self):
        """
        [KR] 엑셀 파일 청크 로딩 테스트
        """
        chunks = list(self.scanner.read_file_chunks(str(self.xlsx_path), chunksize=1))
        # 2 rows / 1 chunksize = 2 chunks
        self.assertEqual(len(chunks), 2)
        self.assertIn('Sheet1', chunks[0]['sheet_name'])
        # Note: pandas default sheet name is 'Sheet1'
        self.assertEqual(len(chunks[0]['data']), 1)

    def test_file_not_found(self):
        """
        [KR] 존재하지 않는 파일 읽기 시도 시 에러 발생 테스트
        """
        with self.assertRaises(FileNotFoundError):
            next(self.scanner.read_file_chunks("non_existent.csv"))

if __name__ == '__main__':
    unittest.main()

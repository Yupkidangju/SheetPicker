import unittest
from unittest.mock import MagicMock, patch
import time
from src.core.workers import SearchWorker

class TestSearchWorker(unittest.TestCase):
    def setUp(self):
        # [KR] Mock 데이터 및 환경 설정
        self.files = ["dummy.csv"]
        self.keyword = "test"
        self.worker = SearchWorker(self.files, self.keyword, by_column=False, case_sensitive=False)

        # [KR] Signal Mocking
        self.worker.result_found = MagicMock()
        self.worker.progress_updated = MagicMock()
        self.worker.finished_task = MagicMock()
        self.worker.error_occurred = MagicMock()

    @patch("src.core.workers.FileScanner")
    @patch("src.core.workers.DataSearcher")
    def test_run_flow(self, mock_searcher, mock_scanner):
        """
        [KR] Worker의 실행 흐름 및 시그널 방출 테스트
        """
        # [KR] Scanner Mock 설정
        mock_scanner_instance = mock_scanner.return_value
        # 1개의 청크 데이터 반환
        mock_df = MagicMock()
        mock_scanner_instance.read_file_chunks.return_value = iter([{'sheet_name': 'Sheet1', 'data': mock_df}])

        # [KR] Searcher Mock 설정
        # 검색 결과로 1개의 행이 있는 데이터프레임 반환
        mock_result_df = MagicMock()
        mock_result_df.empty = False
        mock_result_df.columns = ["col1"]
        mock_result_df.itertuples.return_value = iter([("val1",)]) # 1 row

        # Mock iterrows for baseline test compatibility
        mock_row = MagicMock()
        mock_row.to_dict.return_value = {"col1": "val1"}
        mock_result_df.iterrows.return_value = iter([(0, mock_row)])

        mock_searcher.search_dataframe.return_value = mock_result_df
        mock_searcher.format_result_row.return_value = "Preview Data"

        # [KR] 스레드 실행 (동기적으로 run 호출하여 테스트)
        self.worker.scanner = mock_scanner_instance # 주입
        self.worker.run()

        # [KR] 검증
        # 1. Scanner가 호출되었는지
        mock_scanner_instance.read_file_chunks.assert_called_with("dummy.csv")

        # 2. Searcher가 호출되었는지
        mock_searcher.search_dataframe.assert_called()

        # 3. 결과 시그널이 방출되었는지
        self.worker.result_found.emit.assert_called()
        args = self.worker.result_found.emit.call_args[0][0]
        self.assertIsInstance(args, list)
        self.assertTrue(len(args) > 0)
        self.assertEqual(args[0]['file'], 'dummy.csv')
        self.assertEqual(args[0]['preview'], 'Preview Data')

        # 4. 완료 시그널이 방출되었는지
        self.worker.finished_task.emit.assert_called_once()

    @patch("src.core.workers.FileScanner")
    def test_stop_worker(self, mock_scanner):
        """
        [KR] 작업 중단(stop) 기능 테스트
        """
        self.worker.stop()
        self.assertFalse(self.worker._is_running)
        # 실행 즉시 중단되어야 함 (Scanner loop가 돌지 않아야 함)
        self.worker.run()
        # progress_updated는 "Starting..." 한번 호출될 수 있음
        # 하지만 Scanner 루프 내부 진입은 막히거나 즉시 탈출해야 함

if __name__ == '__main__':
    unittest.main()

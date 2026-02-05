import unittest
from unittest.mock import patch, MagicMock
from src.utils.clipboard_manager import ClipboardManager

class TestClipboardManager(unittest.TestCase):
    def test_format_for_clipboard(self):
        """
        [KR] 데이터 포맷팅 테스트 (TSV 형식 확인)
        """
        rows = [
            {'file': 'file1.xlsx', 'sheet': 'Sheet1', 'data': 'Row1Data'},
            {'file': 'file2.csv', 'sheet': 'file2.csv', 'data': 'Row2Data\nWithNewline'}
        ]

        expected = "Source File\tSheet Name\tRow Data\n" \
                   "file1.xlsx\tSheet1\tRow1Data\n" \
                   "file2.csv\tfile2.csv\tRow2Data WithNewline" # Newline replaced by space

        result = ClipboardManager.format_for_clipboard(rows)
        self.assertEqual(result, expected)

    def test_format_empty(self):
        """
        [KR] 빈 데이터 처리 테스트
        """
        result = ClipboardManager.format_for_clipboard([])
        self.assertEqual(result, "")

    @patch('src.utils.clipboard_manager.pyperclip.copy')
    def test_copy_success(self, mock_copy):
        """
        [KR] 클립보드 복사 호출 성공 테스트
        """
        text = "test\tdata"
        success = ClipboardManager.copy_to_clipboard(text)

        self.assertTrue(success)
        mock_copy.assert_called_once_with(text)

    @patch('src.utils.clipboard_manager.pyperclip.copy', side_effect=Exception("Clipboard Error"))
    def test_copy_failure(self, mock_copy):
        """
        [KR] 클립보드 복사 실패(예외) 처리 테스트
        """
        success = ClipboardManager.copy_to_clipboard("data")
        self.assertFalse(success)

if __name__ == '__main__':
    unittest.main()

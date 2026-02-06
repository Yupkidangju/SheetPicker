import os
import pytest
from src.core.scanner import FileScanner

xlwt = pytest.importorskip("xlwt")

@pytest.fixture
def xls_file(tmp_path):
    filename = tmp_path / "test.xls"
    wb = xlwt.Workbook()
    # Create 2 sheets
    for i in range(2):
        ws = wb.add_sheet(f'Sheet{i}')
        ws.write(0, 0, 'Name')
        ws.write(1, 0, f'Data_{i}')
    wb.save(str(filename))
    return str(filename)

def test_read_xls_optimized(xls_file):
    scanner = FileScanner()

    # Read chunks
    chunks = list(scanner.read_file_chunks(xls_file, chunksize=10))

    # Verify we got data from both sheets
    assert len(chunks) == 2

    sheet_names = [c['sheet_name'] for c in chunks]
    assert 'Sheet0' in sheet_names
    assert 'Sheet1' in sheet_names

    # Verify content
    for c in chunks:
        df = c['data']
        assert 'Name' in df.columns
        # Verify data presence
        # Sheet0 should have Data_0, Sheet1 should have Data_1
        val = df['Name'].iloc[0]
        sheet = c['sheet_name']
        if sheet == 'Sheet0':
            assert val == 'Data_0'
        elif sheet == 'Sheet1':
            assert val == 'Data_1'

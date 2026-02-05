import pytest
import pandas as pd
from src.core.scanner import FileScanner
from openpyxl import Workbook
import csv

@pytest.fixture
def temp_files(tmp_path):
    # Create a dummy CSV
    csv_file = tmp_path / "test.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(["Name", "Age"])
        writer.writerow(["Alice", "30"])
        writer.writerow(["Bob", "25"])

    # Create a dummy Excel
    xlsx_file = tmp_path / "test.xlsx"
    wb = Workbook()
    ws = wb.active
    ws.append(["Name", "Age"])
    ws.append(["Charlie", "35"])
    wb.save(xlsx_file)

    return [str(csv_file), str(xlsx_file)]

def test_get_supported_files(tmp_path, temp_files):
    scanner = FileScanner()

    # Test directory scan
    found = scanner.get_supported_files([str(tmp_path)])
    assert len(found) == 2
    assert any("test.csv" in f for f in found)
    assert any("test.xlsx" in f for f in found)

def test_read_csv_chunks(temp_files):
    scanner = FileScanner()
    csv_file = [f for f in temp_files if f.endswith('.csv')][0]

    chunks = list(scanner.read_file_chunks(csv_file, chunksize=1))
    assert len(chunks) == 2 # 2 rows, chunksize 1 -> 2 chunks

    df1 = chunks[0]['data']
    assert df1.iloc[0]['Name'] == "Alice"

def test_read_xlsx_chunks(temp_files):
    scanner = FileScanner()
    xlsx_file = [f for f in temp_files if f.endswith('.xlsx')][0]

    # openpyxl chunk reading logic is based on buffer size
    chunks = list(scanner.read_file_chunks(xlsx_file, chunksize=10))
    assert len(chunks) >= 1

    df = chunks[0]['data']
    assert "Charlie" in df['Name'].values

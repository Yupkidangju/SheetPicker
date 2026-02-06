import pytest
import pandas as pd
from src.core.searcher import DataSearcher

@pytest.fixture
def sample_df():
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Email': ['alice.user@example.com', 'bob@test.org', 'charlie@example.com'],
        'Phone': ['123-456', '987-654', '555-555']
    }
    return pd.DataFrame(data)

def test_search_literal(sample_df):
    # Basic search
    res = DataSearcher.search_dataframe(sample_df, "Alice")
    assert len(res) == 1
    assert res.iloc[0]['Name'] == 'Alice'

    # Case insensitive
    # "BOB" searches for "Bob" (Name) and "bob@..." (Email)
    res = DataSearcher.search_dataframe(sample_df, "BOB", case_sensitive=False)
    assert len(res) == 1

    # Case sensitive fail
    # "BOB" should not match "Bob" or "bob@..."
    res = DataSearcher.search_dataframe(sample_df, "BOB", case_sensitive=True)
    assert len(res) == 0

def test_search_regex(sample_df):
    # Regex search for email domain
    res = DataSearcher.search_dataframe(sample_df, r"@example\.com", use_regex=True)
    assert len(res) == 2 # Alice and Charlie

    # Regex search for digits
    res = DataSearcher.search_dataframe(sample_df, r"\d{3}-\d{3}", use_regex=True)
    assert len(res) == 3

def test_column_targeting(sample_df):
    # Target only Name column (should find Alice)
    res = DataSearcher.search_dataframe(sample_df, "Alice", target_columns=["Name"])
    assert len(res) == 1

    # Target only Email column (should NOT find "Alice" because case_sensitive=True to distinguish from email content if needed,
    # but here let's use a keyword that is ONLY in Name)

    # "Charlie" is in Name. "charlie@..." is in Email.
    # If we search "Charlie" (Capital C) in Email with case_sensitive=True, it should fail.
    res = DataSearcher.search_dataframe(sample_df, "Charlie", target_columns=["Email"], case_sensitive=True)
    assert len(res) == 0

    # Target Email column (should find domain)
    res = DataSearcher.search_dataframe(sample_df, "test.org", target_columns=["Email"])
    assert len(res) == 1

def test_search_by_column(sample_df):
    # Transpose search
    res = DataSearcher.search_dataframe(sample_df, "Alice", by_column=True)
    assert len(res) >= 1
    assert 'Name' in res.index

def test_format_result_row(sample_df):
    row_series = sample_df.iloc[0]
    formatted = DataSearcher.format_result_row(row_series)
    # Alice | alice.user@example.com | 123-456
    # Truncated at 20 chars per val. alice... is 22 chars.
    # alice.user@example.c
    expected = "Alice | alice.user@example.c | 123-456"
    assert formatted == expected

    # Test tuple input
    row_tuple = ('Alice', 'alice.user@example.com', '123-456')
    formatted_tuple = DataSearcher.format_result_row(row_tuple)
    assert formatted_tuple == expected

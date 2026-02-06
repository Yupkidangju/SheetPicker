import pytest
import pandas as pd
from src.core.searcher import DataSearcher

@pytest.fixture
def sample_df():
    data = {
        'Name': ['Alice', 'Bob', 'Charlie'],
        'Info': ['Seoul Gangnam', 'Seoul Gangbuk', 'Busan Haeundae']
    }
    return pd.DataFrame(data)

def test_smart_search_and(sample_df):
    # "Seoul Gangnam" -> AND logic
    res = DataSearcher.search_dataframe(sample_df, "Seoul Gangnam")
    assert len(res) == 1
    assert res.iloc[0]['Name'] == 'Alice'

def test_smart_search_or(sample_df):
    # "Gangnam|Busan" -> OR logic
    res = DataSearcher.search_dataframe(sample_df, "Gangnam|Busan")
    assert len(res) == 2 # Alice(Gangnam) + Charlie(Busan)

def test_smart_search_not(sample_df):
    # "Seoul -Gangnam" -> Seoul AND NOT Gangnam
    res = DataSearcher.search_dataframe(sample_df, "Seoul -Gangnam")
    assert len(res) == 1
    assert res.iloc[0]['Name'] == 'Bob'

def test_smart_search_exact_quote(sample_df):
    # Quotes handling by shlex
    # "Seoul Gangnam" treated as one token in shlex
    res = DataSearcher.search_dataframe(sample_df, '"Seoul Gangnam"')
    assert len(res) == 1
    assert res.iloc[0]['Name'] == 'Alice'

import pytest
import pandas as pd
import time
from src.core.searcher import DataSearcher

def test_redos_protection():
    """
    [KR] ReDoS(Regular Expression Denial of Service) 보호 기능을 테스트합니다.
    취약한 정규식 패턴을 사용했을 때 google-re2가 빠르게 처리하는지 검증합니다.
    """
    # Vulnerable pattern: (a+)+$
    pattern = "(a+)+$"
    # Payload designed to cause catastrophic backtracking in standard re
    # 25 characters is usually enough to cause seconds of delay in re,
    # but let's be reasonable for a unit test (should be instant with re2)
    payload = "a" * 30 + "!"

    df = pd.DataFrame({'data': [payload]})

    start_time = time.time()

    # Perform search with regex enabled
    # This uses re2 internally now
    result = DataSearcher.search_dataframe(df, pattern, use_regex=True)

    elapsed = time.time() - start_time

    # Verify performance
    # With re2, this should be sub-millisecond.
    # With standard re, it would be > 5-10 seconds or hang.
    # We set a generous upper bound of 1.0 second to account for CI environments.
    assert elapsed < 1.0, f"Search took too long ({elapsed:.4f}s), ReDoS protection might be failing."

    # Should not match (because of '!')
    assert result.empty

def test_complex_regex_safety():
    """
    [KR] 복잡한 정규식 처리 안전성 테스트
    """
    # Valid complex regex (email pattern)
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    data = ["test@example.com", "invalid-email", "user.name+tag@sub.domain.co.kr"]
    df = pd.DataFrame({'email': data})

    result = DataSearcher.search_dataframe(df, pattern, use_regex=True)

    assert len(result) == 2
    assert "test@example.com" in result['email'].values
    assert "user.name+tag@sub.domain.co.kr" in result['email'].values

def test_invalid_regex_safety():
    """
    [KR] 잘못된 정규식 입력 시 크래시 방지 테스트
    """
    pattern = "[" # Unclosed bracket
    df = pd.DataFrame({'data': ["test"]})

    # Should not crash, just return empty
    result = DataSearcher.search_dataframe(df, pattern, use_regex=True)
    assert result.empty

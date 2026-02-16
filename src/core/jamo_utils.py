"""
[v2.0.0] 한글 자모 분해 유틸리티
한글 초성 검색을 위한 자모 분해, 초성 추출, 매칭 기능을 제공합니다.
외부 라이브러리 없이 유니코드 연산만으로 구현되어 의존성이 없습니다.
"""

# 한글 유니코드 범위 상수
HANGUL_BASE = 0xAC00  # '가'
HANGUL_END = 0xD7A3   # '힣'

# 초성, 중성, 종성 개수
JUNG_COUNT = 21
JONG_COUNT = 28

# 초성 목록 (19개, 유니코드 순서)
CHO_LIST = [
    'ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ',
    'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
]

# 초성 자음 문자의 집합 (빠른 판별용)
CHOSUNG_SET = set(CHO_LIST)


def is_hangul_syllable(char: str) -> bool:
    """한글 완성형 음절 여부 확인 ('가'~'힣')"""
    return HANGUL_BASE <= ord(char) <= HANGUL_END


def is_chosung_char(char: str) -> bool:
    """단독 초성(자음) 문자 여부 확인 ('ㄱ'~'ㅎ')"""
    return char in CHOSUNG_SET


def decompose(char: str):
    """
    한글 음절을 초성, 중성, 종성 인덱스로 분해합니다.
    한글이 아닌 경우 None을 반환합니다.

    Returns:
        tuple(int, int, int) 또는 None
    """
    if not is_hangul_syllable(char):
        return None
    code = ord(char) - HANGUL_BASE
    cho = code // (JUNG_COUNT * JONG_COUNT)
    jung = (code % (JUNG_COUNT * JONG_COUNT)) // JONG_COUNT
    jong = code % JONG_COUNT
    return (cho, jung, jong)


def extract_chosung(text: str) -> str:
    """
    텍스트에서 초성만 추출합니다.
    한글 음절 → 초성, 비한글 → 그대로 유지.

    예: '홍길동' → 'ㅎㄱㄷ', 'Hello홍' → 'Helloㅎ'
    """
    result = []
    for char in text:
        if is_hangul_syllable(char):
            cho_idx = decompose(char)[0]
            result.append(CHO_LIST[cho_idx])
        else:
            result.append(char)
    return ''.join(result)


def is_chosung_query(text: str) -> bool:
    """
    입력 텍스트가 모두 초성(자음)으로만 이루어져 있는지 확인합니다.
    공백은 무시합니다. 빈 문자열은 False를 반환합니다.

    예: 'ㅎㄱㄷ' → True, 'ㅎ길ㄷ' → False
    """
    if not text or not text.strip():
        return False
    for char in text:
        if char == ' ':
            continue
        if not is_chosung_char(char):
            return False
    return True


def match_chosung(query: str, text: str) -> bool:
    """
    초성 쿼리가 텍스트의 초성 패턴에 포함되는지 확인합니다.

    예: match_chosung('ㅎㄱㄷ', '홍길동입니다') → True
        match_chosung('ㅎㄱ', '한강')         → True
    """
    if not query or not text:
        return False
    text_chosung = extract_chosung(text)
    return query in text_chosung


def chosung_similarity(query: str, text: str) -> float:
    """
    초성 쿼리와 텍스트의 초성 매칭 유사도를 0.0~1.0으로 반환합니다.
    완전 매칭이면 1.0, 부분 매칭이면 비율에 따라 0.0~1.0.
    """
    if not query or not text:
        return 0.0
    text_chosung = extract_chosung(text)
    if query == text_chosung:
        return 1.0
    if query in text_chosung:
        return 0.8 + (len(query) / len(text_chosung)) * 0.2
    return 0.0

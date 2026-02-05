import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name="DataScavenger", log_file="app.log", level=logging.INFO):
    """
    [KR] 애플리케이션 전역 로거를 설정합니다.
    콘솔 출력과 파일 저장을 동시에 수행합니다.

    Args:
        name (str): 로거 이름
        log_file (str): 로그 파일 경로
        level (int): 로깅 레벨 (기본: INFO)
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # 중복 핸들러 방지
    if logger.hasHandlers():
        return logger

    # 포맷 설정
    formatter = logging.Formatter(
        '[%(asctime)s] [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # 1. 콘솔 핸들러 (StreamHandler)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 2. 파일 핸들러 (RotatingFileHandler) - 5MB x 3개 유지
    try:
        file_handler = RotatingFileHandler(
            log_file, maxBytes=5*1024*1024, backupCount=3, encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to setup file logging: {e}")

    return logger

# [KR] 전역 로거 인스턴스 생성
logger = setup_logger()

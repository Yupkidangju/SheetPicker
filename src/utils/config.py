import json
import os
from pathlib import Path
import platformdirs

class ConfigManager:
    """
    [KR] 애플리케이션 설정을 관리하는 클래스.
    JSON 파일로 설정을 저장하고 로드합니다.
    설정 파일은 OS 표준 사용자 데이터 디렉토리에 저장됩니다.
    """
    APP_NAME = "Data Scavenger"
    APP_AUTHOR = "JulesCorp"

    # [KR] 사용자 데이터 디렉토리 경로 결정
    CONFIG_DIR = platformdirs.user_data_dir(APP_NAME, APP_AUTHOR)
    CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

    DEFAULT_CONFIG = {
        "theme": "light", # light or dark
        "favorites": [],
        "search_history": []
    }

    @staticmethod
    def load_config():
        """
        [KR] 설정을 로드합니다. 파일이 없으면 기본값을 반환합니다.
        """
        if not os.path.exists(ConfigManager.CONFIG_FILE):
            return ConfigManager.DEFAULT_CONFIG.copy()

        try:
            with open(ConfigManager.CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception:
            return ConfigManager.DEFAULT_CONFIG.copy()

    @staticmethod
    def save_config(config):
        """
        [KR] 설정을 저장합니다. 디렉토리가 없으면 생성합니다.
        """
        try:
            # [KR] 디렉토리 존재 확인 및 생성
            config_dir = os.path.dirname(ConfigManager.CONFIG_FILE)
            os.makedirs(config_dir, exist_ok=True)

            with open(ConfigManager.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Failed to save config: {e}")

    @staticmethod
    def get(key, default=None):
        config = ConfigManager.load_config()
        return config.get(key, default)

    @staticmethod
    def set(key, value):
        config = ConfigManager.load_config()
        config[key] = value
        ConfigManager.save_config(config)

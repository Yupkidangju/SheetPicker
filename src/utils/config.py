import json
import os
from pathlib import Path

class ConfigManager:
    """
    [KR] 애플리케이션 설정을 관리하는 클래스.
    JSON 파일로 설정을 저장하고 로드합니다.
    """
    CONFIG_FILE = "config.json"

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
        [KR] 설정을 저장합니다.
        """
        try:
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

    @staticmethod
    def save():
        """[v2.0.0] 현재 설정을 즉시 디스크에 저장합니다 (명시적 호출용)."""
        # 이미 set()에서 매번 저장하므로, 이 메서드는 명시적 flush 용도
        pass

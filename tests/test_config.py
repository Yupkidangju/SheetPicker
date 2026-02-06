import os
import shutil
import tempfile
import pytest
from src.utils.config import ConfigManager
import platformdirs

class TestConfigManager:
    def test_config_path_is_secure(self):
        """
        [KR] 설정 파일 경로가 CWD가 아닌 사용자 데이터 디렉토리인지 확인합니다.
        """
        # CWD에 있는 config.json이 아니어야 함
        assert ConfigManager.CONFIG_FILE != "config.json"
        assert os.path.isabs(ConfigManager.CONFIG_FILE)

        # 예상되는 경로 포함 여부 확인
        expected_part = "Data Scavenger"
        assert expected_part in ConfigManager.CONFIG_FILE

    def test_save_and_load_config(self):
        """
        [KR] 설정을 저장하고 로드하는 기능을 테스트합니다. (임시 디렉토리 사용)
        """
        # 임시 디렉토리 생성
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_config_file = os.path.join(temp_dir, "config.json")

            # 기존 값 백업
            original_config_file = ConfigManager.CONFIG_FILE

            try:
                # 테스트용 경로 설정
                ConfigManager.CONFIG_FILE = temp_config_file

                # 테스트 데이터
                test_key = "test_key"
                test_value = "test_value"

                # 설정 저장
                ConfigManager.set(test_key, test_value)

                # 파일 생성 확인
                assert os.path.exists(temp_config_file)

                # 설정 로드 확인
                loaded_value = ConfigManager.get(test_key)
                assert loaded_value == test_value

                # 기본값 확인
                assert ConfigManager.get("non_existent", "default") == "default"

            finally:
                # 복원
                ConfigManager.CONFIG_FILE = original_config_file

    def test_directory_creation(self):
        """
        [KR] 설정 저장 시 상위 디렉토리가 없으면 생성되는지 확인합니다.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            # 깊은 경로 설정
            deep_path = os.path.join(temp_dir, "subdir", "config.json")

            original_config_file = ConfigManager.CONFIG_FILE
            try:
                ConfigManager.CONFIG_FILE = deep_path

                ConfigManager.save_config({"test": "data"})

                assert os.path.exists(deep_path)
            finally:
                ConfigManager.CONFIG_FILE = original_config_file

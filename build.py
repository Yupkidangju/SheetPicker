import os
import sys
import subprocess
import argparse
from pathlib import Path

def run_build(dry_run=False):
    """
    [KR] Nuitka를 사용하여 프로젝트를 빌드합니다.
    """
    project_root = Path(__file__).parent.resolve()
    main_script = project_root / "src" / "main.py"

    if not main_script.exists():
        print(f"[Error] Main script not found at: {main_script}")
        sys.exit(1)

    # [KR] Nuitka 명령어 구성
    cmd = [
        sys.executable, "-m", "nuitka",
        "--standalone",
        "--onefile",
        "--enable-plugin=pyside6",
        "--include-package=pandas", # Pandas 명시적 포함
        "--include-package=openpyxl",
        "--windows-console-mode=disable", # GUI 앱이므로 콘솔 숨김

        # [KR] 메타데이터 및 회사 정보
        "--company-name=JulesCorp",
        "--product-name=Data Scavenger",
        "--file-version=1.0.0",
        "--product-version=1.0.0",
        "--file-description=High-performance Excel/CSV Search Tool",
        "--copyright=Copyright (c) 2024 JulesCorp",

        # [KR] 최적화 옵션 (LTO) - 빌드 시간 증가하므로 릴리즈 시 사용 권장
        # "--lto=yes",

        str(main_script)
    ]

    print(f"[Build] Executing command: {' '.join(cmd)}")

    if not dry_run:
        try:
            subprocess.run(cmd, check=True)
            print("[Build] Build completed successfully.")
        except subprocess.CalledProcessError as e:
            print(f"[Error] Build failed with code {e.returncode}")
            sys.exit(e.returncode)
    else:
        print("[Build] Dry run mode enabled. No changes made.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Build Data Scavenger using Nuitka")
    parser.add_argument("--dry-run", action="store_true", help="Print command without executing")
    args = parser.parse_args()

    run_build(dry_run=args.dry_run)

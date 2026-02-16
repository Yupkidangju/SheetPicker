"""
[v2.0.0] SQLite 기반 인덱스 캐시
파일 데이터를 SQLite에 캐싱하여 앱 재시작 시 Excel 파일을 다시 읽지 않고도
인덱스를 재구축할 수 있게 합니다. 파일 변경 시점(mtime)과 크기로 유효성을 판단합니다.
"""

import sqlite3
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from src.utils.logger import logger

# 캐시 DB 파일명
CACHE_DB_NAME = "data_scavenger_cache.db"


class IndexCache:
    """
    SQLite 기반 파일 데이터 캐시.
    인덱싱된 셀 데이터를 디스크에 보관하여 재시작 시 파일 재로드 없이 인덱스 복원이 가능합니다.
    """

    def __init__(self, db_path: Optional[str] = None):
        self.db_path = db_path or CACHE_DB_NAME
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        """DB 스키마를 초기화합니다."""
        try:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA synchronous=NORMAL")

            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS file_meta (
                    file_path TEXT PRIMARY KEY,
                    file_name TEXT NOT NULL,
                    file_mtime REAL NOT NULL,
                    file_size INTEGER NOT NULL,
                    indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS cell_data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    file_path TEXT NOT NULL,
                    sheet_name TEXT NOT NULL,
                    row_idx INTEGER NOT NULL,
                    col_idx INTEGER NOT NULL,
                    col_name TEXT NOT NULL,
                    cell_value TEXT NOT NULL,
                    FOREIGN KEY (file_path) REFERENCES file_meta(file_path)
                );

                CREATE INDEX IF NOT EXISTS idx_cell_file
                    ON cell_data(file_path);

                CREATE TABLE IF NOT EXISTS sheet_headers (
                    file_path TEXT NOT NULL,
                    sheet_name TEXT NOT NULL,
                    headers_json TEXT NOT NULL,
                    PRIMARY KEY (file_path, sheet_name)
                );
            """)
            self._conn.commit()
        except Exception as e:
            logger.error(f"캐시 DB 초기화 실패: {e}")
            self._conn = None

    def is_file_cached(self, file_path: str) -> bool:
        """파일이 캐시에 존재하고 변경되지 않았는지 확인합니다."""
        if not self._conn:
            return False

        try:
            path_obj = Path(file_path)
            if not path_obj.exists():
                return False

            current_mtime = path_obj.stat().st_mtime
            current_size = path_obj.stat().st_size

            row = self._conn.execute(
                "SELECT file_mtime, file_size FROM file_meta WHERE file_path = ?",
                (file_path,)
            ).fetchone()

            if row is None:
                return False

            # 수정 시간과 크기가 모두 일치하면 유효한 캐시
            return row[0] == current_mtime and row[1] == current_size
        except Exception:
            return False

    def save_file_data(self, file_path: str, file_name: str,
                       cells: List[Dict], headers: Dict[str, List[str]]):
        """파일의 셀 데이터를 캐시에 저장합니다."""
        if not self._conn:
            return

        try:
            path_obj = Path(file_path)
            mtime = path_obj.stat().st_mtime
            size = path_obj.stat().st_size

            # 기존 데이터 삭제 후 재삽입
            self._conn.execute(
                "DELETE FROM cell_data WHERE file_path = ?", (file_path,)
            )
            self._conn.execute(
                "DELETE FROM sheet_headers WHERE file_path = ?", (file_path,)
            )
            self._conn.execute(
                "DELETE FROM file_meta WHERE file_path = ?", (file_path,)
            )

            # 메타 정보 저장
            self._conn.execute(
                "INSERT INTO file_meta (file_path, file_name, file_mtime, file_size) VALUES (?, ?, ?, ?)",
                (file_path, file_name, mtime, size)
            )

            # 헤더 정보 저장
            for sheet_name, header_list in headers.items():
                self._conn.execute(
                    "INSERT INTO sheet_headers (file_path, sheet_name, headers_json) VALUES (?, ?, ?)",
                    (file_path, sheet_name, json.dumps(header_list, ensure_ascii=False))
                )

            # 셀 데이터 일괄 삽입
            self._conn.executemany(
                "INSERT INTO cell_data (file_path, sheet_name, row_idx, col_idx, col_name, cell_value) VALUES (?, ?, ?, ?, ?, ?)",
                [(c['file_path'], c['sheet_name'], c['row_idx'],
                  c['col_idx'], c['col_name'], c['value']) for c in cells]
            )

            self._conn.commit()
            logger.info(f"캐시 저장 완료: {file_name} ({len(cells)} 셀)")
        except Exception as e:
            logger.error(f"캐시 저장 실패: {file_path} — {e}")

    def load_file_data(self, file_path: str) -> Optional[Dict]:
        """캐시에서 파일 데이터를 로드합니다."""
        if not self._conn:
            return None

        try:
            # 메타 정보 조회
            meta = self._conn.execute(
                "SELECT file_name FROM file_meta WHERE file_path = ?",
                (file_path,)
            ).fetchone()
            if not meta:
                return None

            file_name = meta[0]

            # 헤더 정보 조회
            headers = {}
            for row in self._conn.execute(
                "SELECT sheet_name, headers_json FROM sheet_headers WHERE file_path = ?",
                (file_path,)
            ):
                headers[row[0]] = json.loads(row[1])

            # 셀 데이터 조회
            cells = []
            for row in self._conn.execute(
                "SELECT sheet_name, row_idx, col_idx, col_name, cell_value FROM cell_data WHERE file_path = ?",
                (file_path,)
            ):
                cells.append({
                    'file_path': file_path,
                    'file_name': file_name,
                    'sheet_name': row[0],
                    'row_idx': row[1],
                    'col_idx': row[2],
                    'col_name': row[3],
                    'value': row[4]
                })

            return {
                'file_path': file_path,
                'file_name': file_name,
                'headers': headers,
                'cells': cells
            }
        except Exception as e:
            logger.error(f"캐시 로드 실패: {file_path} — {e}")
            return None

    def remove_file(self, file_path: str):
        """캐시에서 파일 데이터를 제거합니다."""
        if not self._conn:
            return
        try:
            self._conn.execute("DELETE FROM cell_data WHERE file_path = ?", (file_path,))
            self._conn.execute("DELETE FROM sheet_headers WHERE file_path = ?", (file_path,))
            self._conn.execute("DELETE FROM file_meta WHERE file_path = ?", (file_path,))
            self._conn.commit()
        except Exception as e:
            logger.error(f"캐시 삭제 실패: {file_path} — {e}")

    def get_cached_files(self) -> List[str]:
        """캐시에 저장된 모든 파일 경로를 반환합니다."""
        if not self._conn:
            return []
        try:
            rows = self._conn.execute("SELECT file_path FROM file_meta").fetchall()
            return [r[0] for r in rows]
        except Exception:
            return []

    def clear_all(self):
        """전체 캐시를 초기화합니다."""
        if not self._conn:
            return
        try:
            self._conn.executescript("""
                DELETE FROM cell_data;
                DELETE FROM sheet_headers;
                DELETE FROM file_meta;
            """)
            self._conn.commit()
        except Exception as e:
            logger.error(f"캐시 전체 삭제 실패: {e}")

    def close(self):
        """DB 연결을 닫습니다."""
        if self._conn:
            self._conn.close()
            self._conn = None

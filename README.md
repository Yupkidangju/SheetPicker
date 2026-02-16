# Data Scavenger (v2.0.0)

## 🇰🇷 한국어 (Korean)
**Data Scavenger**는 윈도우 데스크톱 환경을 위한 고성능 엑셀/CSV 데이터 검색 도구입니다. 대용량 파일을 빠르게 인덱싱하고, 정확 매칭·유사 매칭·초성 검색을 조합하여 원하는 데이터를 즉시 찾아줍니다.

### 주요 기능
* **🔍 단일 검색창:** 구글처럼 검색어만 입력하면 끝. 정규식·수식·쿼리문 불필요.
* **⚡ 4단계 검색 엔진:** 정확 매칭 + 퍼지 매칭(오타 허용) + 초성 검색(ㅎㄱㄷ→홍길동) + BM25 관련도 랭킹
* **📊 인덱싱 기반:** 파일 추가 시 1회 인덱싱 → 이후 검색 <100ms
* **💾 SQLite 캐시:** 앱 재시작 시 파일 재로드 없이 즉시 검색
* **⭐ 파일 세트 즐겨찾기:** 자주 쓰는 파일 조합을 저장/복원
* **📤 결과 내보내기:** 검색 결과를 xlsx/csv로 저장 (출처 정보 포함)
* **🎨 다크/라이트 모드:** Windows 11 Fluent 스타일

### 🛠 사용 설명서
1. **파일 추가:** 좌측 패널에서 [+ 파일] 또는 [+ 폴더] 클릭. 또는 드래그 & 드롭.
2. **검색:** 상단 검색창에 키워드 입력. 자동으로 정확+유사+초성 검색 수행.
3. **AND 검색:** `홍길동 서울` → 두 키워드가 모두 포함된 행만 표시.
4. **제외 검색:** `홍길동 -퇴사` → "퇴사" 포함 행 제외.
5. **범위 검색:** `10000~50000` → 해당 숫자 범위의 셀 검색.
6. **초성 검색:** `ㅎㄱㄷ` → "홍길동" 자동 매칭.
7. **유사도 조절:** 우측 슬라이더로 퍼지 매칭 임계값 조절 (40%~100%).
8. **내보내기:** 체크박스로 원하는 결과 선택 → [📤 내보내기] 클릭.
9. **즐겨찾기:** 현재 파일 목록을 세트로 저장하여 나중에 한 번에 불러오기.

### 기술 스택 (2026-02 기준)
* Python 3.13+ / PySide6 6.10+ / Pandas 3.0+ / rapidfuzz / rank_bm25

---

## 🇺🇸 English
**Data Scavenger** is a high-performance Excel/CSV data search tool for Windows. It indexes large files and combines exact matching, fuzzy matching, Korean initial consonant (Chosung) search, and BM25 ranking to instantly find the data you need.

### Key Features
* **🔍 Single Search Bar:** Just type — no regex, formulas, or query languages needed.
* **⚡ 4-Layer Search Engine:** Exact + Fuzzy (typo-tolerant) + Chosung + BM25 relevance ranking.
* **📊 Index-Based:** One-time indexing → subsequent searches <100ms.
* **💾 SQLite Cache:** Instant search on app restart without reloading files.
* **⭐ File Set Favorites:** Save/restore frequently used file combinations.
* **📤 Export Results:** Save search results to xlsx/csv with source metadata.

---

## 🇯🇵 日本語 (Japanese)
**Data Scavenger**はWindows向けの高性能Excel/CSVデータ検索ツールです。大容量ファイルをインデックス化し、完全一致・あいまい検索・韓国語初声検索・BM25ランキングを組み合わせて即座にデータを見つけます。

### 主な機能
* **🔍 シングル検索バー:** キーワードを入力するだけ。正規表現・数式不要。
* **⚡ 4層検索エンジン:** 完全一致 + あいまい + 初声 + BM25関連度ランキング。
* **📊 インデックスベース:** 初回インデックス化 → 以降の検索は100ms未満。
* **📤 結果エクスポート:** 検索結果をxlsx/csvに保存。

---

## 🇹🇼 繁體中文 (Traditional Chinese)
**Data Scavenger** 是一款 Windows 高效能 Excel/CSV 資料搜尋工具。透過索引化大量檔案，結合精確比對、模糊比對、韓語初聲搜尋與 BM25 相關性排名，即時找到所需資料。

### 主要功能
* **🔍 單一搜尋列:** 只需輸入關鍵字，無需正規表示式或查詢語法。
* **⚡ 4層搜尋引擎:** 精確 + 模糊（容錯）+ 初聲 + BM25 相關性排名。
* **📤 匯出結果:** 搜尋結果儲存為 xlsx/csv，包含來源資訊。

---

## 🇨🇳 简体中文 (Simplified Chinese)
**Data Scavenger** 是一款 Windows 高性能 Excel/CSV 数据搜索工具。通过索引化大量文件，结合精确匹配、模糊匹配、韩语初声搜索与 BM25 相关性排名，即时找到所需数据。

### 主要功能
* **🔍 单一搜索栏:** 只需输入关键字，无需正则表达式或查询语法。
* **⚡ 4层搜索引擎:** 精确 + 模糊（容错）+ 初声 + BM25 相关性排名。
* **📤 导出结果:** 搜索结果保存为 xlsx/csv，包含来源信息。

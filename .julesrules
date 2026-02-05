.julesrules (D3D Protocol for GitHub)
1. Template & Project Metadata
Template Name: D3D Protocol

Template Version: 1.0

Project Info:

Name: ${PROJECT_NAME}

Version: ${CURRENT_VERSION}

Environment: ${ENV_TYPE}

2. Permissions
Filesystem Scope: project_root

Allow Read: ["all"]

Allow Write: ["all"]

Allow Execute: ["package_manager", "compiler", "test_runner"]

3. Initialization Protocol (Data Preservation)
Description: 프로젝트 시작, 스캐폴딩 및 환경 설정 시 데이터 보존 규칙

CRITICAL SAFETY RULE (NO_DESTRUCTIVE_INIT): 프로젝트 루트에 .md 파일(특히 spec.md, designs.md 등 DNA 파일)이 하나라도 존재할 경우, 기존 파일을 삭제하거나 덮어쓰는 모든 종류의 초기화 명령을 루트 경로에서 직접 실행하는 것을 절대 금지한다.

Forbidden Flags: --force, --overwrite, rm -rf 등 파괴적 옵션 사용 금지.

Safe Scaffolding Strategy (Merge Pattern):

Temp Init: 하위 임시 폴더(예: ./temp_init)에 프로젝트를 생성한다.

Selective Move: 소스 코드와 설정 파일(package.json, Cargo.toml 등)만 루트로 이동시킨다. (숨김 파일 포함)

Conflict Check: 이동 시 기존 DNA 문서(README, spec.md 등)를 절대 덮어쓰지 않는다.

Cleanup: 임시 폴더를 삭제한다.

4. Error Handling Rules
PROTOCOL: 오류 수정 요청 시, 즉시 코드를 수정하지 말고 먼저 해당 오류와 관련된 기술, 라이브러리, 의존성 정보를 '그라운딩(Web Search)'을 통해 최신 상태로 파악해야 한다.

MANDATORY GROUNDING: 학습된 데이터는 최신 기술과 차이가 있을 수 있으므로, 오류 해결 실패 시 즉시 그라운딩을 수행하여 최신 레퍼런스를 참조한다.

5. Documentation Rules (Core Logic)
CRITICAL: 모든 작업에서 문서 작성 및 갱신을 최우선 순위(Top Priority)로 두며, 개발 착수 전/후에 반드시 관련 문서를 먼저 점검한다.

VERIFICATION: 소스 코드와 문서 간의 정합성을 상시 검증하며, 불일치 발견 시 즉시 코드 수정을 중단하고 문서를 동기화한다.

README Language: README.md는 반드시 다국어로 작성하며, 언어 순서는 **[한 / 영 / 일 / 중(번체) / 중(간체)]**를 엄수할 것.

Standard Language: README.md를 제외한 모든 문서(CHANGELOG, designs.md 등)는 반드시 **'한국어'**로만 작성할 것.

Sync Policy: 코드 변경 시 연관된 모든 문서를 즉시 동기화한다. (API/아키텍처 변경 시 Spec 및 Design Decisions 최신화 필수)

DESIGNS_REFERENCE: 디자인이나 UI를 제작/수정할 때는 반드시 designs.md를 참조 및 최신화해야 한다.

DESIGNS_CONTENT_SPEC: designs.md에는 (1) ASCII 기반 프로젝트 디자인 구조도, (2) 각 부분별 기능 상세 설명, (3) 구현 시 주의사항이 포함되어야 한다.

6. Source Code Annotation Rules
i18n Implementation: 개발 시 모든 코드는 다국어(한/영/일/중)를 지원하도록 구현할 것.

CRITICAL COMMENT: 소스 코드 내의 모든 주석(Comment)은 반드시 **'한국어'**로만 작성할 것. (타 언어 혼용 금지)

Comment Quality: 코드의 의도와 맥락을 파악할 수 있도록 풍부하게 작성하며, 구현된 로직의 구체적인 동작 원리를 명시한다.

Versioning in Code: 코드 변경 시 [vX.X.X]와 같이 버전을 명시하고, 변경 내용을 한국어 주석으로 상세히 기술한다.

Feature Deletion: 기능 삭제 시 코드는 제거하되, 해당 위치에 삭제 사유와 버전을 한국어 주석으로 남겨 맥락을 보존한다.

7. Documentation Sync Checklist (Automated Trigger)
on_feature_add: ["Verify Code-Doc Consistency", "Update README Features (Multilingual)", "Add to CHANGELOG (Added - Korean)", "Update Docstrings (Korean)"]

on_bug_fix: ["Grounding Check", "Add to CHANGELOG (Fixed - Korean)", "Add Root Cause Comment (Korean)"]

on_architecture_change: ["Update DESIGN_DECISIONS.md (Why - Korean)", "Update IMPLEMENTATION_SUMMARY.md (Korean)", "Update designs.md (ASCII & Logic - Korean)"]

on_version_change: ["Update Version in Files", "Automated Audit Check of roadmap"]

8. Required Files
README.md, CHANGELOG.md, BUILD_GUIDE.md, IMPLEMENTATION_SUMMARY.md, LESSONS_LEARNED.md, DESIGN_DECISIONS.md, audit_roadmap.md, designs.md

9. Automation & AI Learning DNA
Agent Mode: Autonomous (사용자의 명시적 중단이 없는 한 자동 완수)

Recovery Logic: 소스 코드가 전실되어도 문서(Summary, Lessons Learned, designs.md 등)만으로 시스템 아키텍처를 95% 이상 복구할 수 있도록 상세히 기록한다.

Self Update: 버전 번호가 올라갈 때마다 audit_roadmap.md를 자동으로 분석 및 재작성하여 최신 감사 기준을 유지한다. 마일스톤 도달 시 LESSONS_LEARNED.md를 생성한다.

10. Version Control Standard
Format: MAJOR.MINOR.PATCH

Commit Message: Conventional Commits 준수. (GitHub Actions 연동 최적화)
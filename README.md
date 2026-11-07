# AI Agent Coding Field Guide

[English README](README.en.md) · [English site](https://eddy961206.github.io/ai-agent-coding-field-guide/en/)

X·Reddit·GitHub에서 AI를 활용한 개발 방법론을 조사하고, 날짜·원문·적용 조건을 함께 관리하는 한국어·영어 공개 자료집입니다.

- **읽기:** https://eddy961206.github.io/ai-agent-coding-field-guide/
- **로컬:** `index.html`을 브라우저로 열면 됩니다. 본문·스타일·상호작용이 포함된 단일 파일입니다.
- **AI에게 전달:** [인계용 Markdown](exports/agent-brief.md), [전체 연구 JSON](exports/research.json)
- **조사 기준일:** 2026-11-07 (Asia/Seoul)

첫 판은 X 40개 게시물과 GitHub·Reddit·웹 자료를 포함한 78개 출처, 16개 실전 방법, 8개 요청문을 연결합니다. 원문 정보, 작성자의 주장, 편집자의 적용 제안을 구분합니다. 전체 웹의 전수조사나 도구 성능 비교는 아닙니다.

## 구조

```text
data/
  site.json       조사 기준일과 문서 정보
  sources.json    고정 ID, 원문, 날짜, 날짜 기준, 확인일, 한계
  methods.json    편집 제안과 근거 출처 ID
  recipes.json    작업별 적용 도우미
  prompts.json    직접 작성한 요청문
src/
  sections/      장별 편집 원고
  intro.html     문서 머리말
  outro.html     문서 꼬리말
  styles.css     화면과 인쇄 스타일
  app.js         필터·탐색·복사
scripts/build.py 단일 HTML과 에이전트용 출력 생성·검사
scripts/validate_batch.py 다른 에이전트의 조사 결과 형식 검사
scripts/research_delta.py 원문 식별자 기반 중복 후보 확인
data/en/        영어 데이터 번역. 출처 메타데이터는 공유
src/en/         영어 장별 원고
research/        조사 기록, 인계 형식, 업데이트 기준
exports/         자동 생성되는 Markdown·JSON
index.html       자동 생성되는 독립 HTML
```

Python 3.10 이상과 표준 라이브러리만 사용합니다. Node 패키지 설치, 외부 CDN, 런타임 API 키, 추적 스크립트가 필요하지 않습니다. 원문 링크를 열 때는 네트워크와 해당 서비스 접근 권한이 필요합니다.

## 수정과 빌드

1. 출처를 `data/sources.json`에 추가합니다. 원문 전문이나 자격 증명은 저장하지 않습니다.
2. 방법 카드의 `sources` 또는 본문의 `[[source-id|표시 이름]]`으로 연결합니다.
3. 원고와 데이터, 조사 기록, `CHANGELOG.md`를 함께 갱신합니다.
4. 실행합니다.

```shell
python scripts/build.py
python scripts/build.py --check
```

첫 명령은 `index.html`, `exports/research.json`, `exports/agent-brief.md`를 생성합니다. 두 번째는 데이터 형식, 중복 출처, 날짜, 출처 참조와 생성 결과의 최신 상태를 검사합니다. 원문의 현재 접속 가능성이나 주장 진실성을 네트워크로 자동 검증하지는 않습니다.

GitHub Actions는 같은 검사를 수행합니다. GitHub Pages는 `main`의 루트에서 한국어판, `/en/`에서 영어판을 게시합니다. 매일 09:00 Asia/Seoul 조사·갱신은 Codex 데스크톱의 이 채팅 자동화로 관리합니다. 이 로컬 실행에는 노트북과 앱이 켜져 있어야 합니다. 절차와 권한은 [DAILY_UPDATE.md](research/DAILY_UPDATE.md)에 있습니다.

## 다음 AI 에이전트에 넘기기

`AGENTS.md` → 최신 `research/runs/` 기록 → `exports/agent-brief.md` 순서로 읽도록 요청할 수 있습니다. 전체 구조화된 자료는 `exports/research.json`에 있습니다. 조사 결과를 받는 형식은 [research/templates/research-batch.json](research/templates/research-batch.json), 검토·통합 절차는 [CONTRIBUTING.md](CONTRIBUTING.md)에 있습니다.

`research.json`에는 출처와 방법뿐 아니라 본문의 비교 분석(`narrative_sections`)과 검토된 조사 묶음(`reviewed_batches`)도 들어 있습니다. 이 파일만 읽는 다음 에이전트도 원문 정보와 종합 판단을 구분할 수 있습니다. 조사 묶음은 별도 검토 없이 자동 게시하지 않습니다.

영어 인계 파일은 `exports/agent-brief.en.md`와 `exports/research.en.json`입니다. 보관한 원본 batch는 원래 언어를 유지하며, 현재 해석과 방법·요청문·본문은 각 언어로 내보냅니다.

HTML과 export 파일을 직접 수정하지 말고 원본 데이터·장별 원고를 수정한 뒤 다시 빌드합니다. 고정 ID를 유지하면 여러 에이전트가 같은 출처를 다뤄도 추적할 수 있습니다.

## 출처와 권리

원문 링크와 짧은 편집 요약을 제공합니다. 원문·영상·이미지·타인의 코드 전문을 복제하지 않습니다. 연결된 콘텐츠의 권리는 원저작자에게 있으며, 공개 링크나 저장소라는 사실이 재배포 허락을 뜻하지 않습니다. 이 저장소의 자체 코드·원고에 대한 별도 라이선스는 아직 지정하지 않았습니다.

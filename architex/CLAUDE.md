# 프로젝트: architex — 기후변화·재난 데이터 저널리즘

## 개요
UN에서 기후변화·재난 데이터를 수집·검증하는 사무관이 **저널리스트 역할**로 운영하는 1인 데이터 저널리즘 프로젝트.
언론사 이름: **architex**. 매일 한국시간(KST) 오후 9시, 웹 검색을 기반으로 기후변화·재난 관련 신규 논문/뉴스/데이터 업데이트를 수집해 `data/items.json`에 누적하고, 대시보드를 재생성한다.
**원본은 GitHub 저장소 `https://github.com/moduhouse/lh-workshop`** (공개, `lh-workshop` 모노레포의 `architex/` 서브폴더). 매일 수집 결과(`architex/data/items.json`)가 이 저장소 `master`에 커밋되면 GitHub Actions(`.github/workflows/architex-deploy.yml`)가 검증·빌드해 `architex/architex_dashboard.html`을 자동 재생성·커밋하고, GitHub Pages(레거시 브랜치 배포, `master`/`/` 기준 — `https://moduhouse.github.io/lh-workshop/architex/`)가 그 파일을 그대로 서빙한다.
PC의 OneDrive 폴더(`lh-workshop/architex`)는 작업 사본일 뿐이며 자동 갱신되지 않는다 — 최신본은 저장소/Pages가 기준. 빌드 파이프라인 없이 정적 HTML 파일 하나로 동작(생성은 Python 스크립트가 보조).
다른 두 프로젝트(개별공시지가, EDAT)와 Pages를 공유하는 모노레포이므로, Pages 배포 방식(레거시 브랜치)은 레포 전체 공통 설정이며 architex만 바꿀 수 없다 — `architex_dashboard.html`은 (다른 두 프로젝트의 산출물처럼) git에 커밋되어야 Pages에 반영된다.

## 수집 범위 (3개 주제, 고정)
- `adaptation` 기후변화 적응·회복력 (적응역량, 도시 회복력, NDC 등)
- `disaster` 자연재해·재난위험 (홍수, 폭염, 가뭄, 태풍 등 재해 데이터/뉴스)
- `climate_general` 기후변화 전반 (완화·정책·과학, IPCC/COP 등 국제협상)

## 논문 수집 방식 — 주의
Google Scholar는 자동화된 크롤링을 CAPTCHA/서비스약관으로 차단하므로 **직접 스크래핑하지 않는다**.
대신 `WebSearch` 도구로 주제별 쿼리를 검색해 논문·보고서·뉴스 링크를 수집하는 **웹 검색 기반 방식**을 사용한다.
- Google Scholar의 특정 결과를 긁어오는 것이 아니라 일반 웹 검색 결과를 표본적으로 수집하는 것이므로, 전수조사가 아님을 항상 인지할 것.
- 출처(저널/매체)나 날짜가 불확실한 항목은 꾸며내지 말고 `confidence_note` 필드에 한계를 명시한 뒤 수록한다.
- 오래된 배경자료(해당 연도 발표가 아닌 것)는 `title_ko`에 `[배경자료]` 접두어를 붙이고 `confidence_note`에 발표 시점을 밝혀 "오늘의 신규 소식"과 구분한다.

## 데이터 파일
`./data/items.json`
```json
{
  "last_updated": "ISO8601 타임스탬프 (KST)",
  "items": [
    {
      "id": "고유 ID (예: 2026-11-01-슬러그)",
      "collected_at": "YYYY-MM-DD (수집한 날짜)",
      "published_date": "YYYY-MM-DD 또는 null (불명확하면 null)",
      "type": "news | paper | data_update",
      "topics": ["adaptation" | "disaster" | "climate_general", ...],
      "title_ko": "한국어 제목 (언론사 톤)",
      "title_original": "원문 제목",
      "source": "매체/기관명",
      "url": "원문 링크",
      "region": "지역명 (한국어)",
      "source_countries": ["자료를 낸 매체·기관·학술지 소재국 ISO 3166-1 alpha-2", ...],
      "related_countries": ["기사 내용(사건·지역)이 다루는 나라 alpha-2", ...],
      "lat": 숫자 또는 null,
      "lon": 숫자 또는 null,
      "summary_ko": "2~3문장 한국어 요약",
      "confidence_note": "출처 한계·검증 필요 사항 (없으면 생략 가능)"
    }
  ]
}
```
- `id`는 중복 수집 방지를 위한 키 — 매일 수집 시 기존 `items`의 `url` 또는 `id`와 대조해 중복이면 건너뛴다.
- `source_countries` / `related_countries`는 **ISO 3166-1 alpha-2 대문자**(예: `US`, `KR`, `ET`) 배열. 모르면 추측하지 말고 `[]`로 두고 `confidence_note`에 적는다. 글로벌 주제면 `related_countries`는 `[]`. 국제기구는 본부 소재국(UNFCCC→`DE`, WMO→`CH`, UNDRR→`CH`, IPCC→`CH`, World Bank→`US`)을 출처국으로 쓴다. 허용 코드 목록은 `scripts/iso_countries.json`.
- 지도: `related_countries`는 회색 채움, `source_countries`는 흰 점선 테두리로 표시(world-atlas 110m 경계 — 소국은 경계가 없어 범례 목록에만 나옴).
- `lat`/`lon`은 사건/기관이 위치한 **지역의 근사 좌표**(국가 또는 주요 도시 중심)이며 정밀 좌표가 아니다. `region`이 "글로벌"이면 좌표 없이(`null`) 지도에는 표시하지 않고 목록에만 노출한다.

## 대시보드 파일
`./architex_dashboard.html` — git에 올리지 않는 로컬 미리보기 산출물. **직접 수정하지 말 것** (`scripts/build_dashboard.py`가 `template.html` + `data/items.json`으로 매번 재생성하는 산출물).
`./template.html` — 실제 수정 대상. 단일 HTML, 외부 빌드 도구 없음.
- 기술스택: 순수 HTML/CSS/JS + Leaflet.js(지도) + Chart.js(차트) + topojson-client·world-atlas(나라 경계), CDN(unpkg/jsdelivr) 로드
- `template.html`의 `ISO_A2_NUM` 압축 문자열은 `scripts/iso_countries.json`과 같은 표(alpha-2→numeric) — 둘을 함께 고칠 것
- 데이터는 `template.html` 내부 `/*__DATA__*/ ... /*__DATA_END__*/` 자리에 `build_dashboard.py`가 JSON을 그대로 삽입
- 구조: 헤더(로고+갱신시각+다크모드 토글) → KPI 통계 6종 → 이슈 지도(Leaflet, 지역별 원형 마커, 색상=대표 주제) → 주제별 분포 도넛 + 일별 수집건수 추이 라인(Chart.js) → 주제/유형 필터 칩 → 기사 카드 목록(배지+요약+confidence_note) → 푸터(데이터 한계 고지)
- 카테고리 색상(2026-11 디자인 개편): 라이트 `#1a87d7`(adaptation) / `#e23248`(disaster) / `#008c69`(climate_general), 다크 `#3a9ae6` / `#f0566b` / `#009e77` — `dataviz` 검증기 통과(다크는 CVD 경고 구간이라 범례·라벨 병기 필수). 지도는 항상 어두운 CARTO 바탕이므로 다크 단계(`--map-*`)를 쓴다. 새 주제 추가·색 변경 시 반드시 `dataviz` 스킬로 재검증할 것.
- 디자인 톤: Lato(+Noto Sans KR) 가는 제목, Georgia(+Noto Serif KR) 보조문, 차콜 `#343a40` 브레드크럼·푸터, 민트 `#00cc99` 알약 버튼, 레드 카테고리 링크, 지도 왼쪽 아이콘 레일+범례 패널(주제별 레이어 토글).
- 라이트/다크 모드: `prefers-color-scheme` + `[data-theme]` 이중 대응, 사용자의 수동 토글 선택은 `localStorage`(`architex-theme`)에 저장.

## 저장소 구성·배포
- `scripts/validate_items.py` — 스키마 검증(필수 필드, id/url 중복, 날짜 형식, 나라 코드, 좌표). 실패 시 종료 코드 1
- `scripts/build_dashboard.py` — `template.html` + `data/items.json` → `architex_dashboard.html`
- `.github/workflows/architex-deploy.yml`(레포 루트) — `master`에 `architex/data/`·`architex/template.html`·`architex/scripts/` 변경이 푸시되면 검증 → 빌드 → 변경 시 `architex_dashboard.html`을 봇 커밋으로 자동 반영(`[skip ci]`로 재트리거 방지). 검증 실패 시 워크플로가 실패하고 커밋하지 않으므로 사이트는 직전 정상본을 유지. `workflow_dispatch`로 수동 실행도 가능
- Pages는 레포 전체가 레거시 브랜치 배포(`master`/`/`)를 공유 — 별도 `_site/` 아티팩트 배포 아님
- 로컬 미리보기: `python scripts/validate_items.py && python scripts/build_dashboard.py` 후 `architex_dashboard.html`을 브라우저로 연다

## 일일 자동 수집 루틴 (매일 21:00 KST)
Claude 예약 작업(클라우드)으로 매일 21:00 KST에 실행된다. 클라우드에서 돌기 때문에 PC 파일이 아니라 **GitHub 저장소를 클론해 작업하고 푸시**한다:
1. `https://github.com/moduhouse/lh-workshop` 저장소를 클론(이미 있으면 `git pull`), `architex/` 폴더에서 작업
2. `adaptation` / `disaster` / `climate_general` 3개 주제로 `WebSearch` 수행 (최근 1~2일 내 소식 우선)
3. 기존 `data/items.json`의 `url`·`id`와 대조해 신규 항목만 추출, 스키마에 맞춰 정리(한국어 제목/요약, 출처국·관련국, `confidence_note` 포함). 주제당 0~3건, 확인되지 않은 사실은 꾸며내지 않는다
4. `data/items.json`에 추가하고 `last_updated`를 실행 시각(KST, ISO8601)으로 갱신 — 신규 항목이 0건이어도 갱신해 "수집은 돌았음"을 남긴다
5. `python scripts/validate_items.py` 통과 확인(실패 시 고치고 재실행), `python scripts/build_dashboard.py`로 빌드 오류 없는지 확인
6. `data/items.json`만 커밋(`collect: YYYY-MM-DD 신규 N건`)하고 `main`에 푸시 → Actions가 Pages 배포
7. 결과(신규 건수, 주요 헤드라인, Pages 주소)를 보고
- 데이터 커밋·푸시는 루틴이 자동으로 한다(2026-11-06 사용자 요청으로 변경). 템플릿·스크립트 변경은 루틴이 하지 않는다

## 코딩 컨벤션
- 단일 HTML 파일 구조 유지 (JS/CSS 파일 분리나 빌드 파이프라인 도입 금지) — 단, `template.html` → `architex_dashboard.html` 생성용 Python 스크립트는 예외
- UI 텍스트는 한국어 사용
- 새 기능 추가 시에도 CDN 기반 라이브러리만 사용 (npm/번들러 도입 금지)
- 차트/색상 작업 시 반드시 `dataviz` 스킬을 먼저 로드하고 팔레트 규칙을 따를 것

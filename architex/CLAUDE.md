# 프로젝트: architex — 기후변화·재난 데이터 저널리즘

## 개요
UN에서 기후변화·재난 데이터를 수집·검증하는 사무관이 **저널리스트 역할**로 운영하는 1인 데이터 저널리즘 프로젝트.
언론사 이름: **architex**. 매일 한국시간(KST) 오후 9시, 웹 검색을 기반으로 기후변화·재난 관련 신규 논문/뉴스/데이터 업데이트를 수집해 `data/items.json`에 누적하고, 대시보드를 재생성한다.
Git 저장소 아님(lh-workshop 저장소 하위 폴더). 빌드 파이프라인 없이 정적 HTML 파일 하나로 동작(생성은 Python 스크립트가 보조).

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
      "lat": 숫자 또는 null,
      "lon": 숫자 또는 null,
      "summary_ko": "2~3문장 한국어 요약",
      "confidence_note": "출처 한계·검증 필요 사항 (없으면 생략 가능)"
    }
  ]
}
```
- `id`는 중복 수집 방지를 위한 키 — 매일 수집 시 기존 `items`의 `url` 또는 `id`와 대조해 중복이면 건너뛴다.
- `lat`/`lon`은 사건/기관이 위치한 **지역의 근사 좌표**(국가 또는 주요 도시 중심)이며 정밀 좌표가 아니다. `region`이 "글로벌"이면 좌표 없이(`null`) 지도에는 표시하지 않고 목록에만 노출한다.

## 대시보드 파일
`./architex_dashboard.html` — **직접 수정하지 말 것** (`scripts/build_dashboard.py`가 `template.html` + `data/items.json`으로 매번 재생성하는 산출물).
`./template.html` — 실제 수정 대상. 단일 HTML, 외부 빌드 도구 없음.
- 기술스택: 순수 HTML/CSS/JS + Leaflet.js(지도) + Chart.js(차트), CDN(unpkg/jsdelivr) 로드
- 데이터는 `template.html` 내부 `/*__DATA__*/ ... /*__DATA_END__*/` 자리에 `build_dashboard.py`가 JSON을 그대로 삽입
- 구조: 헤더(로고+갱신시각+다크모드 토글) → KPI 통계 6종 → 이슈 지도(Leaflet, 지역별 원형 마커, 색상=대표 주제) → 주제별 분포 도넛 + 일별 수집건수 추이 라인(Chart.js) → 주제/유형 필터 칩 → 기사 카드 목록(배지+요약+confidence_note) → 푸터(데이터 한계 고지)
- 카테고리 색상은 `dataviz` 스킬의 검증된 팔레트 slot 1~3(blue/orange/aqua)을 주제(adaptation/disaster/climate_general)에 고정 배정 — 새 주제 추가 시 slot 4(yellow) 이후를 쓰지 말고 반드시 `dataviz` 스킬로 재검증할 것.
- 라이트/다크 모드: `prefers-color-scheme` + `[data-theme]` 이중 대응, 사용자의 수동 토글 선택은 `localStorage`(`architex-theme`)에 저장.

## 재현/갱신 방법
1. `data/items.json`에 당일 수집 항목을 (중복 제거 후) 추가하고 `last_updated`를 갱신
2. `python scripts/build_dashboard.py` 실행 → `architex_dashboard.html` 재생성
3. 브라우저로 열어 KPI 수치·지도 마커·기사 카드가 정상 반영됐는지 확인

## 일일 자동 수집 루틴 (매일 21:00 KST)
Claude Code 세션은 스스로 깨어나지 않으므로, **스케줄 기능(cloud routine)**으로 매일 21:00 KST에 아래 작업을 수행하도록 등록되어 있다(설정 방법은 `schedule` 스킬 참고):
1. `adaptation` / `disaster` / `climate_general` 3개 주제로 `WebSearch` 수행 (최근 1~2일 내 소식 우선)
2. 기존 `data/items.json`의 `url`과 대조해 신규 항목만 추출, 스키마에 맞춰 정리(한국어 제목/요약, `confidence_note` 포함)
3. `data/items.json`에 추가하고 `last_updated` 갱신
4. `python scripts/build_dashboard.py` 실행
5. 결과(신규 항목 수, 주요 헤드라인)를 사용자에게 보고. **git commit은 자동으로 하지 않음** — 필요 시 사용자가 직접 커밋.

## 코딩 컨벤션
- 단일 HTML 파일 구조 유지 (JS/CSS 파일 분리나 빌드 파이프라인 도입 금지) — 단, `template.html` → `architex_dashboard.html` 생성용 Python 스크립트는 예외
- UI 텍스트는 한국어 사용
- 새 기능 추가 시에도 CDN 기반 라이브러리만 사용 (npm/번들러 도입 금지)
- 차트/색상 작업 시 반드시 `dataviz` 스킬을 먼저 로드하고 팔레트 규칙을 따를 것

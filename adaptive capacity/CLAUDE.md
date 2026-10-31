# 프로젝트: EDAT 기후변화 적응역량 대시보드

## 개요
기후변화가 삶에 미치는 영향을 보는 **EDAT 데이터 관리자 본인**이 직접 분석에 쓰는 대시보드 프로젝트.
Git 저장소 아님. 빌드 파이프라인 없이 정적 HTML 파일 하나로 동작.

## 데이터 파일
`./regression base v9.xlsx` (Sheet1, 9,840행 x 45열)
- 51개국 x 984개 지역(주/도) x 2014–2023(10개년) 패널 데이터
- 식별 컬럼: `OBJECTID,ID,continent,code(ISO3),GID_0,country,GID_1,province,NAME_1,ENGTYPE_1,year`
- 지표 컬럼(약 29개, 기후·사회경제·거버넌스):
  ```
  water, elec, life_both, life_female, life_male, health_exp, gini, unemploy,
  wealth_inequal10, welath_inequal50, political, HDI, Corruption_CPI, migration,
  storm, flood100yr, temp, preci, urban, urban_pop, pop_den, gdppc, income50,
  HappinessScore, forest, Green, UHI, pm2_5, slums_pop_country
  ```
- `slums_pop_Province_*` 계열 4개 컬럼(엑셀 12~15열)은 헤더 한글 인코딩이 깨져 있어 **사용하지 않음**
- 대륙은 Africa / Europe / Oceania / Asia 4종만 존재 (아메리카 대륙 데이터 없음)
- **지역(주/도) 단위 경계(GeoJSON)가 없음** → 지도 시각화는 국가 단위 choropleth만 가능. 지역별 지표는 국가 내 단순평균으로 집계(인구가중치 미적용)

## 참고자료
`./참고자료/UN_Habitat_NDC3_2026_Korean.pdf` — NDC 3.0 도시 기후대응 현황 섹션의 근거 보고서 (61MB). 상세 내용은 아래 "NDC 3.0 도시 기후대응 현황 연동" 참고.

## 중간 데이터
`./edat_data.json` — 엑셀에서 추출한 중간 산출물 (git 추적 대상 아님, 매번 재생성 가능)
- `scripts/extract_data.py` 실행으로 생성: 국가-연도 집계(`cy_cols`/`cy_rows`, 510행) + 지역 상세(`p_cols`/`p_rows`, 9,840행, 축소 지표셋)
- 지역 상세는 파일 용량 때문에 17개 핵심 지표로만 제한됨(전체 29개 아님)

## 대시보드 파일
`./EDAT_기후적응역량_대시보드.html` — 단일 HTML 파일, 외부 빌드 도구 없음
- 기술스택: 순수 HTML/CSS/JS + Plotly.js(CDN, jsdelivr), 데이터는 `edat_data.json` 내용을 HTML 내부 `const EDAT_DATA = /*__DATA__*/;` 자리에 인라인 삽입(파일 분리 없음)
- 구조(위→아래 순서):
  1. 지표/연도 컨트롤 (+ 적응역량 종합점수 선택 시 4영역 가중치 슬라이더)
  2. KPI 4종 (선택 연도 평균/전년대비/최고/최저 국가)
  3. 세계지도(choropleth) + 이상치 자동 표시 배지(전체 연도 기준 |z|≥2)
  4. 연도별 추이(대륙별+전체 평균) / 상위·하위 10개국 바 차트
  5. 기후–사회경제 관계 분석 (산점도+OLS 회귀선, r/R², 연도별/전체기간 토글)
  6. 지표간 상관관계 히트맵 (피어슨, ~30개 지표, 영역별 필터 탭)
  7. 국가 간 직접 비교 (2~5개국, 핵심 지표 z-score 그룹 바 차트)
  8. **NDC 3.0 도시 기후대응 현황** (UN-Habitat 2026 보고서 연동 — 아래 별도 섹션 참고)
  9. 데이터 조회 테이블 (국가별 집계 / 지역별 상세, 필터+정렬, NDC 3.0 상태 필터 포함)

### 적응역량 종합점수 (ADAPT_SCORE) 방법론
4개 영역의 하위 지표를 **전체 패널(2014–2023, 510개 국가-연도) 기준 z-score**로 표준화 후 영역 내 평균, 대시보드의 슬라이더로 영역별 가중치를 조절해 가중합한다.
| 영역 | 하위 지표 |
|---|---|
| 경제력 | gdppc, income50, health_exp |
| 기본인프라 | water, elec, urban |
| 거버넌스 | political, Corruption_CPI, HDI |
| 환경자원 | forest, Green, pop_den |

`pop_den`(인구밀도)은 낮을수록 유리하게 **역방향** 처리(1인당 자원 압박이 적다고 가정). 이 가정을 바꾸고 싶으면 `INVERTED_INDICATORS` 집합만 수정하면 된다.

### NDC 3.0 도시 기후대응 현황 연동
출처: `./참고자료/UN_Habitat_NDC3_2026_Korean.pdf` (UN-Habitat 「NDC 3.0의 도시 관련 내용」, 2026년 4월 중순까지 UNFCCC 제출 기준).
- 국가별 "도시 관련 내용" 등급표(142개국, A+/A/B+/B/C+/C 또는 미제출 No)에서 본 데이터셋 51개국과 일치하는 항목만 추출해 `NDC3_DATA`(HTML `<script>` 내 상수)에 ISO3 코드 기준으로 하드코딩되어 있다. PDF는 텍스트 레이어의 한글 폰트가 깨져 있어 `PyMuPDF`의 블록 좌표(x,y) 기반으로 표를 재구성해 추출했다(시각 스크린샷 대조로 교차검증 완료).
- 51개국 중 34개국은 등급 보유(제출 완료), 1개국(스위스)은 보고서상 "No"(NDC 3.0 미제출), 나머지 16개국(알바니아, 베냉, 보스니아, 카메룬, 가나, 인도, 라오스, 리비아, 북마케도니아, 말리, 나미비아, 파푸아뉴기니, 수단, 세네갈, 차드, 우간다)은 이 보고서의 분석 대상에 아예 포함되지 않아 **"보고서 데이터 없음"**으로 표기(= NDC3.0 미제출이라는 뜻이 아니라, 단지 이 특정 분석 범위 밖이라는 뜻).
- 등급은 기후 지표와 무관한 **정성 평가**(국가 기후계획에 도시 내용이 얼마나 반영됐는지)이며, `+` 접미사는 "구현수단(재무·역량·거버넌스) 포함"을 의미. 보고서 갱신 시 `NDC3_DATA` 객체만 다시 채우면 됨.

### 재현 방법 (데이터 갱신 시)
1. `regression base v9.xlsx`를 교체/수정
2. `python scripts/extract_data.py` 실행 → `edat_data.json` 재생성
3. `edat_data.json` 내용을 HTML의 `/*__DATA__*/` 자리에 붙여넣어 대시보드 파일을 다시 생성

## 코딩 컨벤션
- 단일 HTML 파일 구조 유지 (JS/CSS 파일 분리나 빌드 파이프라인 도입 금지)
- UI 텍스트는 한국어 사용
- 차트 작업 시 `dataviz` 스킬의 팔레트 사용: CSS 변수 `--series-1~4`(카테고리 색), `--seq-100~700`(블루 계열 시퀀셜), `--text-primary/secondary/muted`, `--grid`, `--border` 등을 `:root`에서 재정의해 재사용. 라이트/다크 모드는 `prefers-color-scheme` + `[data-theme]` 이중 대응
- 새 기능 추가 시에도 CDN 기반 라이브러리만 사용 (npm/번들러 도입 금지), 현재는 Plotly.js(jsdelivr)만 사용 중

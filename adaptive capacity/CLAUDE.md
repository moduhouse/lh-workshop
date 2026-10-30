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

## 중간 데이터
`./edat_data.json` — 엑셀에서 추출한 중간 산출물 (git 추적 대상 아님, 매번 재생성 가능)
- `scripts/extract_data.py` 실행으로 생성: 국가-연도 집계(`cy_cols`/`cy_rows`, 510행) + 지역 상세(`p_cols`/`p_rows`, 9,840행, 축소 지표셋)
- 지역 상세는 파일 용량 때문에 17개 핵심 지표로만 제한됨(전체 29개 아님)

## 대시보드 파일
`./EDAT_기후적응역량_대시보드.html` — 단일 HTML 파일, 외부 빌드 도구 없음
- 기술스택: 순수 HTML/CSS/JS + Plotly.js(CDN, jsdelivr), 데이터는 `edat_data.json` 내용을 HTML 내부 `const EDAT_DATA = /*__DATA__*/;` 자리에 인라인 삽입(파일 분리 없음)
- 구조: 지표/연도 컨트롤(+적응역량 종합점수 선택 시 가중치 슬라이더) → KPI → 세계지도(choropleth) → 연도별 추이 + 상위/하위 10개국 → 기후–사회경제 관계 분석(산점도+OLS 회귀선, r/R² 표시) → 적응역량 종합점수 → 데이터 조회 테이블(국가별 집계 / 지역별 상세, 필터+정렬)

### 적응역량 종합점수 (ADAPT_SCORE) 방법론
4개 영역의 하위 지표를 **전체 패널(2014–2023, 510개 국가-연도) 기준 z-score**로 표준화 후 영역 내 평균, 대시보드의 슬라이더로 영역별 가중치를 조절해 가중합한다.
| 영역 | 하위 지표 |
|---|---|
| 경제력 | gdppc, income50, health_exp |
| 기본인프라 | water, elec, urban |
| 거버넌스 | political, Corruption_CPI, HDI |
| 환경자원 | forest, Green, pop_den |

`pop_den`(인구밀도)은 낮을수록 유리하게 **역방향** 처리(1인당 자원 압박이 적다고 가정). 이 가정을 바꾸고 싶으면 `INVERTED_INDICATORS` 집합만 수정하면 된다.

### 재현 방법 (데이터 갱신 시)
1. `regression base v9.xlsx`를 교체/수정
2. `python scripts/extract_data.py` 실행 → `edat_data.json` 재생성
3. `edat_data.json` 내용을 HTML의 `/*__DATA__*/` 자리에 붙여넣어 대시보드 파일을 다시 생성

## 코딩 컨벤션
- 단일 HTML 파일 구조 유지 (JS/CSS 파일 분리나 빌드 파이프라인 도입 금지)
- UI 텍스트는 한국어 사용
- 차트 작업 시 `dataviz` 스킬의 팔레트 사용: CSS 변수 `--series-1~4`(카테고리 색), `--seq-100~700`(블루 계열 시퀀셜), `--text-primary/secondary/muted`, `--grid`, `--border` 등을 `:root`에서 재정의해 재사용. 라이트/다크 모드는 `prefers-color-scheme` + `[data-theme]` 이중 대응
- 새 기능 추가 시에도 CDN 기반 라이브러리만 사용 (npm/번들러 도입 금지), 현재는 Plotly.js(jsdelivr)만 사용 중

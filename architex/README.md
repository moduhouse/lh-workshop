# architex — 기후변화·재난 데이터 저널리즘

매일 21:00(KST) 기후변화 적응·재해위험·국제 기후협상 관련 신규 논문·뉴스·데이터 갱신 소식을 웹 검색으로 모아 지도와 목록으로 보여 주는 정적 대시보드입니다.

- 대시보드: GitHub Pages (저장소 Settings → Pages에서 주소 확인)
- 데이터: [`data/items.json`](data/items.json)
- 수집·스키마·운영 규칙: [`CLAUDE.md`](CLAUDE.md)

## 구조

```
data/items.json            누적 수집 데이터 (매일 예약 작업이 커밋)
template.html              대시보드 원본 (디자인·기능 수정은 여기서)
scripts/validate_items.py  데이터 검증
scripts/build_dashboard.py template + data → architex_dashboard.html
.github/workflows/deploy.yml  푸시 시 검증 → 빌드 → Pages 배포
```

## 로컬에서 보기

```bash
python scripts/validate_items.py
python scripts/build_dashboard.py
# architex_dashboard.html 을 브라우저로 열기
```

수집은 웹 검색 기반 표본 수집이며 전수조사가 아닙니다. 출처나 날짜가 불확실한 항목은 `confidence_note`에 한계를 적어 둡니다.

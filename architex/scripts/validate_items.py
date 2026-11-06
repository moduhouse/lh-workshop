"""data/items.json 스키마 검증.

사용법: python scripts/validate_items.py
- 매일 수집 루틴이 커밋하기 전에, 그리고 GitHub Actions가 배포하기 전에 실행한다.
- 오류가 하나라도 있으면 종료 코드 1로 끝나 배포가 멈춘다(잘못된 데이터가 사이트에 올라가지 않도록).
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "items.json"
ISO_PATH = Path(__file__).resolve().parent / "iso_countries.json"

TYPES = {"news", "paper", "data_update"}
TOPICS = {"adaptation", "disaster", "climate_general"}
REQUIRED = ["id", "collected_at", "type", "topics", "title_ko", "source", "url",
            "region", "source_countries", "related_countries", "summary_ko"]
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def main():
    iso = set(json.loads(ISO_PATH.read_text(encoding="utf-8")))
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    errors = []

    if "last_updated" not in data or "items" not in data:
        errors.append("최상위에 last_updated, items가 있어야 합니다.")
        items = []
    else:
        items = data["items"]

    seen_ids, seen_urls = set(), set()
    for n, it in enumerate(items):
        tag = f"[{n}] {it.get('id', '?')}"
        for key in REQUIRED:
            if key not in it:
                errors.append(f"{tag}: '{key}' 필드 없음")
        if it.get("id") in seen_ids:
            errors.append(f"{tag}: id 중복")
        if it.get("url") in seen_urls:
            errors.append(f"{tag}: url 중복")
        seen_ids.add(it.get("id"))
        seen_urls.add(it.get("url"))
        if it.get("type") not in TYPES:
            errors.append(f"{tag}: type '{it.get('type')}'은 {sorted(TYPES)} 중 하나여야 함")
        topics = it.get("topics") or []
        if not topics or any(t not in TOPICS for t in topics):
            errors.append(f"{tag}: topics {topics}는 {sorted(TOPICS)}에서 1개 이상")
        if not DATE_RE.match(str(it.get("collected_at", ""))):
            errors.append(f"{tag}: collected_at은 YYYY-MM-DD")
        pd = it.get("published_date")
        if pd is not None and not DATE_RE.match(str(pd)):
            errors.append(f"{tag}: published_date는 YYYY-MM-DD 또는 null")
        for key in ("source_countries", "related_countries"):
            codes = it.get(key)
            if not isinstance(codes, list):
                errors.append(f"{tag}: {key}는 배열이어야 함 (없으면 [])")
                continue
            bad = [c for c in codes if c not in iso]
            if bad:
                errors.append(f"{tag}: {key}에 ISO 3166-1 alpha-2가 아닌 값 {bad}")
        lat, lon = it.get("lat"), it.get("lon")
        if (lat is None) != (lon is None):
            errors.append(f"{tag}: lat/lon은 둘 다 숫자이거나 둘 다 null")
        elif lat is not None and not (-90 <= lat <= 90 and -180 <= lon <= 180):
            errors.append(f"{tag}: 좌표 범위 오류 ({lat}, {lon})")
        if not str(it.get("url", "")).startswith(("http://", "https://")):
            errors.append(f"{tag}: url은 http(s)로 시작")

    if errors:
        print(f"검증 실패: {len(errors)}건")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print(f"검증 통과: {len(items)}개 항목")


if __name__ == "__main__":
    main()

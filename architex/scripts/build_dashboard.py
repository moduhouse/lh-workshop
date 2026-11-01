"""architex/data/items.json 의 내용을 template.html에 삽입해 architex_dashboard.html을 생성한다.

사용법: python build_dashboard.py
매일 21:00 KST 자동 수집 루틴이 items.json을 갱신한 뒤 이 스크립트를 실행해 대시보드를 재생성한다.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_PATH = ROOT / "data" / "items.json"
TEMPLATE_PATH = ROOT / "template.html"
OUTPUT_PATH = ROOT / "architex_dashboard.html"

PLACEHOLDER_RE = re.compile(r"/\*__DATA__\*/.*?/\*__DATA_END__\*/", re.DOTALL)


def main():
    data = json.loads(DATA_PATH.read_text(encoding="utf-8"))
    template = TEMPLATE_PATH.read_text(encoding="utf-8")

    payload = json.dumps(data, ensure_ascii=False)
    replacement = f"/*__DATA__*/{payload}/*__DATA_END__*/"

    if not PLACEHOLDER_RE.search(template):
        raise RuntimeError("template.html에서 데이터 플레이스홀더를 찾지 못했습니다.")

    output = PLACEHOLDER_RE.sub(lambda m: replacement, template, count=1)
    OUTPUT_PATH.write_text(output, encoding="utf-8")
    print(f"생성 완료: {OUTPUT_PATH} ({len(data['items'])}개 항목)")


if __name__ == "__main__":
    main()

"""주 1회 새 회차를 받아 draws.json 에 덧붙인다. 앱은 이 파일만 읽고 동행복권을 부르지 않는다.
보통 요청은 1건이다. 자료가 이상하면 파일을 건드리지 않고 실패로 끝난다.
"""
import json
import os
import pathlib
import sys
import urllib.request

OUT = pathlib.Path(os.environ.get("DRAWS_FILE", pathlib.Path(__file__).resolve().parent.parent / "draws.json"))
URL = "https://www.dhlottery.co.kr/lt645/selectPstLt645InfoNew.do?srchDir=latest&srchCursorLtEpsd={}"
PAGE = 10  # 응답 한 번의 최대 회차 수


def slim(x):
    return {"r": x["ltEpsd"], "d": x["ltRflYmd"],
            "n": [x[f"tm{i}WnNo"] for i in range(1, 7)], "b": x["bnsWnNo"],
            "w": x["rnk1WnNope"], "a": x["rnk1WnAmt"]}


def valid(d):
    nums = d["n"] + [d["b"]]
    return len(set(nums)) == 7 and all(1 <= n <= 45 for n in nums) and len(d["d"]) == 8


def merge(draws, rows):
    """연속된 다음 회차만 덧붙인다. 하나라도 이상하면 ValueError."""
    out = list(draws)
    for d in sorted(map(slim, rows), key=lambda d: d["r"]):
        if d["r"] != out[-1]["r"] + 1 or not valid(d):
            raise ValueError(f"bad round {d['r']} after {out[-1]['r']}")
        out.append(d)
    return out


def main():
    draws = json.loads(OUT.read_text())
    before = len(draws)
    while True:
        with urllib.request.urlopen(URL.format(draws[-1]["r"]), timeout=20) as r:
            rows = json.load(r)["data"]["list"]
        draws = merge(draws, rows)
        if len(rows) < PAGE:
            break
    if len(draws) > before:
        OUT.write_text(json.dumps(draws, ensure_ascii=False, separators=(",", ":")))
    print(f"{before} -> {len(draws)}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:  # 실패를 작업 실패로 드러낸다.
        sys.exit(f"failed: {e}")

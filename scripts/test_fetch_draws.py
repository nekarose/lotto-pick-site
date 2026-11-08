import fetch_draws as f


def row(r, a=1):
    return {"ltEpsd": r, "ltRflYmd": "20260101", **{f"tm{i}WnNo": i + a - 1 for i in range(1, 7)},
            "bnsWnNo": 40, "rnk1WnNope": 1, "rnk1WnAmt": 9}


base = [f.slim(row(1))]
assert [d["r"] for d in f.merge(base, [row(3), row(2)])] == [1, 2, 3]  # 내림차순 응답
assert f.merge(base, []) == base
for bad in ([row(3)], [row(2, a=45)]):  # 회차 건너뜀, 범위 밖 번호
    try:
        f.merge(base, bad)
    except ValueError:
        continue
    raise AssertionError(bad)
print("ok")

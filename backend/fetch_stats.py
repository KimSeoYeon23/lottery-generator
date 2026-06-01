"""동행복권 API로 역대 통계 수집 후 ~/.lottery/stats.json 저장

API: https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do?srchLtEpsd={회차}
"""

import json
import os
import time
from collections import Counter

import requests

# Docker: /app/stats.json (./backend:/app 볼륨 마운트)
# GitHub Actions: backend/stats.json (커밋 후 자동 반영)
STATS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.json")
API_URL = "https://www.dhlottery.co.kr/lt645/selectPstLt645Info.do?srchLtEpsd={}"


def _get(session, round_no):
    """회차 데이터 조회. 없으면 None 반환."""
    try:
        data = session.get(API_URL.format(round_no), timeout=10).json()
        items = data.get("data", {}).get("list", [])
        if not items:
            return None
        item = items[0]
        return {
            "nums": [item[f"tm{i}WnNo"] for i in range(1, 7)],
            "bonus": item["bnsWnNo"],
        }
    except Exception:
        return None


def fetch_latest_round(session):
    lo, hi = 1, 2000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if _get(session, mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


def fetch_all_results(session, latest_round):
    freq = Counter()
    recent_50 = Counter()
    sums = []

    for rnd in range(1, latest_round + 1):
        result = _get(session, rnd)
        if not result:
            time.sleep(0.1)
            continue
        for n in result["nums"]:
            freq[n] += 1
        if rnd > latest_round - 50:
            for n in result["nums"]:
                recent_50[n] += 1
        sums.append(sum(result["nums"]))

        if rnd % 100 == 0:
            print(f"  {rnd}/{latest_round}회 수집 완료...")
        time.sleep(0.05)

    return freq, recent_50, sums


def calc_sum_range(sums, pct=0.80):
    sums_sorted = sorted(sums)
    cut = int(len(sums_sorted) * (1 - pct) / 2)
    if not sums_sorted or cut >= len(sums_sorted):
        return 0, 0
    return sums_sorted[cut], sums_sorted[-cut - 1]


def run():
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})

    print("최신 회차 탐색 중...")
    latest = fetch_latest_round(session)
    print(f"최신 회차: {latest}회")

    if latest <= 1:
        raise RuntimeError("최신 회차 탐색 실패")

    print("전체 데이터 수집 중...")
    freq, recent_50, sums = fetch_all_results(session, latest)

    if not sums:
        raise RuntimeError("수집된 데이터가 없습니다.")

    sum_lo, sum_hi = calc_sum_range(sums)
    stats = {
        "latest_round": latest,
        "lotto_freq": dict(freq),
        "lotto_recent_50": dict(recent_50),
        "lotto_sum_range": [sum_lo, sum_hi],
    }

    with open(STATS_PATH, "w") as f:
        json.dump(stats, f)

    print(f"저장 완료: {STATS_PATH} (최신 {latest}회)")
    return stats


def load():
    if os.path.exists(STATS_PATH):
        with open(STATS_PATH) as f:
            return json.load(f)
    return None


if __name__ == "__main__":
    run()

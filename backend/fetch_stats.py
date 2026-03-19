"""동행복권 공개 API로 역대 통계 수집 후 ~/.lottery/stats.json 저장"""

import json
import os
import time
from collections import Counter

import requests

STATS_PATH = os.path.expanduser("~/.lottery/stats.json")
API_URL = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}"


def fetch_latest_round():
    resp = requests.get(API_URL.format(1), timeout=10)
    # 최신 회차는 1회차부터 순차 탐색 대신 큰 숫자로 이진탐색
    lo, hi = 1, 2000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        try:
            data = requests.get(API_URL.format(mid), timeout=10).json()
            if data.get("returnValue") == "success":
                lo = mid
            else:
                hi = mid - 1
        except Exception:
            hi = mid - 1
    return lo


def fetch_all_results(latest_round):
    freq = Counter()
    recent_50 = Counter()
    sums = []

    for rnd in range(1, latest_round + 1):
        try:
            data = requests.get(API_URL.format(rnd), timeout=10).json()
        except Exception:
            continue

        if data.get("returnValue") != "success":
            continue

        nums = [data[f"drwtNo{i}"] for i in range(1, 7)]
        bonus = data.get("bnusNo")

        for n in nums:
            freq[n] += 1

        if rnd > latest_round - 50:
            for n in nums:
                recent_50[n] += 1

        sums.append(sum(nums))

        if rnd % 100 == 0:
            print(f"  {rnd}/{latest_round}회 수집 완료...")
        time.sleep(0.05)  # 서버 부하 방지

    return freq, recent_50, sums


def calc_sum_range(sums, pct=0.80):
    sums_sorted = sorted(sums)
    cut = int(len(sums_sorted) * (1 - pct) / 2)
    return sums_sorted[cut], sums_sorted[-cut - 1]


def run():
    print("최신 회차 탐색 중...")
    latest = fetch_latest_round()
    print(f"최신 회차: {latest}회")

    print("전체 데이터 수집 중...")
    freq, recent_50, sums = fetch_all_results(latest)

    sum_lo, sum_hi = calc_sum_range(sums)

    stats = {
        "latest_round": latest,
        "lotto_freq": dict(freq),
        "lotto_recent_50": dict(recent_50),
        "lotto_sum_range": [sum_lo, sum_hi],
    }

    os.makedirs(os.path.dirname(STATS_PATH), exist_ok=True)
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

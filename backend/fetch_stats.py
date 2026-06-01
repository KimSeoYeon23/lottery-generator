"""동행복권 공개 API로 역대 통계 수집 후 stats.json 저장

참고: 동행복권은 자동화 요청을 서버 레벨에서 차단합니다.
      이 스크립트는 차단이 풀린 네트워크 환경에서만 동작합니다.
"""

import json
import os
import time
from collections import Counter

import requests

# 스크립트와 같은 디렉토리에 저장 (Docker: /app/stats.json)
STATS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.json")
API_URL = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo={}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json, text/javascript, */*; q=0.01",
    "X-Requested-With": "XMLHttpRequest",
    "Referer": "https://www.dhlottery.co.kr/",
}


def _session():
    s = requests.Session()
    s.headers.update(HEADERS)
    s.get("https://www.dhlottery.co.kr/", timeout=10)
    return s


def fetch_latest_round(session):
    lo, hi = 1, 2000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        try:
            data = session.get(API_URL.format(mid), timeout=10).json()
            if data.get("returnValue") == "success":
                lo = mid
            else:
                hi = mid - 1
        except Exception:
            hi = mid - 1
    return lo


def fetch_all_results(session, latest_round):
    freq = Counter()
    recent_50 = Counter()
    sums = []

    for rnd in range(1, latest_round + 1):
        try:
            data = session.get(API_URL.format(rnd), timeout=10).json()
        except Exception:
            continue
        if data.get("returnValue") != "success":
            continue
        nums = [data[f"drwtNo{i}"] for i in range(1, 7)]
        for n in nums:
            freq[n] += 1
        if rnd > latest_round - 50:
            for n in nums:
                recent_50[n] += 1
        sums.append(sum(nums))
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
    print("세션 초기화 중...")
    session = _session()

    print("최신 회차 탐색 중...")
    latest = fetch_latest_round(session)
    print(f"최신 회차: {latest}회")

    if latest <= 1:
        raise RuntimeError("API 접근 차단됨 — 다른 네트워크에서 시도해주세요.")

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

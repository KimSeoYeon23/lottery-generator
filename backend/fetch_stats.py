"""동행복권 공개 API로 역대 통계 수집 후 stats.json 저장

GitHub Actions에서 Playwright(Chromium)로 실행 → 봇 차단 우회
매주 토요일 21:30 KST 자동 실행 후 stats.json 커밋
"""

import json
import os
from collections import Counter

# 스크립트와 같은 디렉토리에 저장 (Docker: /app/stats.json, GH Actions: backend/stats.json)
STATS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "stats.json")
API_BASE = "https://www.dhlottery.co.kr/common.do?method=getLottoNumber&drwNo="
BATCH = 50


def _open_page():
    from playwright.sync_api import sync_playwright

    pw = sync_playwright().start()
    browser = pw.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent=(
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        extra_http_headers={"Accept-Language": "ko-KR,ko;q=0.9"},
        viewport={"width": 1280, "height": 800},
    )
    page = context.new_page()

    # 메인 페이지 방문으로 세션 수립
    page.goto("https://www.dhlottery.co.kr/", wait_until="load", timeout=30000)

    # "비정상적인 방법으로 접속" 팝업 처리
    try:
        page.get_by_role("button", name="확인").click(timeout=3000)
    except Exception:
        pass

    return pw, browser, page


def fetch_latest_round(page):
    lo, hi = 1, 2000
    while lo < hi:
        mid = (lo + hi + 1) // 2
        try:
            data = page.evaluate(
                f"() => fetch('{API_BASE}{mid}').then(r => r.json()).catch(() => null)"
            )
            if data and data.get("returnValue") == "success":
                lo = mid
            else:
                hi = mid - 1
        except Exception:
            hi = mid - 1
    return lo


def fetch_all_results(page, latest_round):
    freq = Counter()
    recent_50 = Counter()
    sums = []

    for start in range(1, latest_round + 1, BATCH):
        end = min(start + BATCH, latest_round + 1)
        rounds = list(range(start, end))

        results = page.evaluate(
            f"""
            async () => {{
                const rounds = {rounds};
                return await Promise.all(rounds.map(n =>
                    fetch('{API_BASE}' + n)
                        .then(r => r.json())
                        .catch(() => null)
                ));
            }}
            """
        )

        for data in results or []:
            if not data or data.get("returnValue") != "success":
                continue
            nums = [data[f"drwtNo{i}"] for i in range(1, 7)]
            rnd = data.get("drwNo", 0)
            for n in nums:
                freq[n] += 1
            if rnd > latest_round - 50:
                for n in nums:
                    recent_50[n] += 1
            sums.append(sum(nums))

        print(f"  {min(end - 1, latest_round)}/{latest_round}회 수집 완료...")

    return freq, recent_50, sums


def calc_sum_range(sums, pct=0.80):
    sums_sorted = sorted(sums)
    cut = int(len(sums_sorted) * (1 - pct) / 2)
    if not sums_sorted or cut >= len(sums_sorted):
        return 0, 0
    return sums_sorted[cut], sums_sorted[-cut - 1]


def run():
    print("브라우저 시작 중...")
    pw, browser, page = _open_page()

    try:
        print("최신 회차 탐색 중...")
        latest = fetch_latest_round(page)
        print(f"최신 회차: {latest}회")

        if latest <= 1:
            raise RuntimeError("최신 회차 탐색 실패 — API 접근이 차단되었을 수 있습니다.")

        print("전체 데이터 수집 중...")
        freq, recent_50, sums = fetch_all_results(page, latest)
    finally:
        browser.close()
        pw.stop()

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

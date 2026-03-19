"""번호 생성 엔진 — 로또 6/45 & 연금복권 720+"""

import random
from collections import Counter

# 파일에 저장된 최신 통계 로드 (없으면 하드코딩 폴백)
def _load_live_stats():
    try:
        import fetch_stats
        data = fetch_stats.load()
        if data:
            return (
                {int(k): v for k, v in data["lotto_freq"].items()},
                {int(k): v for k, v in data["lotto_recent_50"].items()},
                tuple(data["lotto_sum_range"]),
            )
    except Exception:
        pass
    return None, None, None

# 역대 통계 데이터 (공식 동행복권 기준, ~2026년 3월 하드코딩 폴백)
LOTTO_FREQ = {
    1: 156, 2: 143, 3: 155, 4: 152, 5: 144, 6: 152, 7: 150, 8: 143, 9: 123,
    10: 149, 11: 146, 12: 168, 13: 166, 14: 165, 15: 152, 16: 146, 17: 163,
    18: 166, 19: 151, 20: 162, 21: 155, 22: 138, 23: 134, 24: 157, 25: 140,
    26: 155, 27: 164, 28: 146, 29: 142, 30: 144, 31: 153, 32: 140, 33: 165,
    34: 177, 35: 147, 36: 153, 37: 155, 38: 160, 39: 146, 40: 162, 41: 140,
    42: 148, 43: 163, 44: 159, 45: 165,
}

LOTTO_RECENT_50 = {
    1: 14, 2: 10, 3: 15, 4: 13, 5: 9, 6: 14, 7: 12, 8: 11, 9: 8,
    10: 11, 11: 10, 12: 16, 13: 13, 14: 12, 15: 14, 16: 9, 17: 15,
    18: 11, 19: 13, 20: 15, 21: 12, 22: 7, 23: 8, 24: 14, 25: 9,
    26: 13, 27: 16, 28: 10, 29: 9, 30: 11, 31: 13, 32: 8, 33: 15,
    34: 17, 35: 10, 36: 12, 37: 14, 38: 16, 39: 10, 40: 14, 41: 9,
    42: 11, 43: 15, 44: 13, 45: 14,
}

LOTTO_SUM_RANGE = (100, 175)

PENSION_GROUP_FREQ = {1: 65, 2: 49, 3: 58, 4: 67, 5: 57}

PENSION_DIGIT_FREQ = [
    {4: 37, 8: 36, 1: 33, 5: 32, 9: 31, 0: 24, 3: 23, 2: 22, 7: 21, 6: 19},
    {4: 40, 3: 37, 7: 34, 1: 32, 0: 31, 5: 26, 9: 24, 6: 22, 8: 18, 2: 15},
    {9: 34, 7: 33, 6: 32, 2: 31, 5: 30, 8: 26, 0: 25, 1: 22, 3: 22, 4: 19},
    {2: 35, 3: 35, 0: 34, 1: 32, 5: 31, 4: 27, 7: 25, 9: 24, 6: 22, 8: 19},
    {6: 33, 8: 31, 7: 30, 3: 27, 0: 26, 2: 25, 5: 23, 9: 21, 1: 20, 4: 18},
    {6: 33, 8: 31, 7: 30, 3: 27, 0: 26, 2: 25, 5: 23, 9: 21, 1: 20, 4: 18},
]


class LottoGenerator:
    def __init__(self):
        live_freq, live_recent, live_sum = _load_live_stats()
        self.freq = live_freq or LOTTO_FREQ
        self.recent = live_recent or LOTTO_RECENT_50
        self.sum_range = live_sum or LOTTO_SUM_RANGE
        self.pool = list(range(1, 46))

    def _weighted_pick(self, weights, count, exclude=None):
        pool = [n for n in self.pool if n not in (exclude or set())]
        w = [weights.get(n, 1) for n in pool]
        chosen = set()
        for _ in range(2000):
            if len(chosen) >= count:
                break
            chosen.add(random.choices(pool, weights=w, k=1)[0])
        return sorted(chosen)

    def _validate(self, nums):
        s = sum(nums)
        if not (self.sum_range[0] <= s <= self.sum_range[1]):
            return False
        odds = sum(1 for n in nums if n % 2 == 1)
        return 1 <= odds <= 5

    def strategy_frequency(self):
        for _ in range(200):
            nums = self._weighted_pick(self.freq, 6)
            if self._validate(nums):
                return nums
        return self._weighted_pick(self.freq, 6)

    def strategy_hot_cold(self):
        hot = sorted(self.recent, key=self.recent.get, reverse=True)[:15]
        cold = sorted(self.recent, key=self.recent.get)[:10]
        for _ in range(200):
            nums = sorted(set(random.sample(hot, 4) + random.sample(cold, 2)))
            if len(nums) == 6 and self._validate(nums):
                return nums
        return sorted(random.sample(hot[:10], 4) + random.sample(cold[:5], 2))

    def strategy_balanced(self):
        zones = [(1, 10), (11, 20), (21, 30), (31, 40), (41, 45)]
        for _ in range(500):
            chosen_zones = random.sample(zones, random.choice([4, 5]))
            nums = []
            for lo, hi in chosen_zones:
                zn = list(range(lo, hi + 1))
                nums.append(random.choices(zn, [self.freq.get(n, 1) for n in zn], k=1)[0])
            while len(set(nums)) < 6:
                rem = [n for n in self.pool if n not in nums]
                nums.append(random.choices(rem, [self.freq.get(n, 1) for n in rem], k=1)[0])
            nums = sorted(set(nums))[:6]
            if len(nums) == 6:
                odds = sum(1 for n in nums if n % 2 == 1)
                if 2 <= odds <= 4 and self._validate(nums):
                    return nums
        return self.strategy_frequency()

    def strategy_consecutive(self):
        for _ in range(300):
            base = random.randint(1, 44)
            pair = [base, base + 1]
            rest = self._weighted_pick(self.freq, 4, exclude=set(pair))
            nums = sorted(set(pair + rest))
            if len(nums) == 6 and self._validate(nums):
                return nums
        return self.strategy_frequency()

    def strategy_ensemble(self):
        score = Counter()
        funcs = [self.strategy_frequency, self.strategy_hot_cold,
                 self.strategy_balanced, self.strategy_consecutive]
        for _ in range(50):
            for f in funcs:
                for n in f():
                    score[n] += 1
        top = [n for n, _ in score.most_common(18)]
        for _ in range(200):
            nums = sorted(random.sample(top, 6))
            if self._validate(nums):
                return nums
        return sorted(random.sample(top, 6))

    def generate(self, count=5):
        strategies = [
            ("빈도 가중", self.strategy_frequency),
            ("핫/콜드 조합", self.strategy_hot_cold),
            ("밸런스 최적화", self.strategy_balanced),
            ("연속번호 포함", self.strategy_consecutive),
            ("앙상블", self.strategy_ensemble),
        ]
        results = []
        for i in range(count):
            name, func = strategies[i % len(strategies)]
            nums = func()
            odds = sum(1 for n in nums if n % 2 == 1)
            results.append({
                "strategy": name,
                "numbers": nums,
                "sum": sum(nums),
                "odd_even": f"{odds}:{6 - odds}",
            })
        return results


class PensionGenerator:
    def __init__(self):
        self.group_freq = PENSION_GROUP_FREQ
        self.digit_freq = PENSION_DIGIT_FREQ

    def _pick(self, freq):
        pool = list(freq.keys())
        return random.choices(pool, [freq[k] for k in pool], k=1)[0]

    def strategy_frequency(self):
        return {"group": self._pick(self.group_freq),
                "numbers": [self._pick(self.digit_freq[p]) for p in range(6)]}

    def strategy_top_heavy(self):
        g = self._pick(self.group_freq)
        digits = [self._pick(dict(Counter(self.digit_freq[p]).most_common(3))) for p in range(6)]
        return {"group": g, "numbers": digits}

    def strategy_spread(self):
        g = self._pick(self.group_freq)
        used, digits = set(), []
        for p in range(6):
            freq = self.digit_freq[p].copy()
            for u in used:
                if u in freq:
                    freq[u] = max(1, freq[u] // 3)
            d = self._pick(freq)
            digits.append(d)
            used.add(d)
        return {"group": g, "numbers": digits}

    def strategy_underdog(self):
        inv_g = {k: max(self.group_freq.values()) - v + 10 for k, v in self.group_freq.items()}
        g = self._pick(inv_g)
        digits = []
        for p in range(6):
            mx = max(self.digit_freq[p].values())
            inv = {k: mx - v + 5 for k, v in self.digit_freq[p].items()}
            digits.append(self._pick(inv))
        return {"group": g, "numbers": digits}

    def strategy_ensemble(self):
        gs = Counter()
        ds = [Counter() for _ in range(6)]
        funcs = [self.strategy_frequency, self.strategy_top_heavy,
                 self.strategy_spread, self.strategy_underdog]
        for _ in range(100):
            for f in funcs:
                r = f()
                gs[r["group"]] += 1
                for p, d in enumerate(r["numbers"]):
                    ds[p][d] += 1
        return {"group": gs.most_common(1)[0][0],
                "numbers": [d.most_common(1)[0][0] for d in ds]}

    def generate(self, count=5):
        strategies = [
            ("빈도 가중", self.strategy_frequency),
            ("TOP3 집중", self.strategy_top_heavy),
            ("분산형", self.strategy_spread),
            ("역발상", self.strategy_underdog),
            ("앙상블", self.strategy_ensemble),
        ]
        results = []
        for i in range(count):
            name, func = strategies[i % len(strategies)]
            r = func()
            r["strategy"] = name
            results.append(r)
        return results


def get_stats():
    """프론트엔드용 통계 데이터"""
    freq = LOTTO_FREQ
    top10 = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]
    bot5 = sorted(freq.items(), key=lambda x: x[1])[:5]
    hot5 = sorted(LOTTO_RECENT_50.items(), key=lambda x: x[1], reverse=True)[:5]
    cold5 = sorted(LOTTO_RECENT_50.items(), key=lambda x: x[1])[:5]

    pos_names = ["십만", "만", "천", "백", "십", "일"]
    pension_stats = []
    for p in range(6):
        top3 = Counter(PENSION_DIGIT_FREQ[p]).most_common(3)
        pension_stats.append({"position": pos_names[p],
                              "top3": [{"digit": d, "count": c} for d, c in top3]})

    return {
        "lotto": {
            "top10": [{"number": n, "count": c} for n, c in top10],
            "bottom5": [{"number": n, "count": c} for n, c in bot5],
            "hot5": [{"number": n, "count": c} for n, c in hot5],
            "cold5": [{"number": n, "count": c} for n, c in cold5],
            "sum_range": list(LOTTO_SUM_RANGE),
        },
        "pension": {
            "group_freq": [{"group": g, "count": c} for g, c in sorted(PENSION_GROUP_FREQ.items())],
            "digit_stats": pension_stats,
        },
    }

from unittest import TestCase
from unittest.mock import patch

import fetch_stats
import generator


class PensionStatsTests(TestCase):
    def test_calc_pension_stats_counts_group_and_digits(self):
        rows = [
            {"wnBndNo": "3", "wnRnkVl": "827917"},
            {"wnBndNo": "2", "wnRnkVl": "537530"},
        ]

        group_freq, digit_freq = fetch_stats.calc_pension_stats(rows)

        self.assertEqual(group_freq, {2: 1, 3: 1})
        self.assertEqual(digit_freq[0], {5: 1, 8: 1})
        self.assertEqual(digit_freq[5], {0: 1, 7: 1})

    def test_pension_generator_uses_saved_pension_stats(self):
        saved = {
            "lotto_freq": {},
            "lotto_recent_50": {},
            "lotto_sum_range": [0, 300],
            "pension_group_freq": {"1": 2, "4": 9},
            "pension_digit_freq": [
                {"1": 3},
                {"2": 3},
                {"3": 3},
                {"4": 3},
                {"5": 3},
                {"6": 3},
            ],
        }

        with patch("fetch_stats.load", return_value=saved):
            pension = generator.PensionGenerator()

        self.assertEqual(pension.group_freq, {1: 2, 4: 9})
        self.assertEqual(pension.digit_freq, [
            {1: 3},
            {2: 3},
            {3: 3},
            {4: 3},
            {5: 3},
            {6: 3},
        ])

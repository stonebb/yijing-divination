#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for DivinationEngine"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yijing import DivinationEngine


class TestDivinationEngine(unittest.TestCase):

    def setUp(self):
        self.engine = DivinationEngine(seed=42)

    def test_toss_coins_returns_six_lines(self):
        lines = self.engine.toss_coins()
        self.assertEqual(len(lines), 6)

    def test_toss_coins_line_structure(self):
        lines = self.engine.toss_coins()
        for i, line in enumerate(lines):
            self.assertEqual(line["position"], i + 1)
            self.assertIn(line["value"], (0, 1))
            self.assertIsInstance(line["changing"], bool)
            self.assertIn(line["label"], ("老阴", "少阳", "少阴", "老阳"))
            self.assertEqual(sum(line["coins"]), line["coin_sum"])

    def test_toss_coins_seed_reproducibility(self):
        e1 = DivinationEngine(seed=99)
        b1 = DivinationEngine.get_hexagram_binary(e1.toss_coins())

        e2 = DivinationEngine(seed=99)
        b2 = DivinationEngine.get_hexagram_binary(e2.toss_coins())

        self.assertEqual(b1, b2)

    def test_digital_method_returns_six_lines(self):
        lines = self.engine.digital_method()
        self.assertEqual(len(lines), 6)

    def test_digital_method_changing_lines(self):
        for _ in range(20):
            lines = self.engine.digital_method(changing_lines=2)
            changing = sum(1 for l in lines if l["changing"])
            self.assertEqual(changing, 2)

    def test_digital_method_random_changing_lines(self):
        for _ in range(20):
            engine = DivinationEngine()
            lines = engine.digital_method()
            changing = sum(1 for l in lines if l["changing"])
            self.assertGreaterEqual(changing, 1)
            self.assertLessEqual(changing, 3)

    def test_time_method_returns_six_lines(self):
        lines = self.engine.time_method()
        self.assertEqual(len(lines), 6)

    def test_time_method_has_exactly_one_changing_line(self):
        for _ in range(20):
            engine = DivinationEngine()
            lines = engine.time_method()
            changing = sum(1 for l in lines if l["changing"])
            self.assertEqual(changing, 1,
                             "time_method should have exactly 1 changing line")

    def test_time_method_includes_time_params(self):
        lines = self.engine.time_method(timestamp=1747000000.0)
        self.assertEqual(lines[0]["time_params"]["year"], 2025)
        self.assertEqual(lines[0]["time_params"]["month"], 5)

    def test_get_hexagram_binary(self):
        lines = [
            {"position": 1, "value": 1},  # bottom
            {"position": 2, "value": 1},
            {"position": 3, "value": 1},
            {"position": 4, "value": 0},
            {"position": 5, "value": 0},
            {"position": 6, "value": 0},  # top
        ]
        binary = DivinationEngine.get_hexagram_binary(lines)
        self.assertEqual(binary, "111000")

    def test_get_changing_binary(self):
        lines = [
            {"position": 1, "value": 1, "changing": False},
            {"position": 2, "value": 1, "changing": True},   # flips to 0
            {"position": 3, "value": 1, "changing": False},
            {"position": 4, "value": 0, "changing": True},   # flips to 1
            {"position": 5, "value": 0, "changing": False},
            {"position": 6, "value": 0, "changing": False},
        ]
        binary = DivinationEngine.get_changing_binary(lines)
        self.assertEqual(binary, "101100")

    def test_get_changing_positions(self):
        lines = [
            {"position": 1, "changing": True},
            {"position": 2, "changing": False},
            {"position": 3, "changing": False},
            {"position": 4, "changing": False},
            {"position": 5, "changing": True},
            {"position": 6, "changing": False},
        ]
        positions = DivinationEngine.get_changing_positions(lines)
        self.assertEqual(positions, [1, 5])

    def test_get_yao_text(self):
        lines = [
            {"position": 1, "value": 1, "changing": False},
            {"position": 2, "value": 0, "changing": True},
            {"position": 3, "value": 1, "changing": False},
            {"position": 4, "value": 1, "changing": True},
            {"position": 5, "value": 0, "changing": False},
            {"position": 6, "value": 0, "changing": False},
        ]
        text = DivinationEngine.get_yao_text(lines)
        self.assertIn("━━━", text)
        self.assertIn("━ ━", text)
        self.assertIn("X", text.replace("×", "X"))
        self.assertIn("O", text.replace("○", "O"))

    def test_no_changing_lines(self):
        lines = [
            {"position": i, "value": v, "changing": False}
            for i, v in enumerate([1, 1, 1, 1, 1, 1], 1)
        ]
        binary = DivinationEngine.get_changing_binary(lines)
        self.assertEqual(binary, "111111")
        self.assertEqual(DivinationEngine.get_changing_positions(lines), [])


if __name__ == "__main__":
    unittest.main()

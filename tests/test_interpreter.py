#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for ResultInterpreter"""

import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yijing import HexagramDatabase, DivinationEngine, ResultInterpreter


class TestResultInterpreter(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = HexagramDatabase()
        cls.interpreter = ResultInterpreter(cls.db)

    def _make_lines(self, values=("1", "1", "1", "0", "0", "0"), changes=(False,)*6):
        return [
            {"position": i, "value": int(v), "changing": c, "label": "少阳"}
            for i, (v, c) in enumerate(zip(values, changes), 1)
        ]

    def test_interpret_no_changing_lines(self):
        lines = self._make_lines()
        result = self.interpreter.interpret(lines, "测试")
        self.assertIsNotNone(result["main_hexagram"])
        self.assertEqual(result["changing_positions"], [])
        self.assertEqual(result["main_hexagram"], result["changing_hexagram"])

    def test_interpret_with_changing_lines(self):
        lines = self._make_lines(changes=(True, False, False, False, False, False))
        result = self.interpreter.interpret(lines, "测试")
        self.assertIsNotNone(result["main_hexagram"])
        self.assertIsNotNone(result["changing_hexagram"])
        self.assertEqual(result["changing_positions"], [1])
        self.assertEqual(len(result["changing_yao_ci"]), 1)

    def test_interpret_multiple_changing_lines(self):
        lines = self._make_lines(changes=(True, False, True, False, True, False))
        result = self.interpreter.interpret(lines, "测试")
        self.assertEqual(len(result["changing_positions"]), 3)
        self.assertEqual(len(result["changing_yao_ci"]), 3)

    def test_interpret_question_is_preserved(self):
        lines = self._make_lines()
        result = self.interpreter.interpret(lines, "我的事业如何？")
        self.assertEqual(result["question"], "我的事业如何？")

    def test_interpret_empty_question(self):
        lines = self._make_lines()
        result = self.interpreter.interpret(lines, "")
        self.assertEqual(result["question"], "")

    def test_format_brief(self):
        lines = self._make_lines(values=("1","1","1","1","1","1"))
        result = self.interpreter.interpret(lines, "test")
        brief = self.interpreter.format_brief(result)
        self.assertIn("乾为天", brief)

    def test_format_brief_with_changes(self):
        lines = self._make_lines(changes=(True, False, False, False, False, False))
        result = self.interpreter.interpret(lines, "test")
        brief = self.interpreter.format_brief(result)
        self.assertIn("->", brief)
        self.assertIn("动爻", brief)

    def test_report_contains_key_sections(self):
        lines = self._make_lines(changes=(True, False, False, False, False, False))
        result = self.interpreter.interpret(lines, "事业前途")
        report = result["report"]
        self.assertIn("本卦", report)
        self.assertIn("变卦", report)
        self.assertIn("卦辞", report)
        self.assertIn("动爻详解", report)
        self.assertIn("智慧提示", report)

    def test_report_no_changes_says_no_moving_line(self):
        lines = self._make_lines()
        result = self.interpreter.interpret(lines, "test")
        report = result["report"]
        self.assertIn("无动爻", report)

    def test_yao_drawing_in_result(self):
        lines = self._make_lines()
        result = self.interpreter.interpret(lines, "test")
        self.assertIn("yao_drawing", result)
        self.assertIn("━━━", result["yao_drawing"])

    def test_yao_position_names_correct(self):
        """Test that position names match expected values."""
        self.assertEqual(
            self.interpreter.YAO_POSITION_NAMES,
            ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]
        )


if __name__ == "__main__":
    unittest.main()

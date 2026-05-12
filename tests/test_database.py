#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tests for HexagramDatabase"""

import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from yijing import HexagramDatabase


class TestHexagramDatabase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.db = HexagramDatabase()

    def test_loads_all_64_hexagrams(self):
        self.assertEqual(len(self.db.hexagrams), 64)

    def test_hexagrams_sorted_by_id(self):
        ids = [h["id"] for h in self.db.hexagrams]
        self.assertEqual(ids, list(range(1, 65)))

    def test_get_by_id(self):
        h = self.db.get_by_id(1)
        self.assertIsNotNone(h)
        self.assertEqual(h["name"], "乾为天")

        h = self.db.get_by_id(64)
        self.assertIsNotNone(h)
        self.assertEqual(h["name"], "火水未济")

        self.assertIsNone(self.db.get_by_id(0))
        self.assertIsNone(self.db.get_by_id(65))

    def test_get_by_name_full(self):
        h = self.db.get_by_name("乾为天")
        self.assertIsNotNone(h)
        self.assertEqual(h["id"], 1)

    def test_get_by_name_short(self):
        h = self.db.get_by_name("乾卦")
        self.assertIsNotNone(h)
        self.assertEqual(h["name"], "乾为天")

    def test_get_by_name_not_found(self):
        self.assertIsNone(self.db.get_by_name("不存在的卦"))

    def test_get_by_binary(self):
        # 乾为天: upper=乾(111), lower=乾(111) -> binary = 111111
        h = self.db.get_by_binary("111111")
        self.assertIsNotNone(h)
        self.assertEqual(h["name"], "乾为天")

        # 坤为地: 000000
        h = self.db.get_by_binary("000000")
        self.assertIsNotNone(h)
        self.assertEqual(h["name"], "坤为地")

    def test_get_by_binary_not_found(self):
        self.assertIsNone(self.db.get_by_binary("999999"))

    def test_get_by_trigrams(self):
        h = self.db.get_by_trigrams("乾", "乾")
        self.assertIsNotNone(h)
        self.assertEqual(h["name"], "乾为天")

        h = self.db.get_by_trigrams("坤", "坤")
        self.assertIsNotNone(h)
        self.assertEqual(h["name"], "坤为地")

    def test_search_by_keyword_in_name(self):
        results = self.db.search_by_keyword("乾")
        self.assertGreaterEqual(len(results), 1)

    def test_search_by_keyword_in_core_meaning(self):
        results = self.db.search_by_keyword("谦虚")
        self.assertGreaterEqual(len(results), 1)
        names = [h["name"] for h in results]
        self.assertIn("地山谦", names)

    def test_search_no_results(self):
        results = self.db.search_by_keyword("xyz不存在的词")
        self.assertEqual(len(results), 0)

    def test_list_all_names(self):
        names = self.db.list_all_names()
        self.assertEqual(len(names), 64)

    def test_metadata(self):
        meta = self.db.metadata
        self.assertIn("name", meta)
        self.assertEqual(meta.get("total_hexagrams"), 64)

    def test_trigrams(self):
        trigrams = self.db.trigrams
        self.assertEqual(len(trigrams), 8)

    def test_no_placeholder_text(self):
        """Verify no hexagram contains placeholder text."""
        for h in self.db.hexagrams:
            blob = json.dumps(h, ensure_ascii=False)
            self.assertNotIn("需要补充", blob,
                             f"Hexagram {h['id']} ({h['name']}) has placeholder text")

    def test_all_fields_present(self):
        required_fields = [
            "id", "name", "short_name", "unicode_symbol",
            "upper_trigram", "lower_trigram", "binary",
            "judgment", "judgment_interpretation",
            "image", "image_interpretation",
            "core_meaning", "keywords", "yao_ci",
        ]
        for h in self.db.hexagrams:
            for field in required_fields:
                self.assertIn(field, h,
                              f"Hexagram {h.get('id','?')} missing field '{field}'")

    def test_yao_ci_structure(self):
        for h in self.db.hexagrams:
            yao_ci = h.get("yao_ci", [])
            self.assertEqual(len(yao_ci), 6,
                             f"Hexagram {h['id']} has {len(yao_ci)} yao_ci, expected 6")
            for i, yao in enumerate(yao_ci):
                self.assertIn("position", yao)
                self.assertIn("text", yao)
                self.assertIn("interpretation", yao)
                self.assertTrue(yao["text"], f"Hex {h['id']} yao {i+1} text is empty")


if __name__ == "__main__":
    unittest.main()

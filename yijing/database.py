#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
六十四卦数据库模块
提供卦象数据的加载、查询与索引功能
"""

import json
import os
from typing import List, Dict, Optional, Any


class HexagramDatabase:
    """易经六十四卦数据库"""

    TRIGRAM_UNICODE = {
        "乾": "\u2630", "兑": "\u2631", "离": "\u2632", "震": "\u2633",
        "巽": "\u2634", "坎": "\u2635", "艮": "\u2636", "坤": "\u2637",
    }

    TRIGRAM_BINARY_TOP_DOWN = {
        "乾": "111", "兑": "011", "离": "101", "震": "001",
        "巽": "110", "坎": "010", "艮": "100", "坤": "000",
    }

    @staticmethod
    def _find_database() -> str:
        """Find hexagrams_db.json in common locations."""
        candidates = []
        # Same package directory
        base = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(os.path.dirname(base), "data", "hexagrams_db.json"))
        # Relative to CWD
        candidates.append(os.path.join("data", "hexagrams_db.json"))
        candidates.append("hexagrams_db.json")
        for p in candidates:
            if os.path.exists(p):
                return p
        raise FileNotFoundError(
            f"Database hexagrams_db.json not found in: {candidates}"
        )

    def __init__(self, db_path: str = None):
        """
        初始化数据库
        :param db_path: JSON数据库文件路径，默认使用 data/hexagrams_db.json
        """
        if db_path is None:
            db_path = self._find_database()
        self.db_path = db_path
        self._data = {}
        self._hexagrams = []
        self._by_binary = {}
        self._by_id = {}
        self._by_name = {}
        self._load()

    def _load(self):
        """加载并索引数据库"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f"Database not found: {self.db_path}")
        with open(self.db_path, "r", encoding="utf-8") as f:
            self._data = json.load(f)
        self._hexagrams = self._data.get("hexagrams", [])
        for h in self._hexagrams:
            self._by_id[h["id"]] = h
            self._by_binary[h.get("binary", "")] = h
            self._by_name[h["name"]] = h
            self._by_name[h.get("short_name", "")] = h
        # 按ID排序确保文王序
        self._hexagrams.sort(key=lambda x: x["id"])

    @property
    def metadata(self) -> Dict[str, Any]:
        return self._data.get("metadata", {})

    @property
    def trigrams(self) -> List[Dict[str, str]]:
        return self._data.get("trigrams", [])

    @property
    def hexagrams(self) -> List[Dict[str, Any]]:
        return self._hexagrams

    def get_by_id(self, hid: int) -> Optional[Dict[str, Any]]:
        """按ID获取卦象（1-64）"""
        return self._by_id.get(hid)

    def get_by_binary(self, binary: str) -> Optional[Dict[str, Any]]:
        """按二进制编码获取卦象（6位，从下往上）"""
        return self._by_binary.get(binary)

    def get_by_name(self, name: str) -> Optional[Dict[str, Any]]:
        """按卦名获取卦象（支持全名或简称）"""
        return self._by_name.get(name)

    def get_by_trigrams(self, upper: str, lower: str) -> Optional[Dict[str, Any]]:
        """按上下卦名查找"""
        for h in self._hexagrams:
            if h.get("upper_trigram") == upper and h.get("lower_trigram") == lower:
                return h
        return None

    def search_by_keyword(self, keyword: str) -> List[Dict[str, Any]]:
        """按关键词搜索卦象（匹配卦名、核心意义、关键词）"""
        keyword = keyword.strip()
        results = []
        for h in self._hexagrams:
            if keyword in h.get("name", ""):
                results.append(h)
                continue
            if keyword in h.get("core_meaning", ""):
                results.append(h)
                continue
            if any(keyword in k for k in h.get("keywords", [])):
                results.append(h)
                continue
        return results

    def list_all_names(self) -> List[str]:
        """列出所有卦象名称"""
        return [f"{h['id']:2d}. {h['unicode_symbol']} {h['name']}" for h in self._hexagrams]

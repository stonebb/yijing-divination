#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
算卦引擎模块
提供多种起卦方法：铜钱法、数字法、时间法
"""

import random
import time
from datetime import datetime
from typing import List, Dict, Any, Tuple


class DivinationEngine:
    """算卦引擎"""

    COIN_METHOD = "coin"
    DIGITAL_METHOD = "digital"
    TIME_METHOD = "time"

    def __init__(self, seed: int = None):
        """
        :param seed: 随机种子（用于复现卦象，可选）
        """
        self.rng = random.Random(seed)

    def toss_coins(self) -> List[Dict[str, Any]]:
        """
        铜钱起卦法（传统三钱法）
        每爻投掷三枚铜钱：
        - 字面朝上（阴）计 2，背面朝上（阳）计 3
        - 三枚总和：
          6 = 老阴 (少阴之变，阴动，0->1)
          7 = 少阳 (不变之阳，1)
          8 = 少阴 (不变之阴，0)
          9 = 老阳 (少阳之变，阳动，1->0)
        返回从下往上排列的六爻列表
        """
        lines = []
        for i in range(6):
            coins = [self.rng.choice([2, 3]) for _ in range(3)]
            total = sum(coins)
            if total == 6:
                value, changing = 0, True
                label = "老阴"
            elif total == 7:
                value, changing = 1, False
                label = "少阳"
            elif total == 8:
                value, changing = 0, False
                label = "少阴"
            else:  # total == 9
                value, changing = 1, True
                label = "老阳"
            lines.append({
                "position": i + 1,  # 1-based, from bottom
                "value": value,     # 0=yin, 1=yang
                "changing": changing,
                "label": label,
                "coins": coins,
                "coin_sum": total,
            })
        return lines

    def digital_method(self, changing_lines: int = None) -> List[Dict[str, Any]]:
        """
        数字起卦法（简捷现代法）
        直接生成6个0/1随机数，再随机指定1-3个动爻
        :param changing_lines: 指定动爻数量，None则随机1-3
        """
        lines = []
        values = [self.rng.randint(0, 1) for _ in range(6)]
        if changing_lines is None:
            changing_lines = self.rng.randint(1, 3)
        changing_positions = self.rng.sample(range(6), changing_lines)
        for i in range(6):
            value = values[i]
            changing = i in changing_positions
            if changing:
                label = "老阳" if value == 1 else "老阴"
            else:
                label = "少阳" if value == 1 else "少阴"
            lines.append({
                "position": i + 1,
                "value": value,
                "changing": changing,
                "label": label,
            })
        return lines

    def time_method(self, timestamp: float = None) -> List[Dict[str, Any]]:
        """
        时间起卦法（梅花易数简化版）
        以当前时间（年月日时分）的数字起卦
        """
        if timestamp is None:
            timestamp = time.time()
        dt = datetime.fromtimestamp(timestamp)
        # 年+月+日 为上卦，月+日+时 为下卦
        year, month, day, hour = dt.year, dt.month, dt.day, dt.hour
        upper_idx = (year + month + day) % 8
        lower_idx = (month + day + hour) % 8
        # 动爻
        changing_idx = (year + month + day + hour) % 6
        # 映射到八卦（0-7对应乾兑离震巽坎艮坤）
        trigram_map = ["111", "011", "101", "001", "110", "010", "100", "000"]
        upper_bin = trigram_map[upper_idx]
        lower_bin = trigram_map[lower_idx]
        # 组合为六爻（二进制采用下往上，每卦内部也下往上）
        # upper_bin 和 lower_bin 是自上而下的三爻
        # 转换为自下而上：反转
        def to_bottom_up(td: str) -> str:
            return td[::-1]
        full = to_bottom_up(lower_bin) + to_bottom_up(upper_bin)
        lines = []
        for i, b in enumerate(full):
            value = int(b)
            changing = (i == changing_idx)
            if changing:
                label = "老阳" if value == 1 else "老阴"
            else:
                label = "少阳" if value == 1 else "少阴"
            lines.append({
                "position": i + 1,
                "value": value,
                "changing": changing,
                "label": label,
                "time_params": {"year": year, "month": month, "day": day, "hour": hour},
            })
        return lines

    @staticmethod
    def get_hexagram_binary(lines: List[Dict[str, Any]]) -> str:
        """由爻列表生成本卦二进制编码（下往上）"""
        return "".join(str(line["value"]) for line in lines)

    @staticmethod
    def get_changing_binary(lines: List[Dict[str, Any]]) -> str:
        """由爻列表生成变卦二进制编码（动爻翻转）"""
        return "".join(
            str(1 - line["value"]) if line["changing"] else str(line["value"])
            for line in lines
        )

    @staticmethod
    def get_changing_positions(lines: List[Dict[str, Any]]) -> List[int]:
        """获取所有动爻的位置（1-based）"""
        return [line["position"] for line in lines if line["changing"]]

    @staticmethod
    def get_yao_text(lines: List[Dict[str, Any]]) -> str:
        """将爻列表渲染为爻画文本"""
        symbols = []
        for line in reversed(lines):  # 从上往下展示
            if line["value"] == 1:
                base = "━━━"
            else:
                base = "━ ━"
            if line["changing"]:
                base += " ○" if line["value"] == 1 else " ×"
            symbols.append(base)
        return "\n".join(symbols)

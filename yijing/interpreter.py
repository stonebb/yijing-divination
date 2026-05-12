#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
解卦与格式化模块
根据提示词模板结构，生成完整的卦象解读
"""

from typing import List, Dict, Any, Optional
from .database import HexagramDatabase


class ResultInterpreter:
    """卦象结果解释器"""

    YAO_POSITION_NAMES = ["初爻", "二爻", "三爻", "四爻", "五爻", "上爻"]

    def __init__(self, db: HexagramDatabase):
        self.db = db

    def interpret(self, lines: List[Dict[str, Any]], question: str = "") -> Dict[str, Any]:
        """
        对一组爻象进行完整解读
        :param lines: DivinationEngine 生成的六爻列表
        :param question: 用户所问之事
        :return: 结构化解读结果
        """
        from .divination import DivinationEngine
        main_binary = DivinationEngine.get_hexagram_binary(lines)
        change_binary = DivinationEngine.get_changing_binary(lines)
        changing_positions = DivinationEngine.get_changing_positions(lines)

        main_hex = self.db.get_by_binary(main_binary)
        change_hex = self.db.get_by_binary(change_binary)

        result = {
            "question": question,
            "main_hexagram": main_hex,
            "changing_hexagram": change_hex,
            "lines": lines,
            "changing_positions": changing_positions,
            "yao_drawing": DivinationEngine.get_yao_text(lines),
        }

        # 动爻辞集合
        result["changing_yao_ci"] = []
        if main_hex and changing_positions:
            yao_ci_list = main_hex.get("yao_ci", [])
            for pos in changing_positions:
                idx = pos - 1
                if 0 <= idx < len(yao_ci_list):
                    yao_entry = dict(yao_ci_list[idx])
                    yao_entry["position_num"] = pos
                    yao_entry["position_name"] = self.YAO_POSITION_NAMES[idx]
                    result["changing_yao_ci"].append(yao_entry)

        # 生成文本报告
        result["report"] = self._generate_report(result)
        return result

    def _generate_report(self, result: Dict[str, Any]) -> str:
        """生成完整的文本报告"""
        parts = []
        q = result.get("question", "").strip()
        main = result.get("main_hexagram")
        change = result.get("changing_hexagram")
        lines = result.get("lines", [])
        changing_positions = result.get("changing_positions", [])
        yao_drawing = result.get("yao_drawing", "")
        changing_yao_ci = result.get("changing_yao_ci", [])

        # 标题
        parts.append("=" * 40)
        parts.append("          易 经 算 卦")
        parts.append("=" * 40)

        # 所问之事
        if q:
            parts.append(f"\n【所问】{q}\n")
        else:
            parts.append("")

        # 卦象图
        parts.append("【卦象图】")
        parts.append(yao_drawing)
        parts.append("")

        # 本卦信息
        if main:
            parts.append(f"【本卦】{main['unicode_symbol']} {main['name']} ({main['short_name']})")
            parts.append(f"      上卦：{main.get('upper_trigram_unicode','')} {main.get('upper_trigram','')}")
            parts.append(f"      下卦：{main.get('lower_trigram_unicode','')} {main.get('lower_trigram','')}")
            parts.append(f"      核心意义：{main.get('core_meaning','')}")
            parts.append("")

        # 变卦信息
        if change and changing_positions:
            parts.append(f"【变卦】{change['unicode_symbol']} {change['name']} ({change['short_name']})")
            parts.append(f"      动爻位置：{', '.join(str(p) for p in changing_positions)}")
            parts.append("")
        elif not changing_positions:
            parts.append("【变卦】无动爻，卦象不变")
            parts.append("")

        # 卦辞
        if main:
            parts.append("【卦辞解读】")
            parts.append(f"  卦辞：{main.get('judgment','')}")
            parts.append(f"  释义：{main.get('judgment_interpretation','')}")
            parts.append("")
            parts.append("【象曰】")
            parts.append(f"  {main.get('image','')}")
            parts.append(f"  {main.get('image_interpretation','')}")
            parts.append("")

        # 动爻辞
        if changing_yao_ci:
            parts.append("【动爻详解】")
            for yao in changing_yao_ci:
                parts.append(f"  ▶ {yao['position_name']}：{yao['text']}")
                parts.append(f"    解读：{yao['interpretation']}")
                parts.append("")

        # 智慧提示
        parts.append("【智慧提示】")
        if main:
            keywords = "、".join(main.get("keywords", []))
            parts.append(f"  关键词：{keywords}")
            parts.append(f"  {main.get('core_meaning','')}")
        if q:
            parts.append(f"\n  针对您所问的「{q}」，本卦提示：")
            if changing_yao_ci:
                parts.append(f"  当前正处于转变的节点，动爻揭示了事情发展的关键动向。")
            else:
                parts.append(f"  当前局势相对稳定，宜按卦辞所示的大方向行事。")
        parts.append("")

        parts.append("=" * 40)
        parts.append("  易经算卦仅供参考，决断在于自己")
        parts.append("=" * 40)

        return "\n".join(parts)

    def format_brief(self, result: Dict[str, Any]) -> str:
        """生成简要报告（一行式）"""
        main = result.get("main_hexagram")
        change = result.get("changing_hexagram")
        positions = result.get("changing_positions", [])
        if not main:
            return "未知卦象"
        s = f"{main['unicode_symbol']} {main['name']}"
        if positions and change:
            s += f" -> {change['unicode_symbol']} {change['name']} (动爻: {positions})"
        return s

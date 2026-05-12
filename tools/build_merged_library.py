#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
合并多来源易经卦数据为单一完整库。

指定主文件：易经六十四卦数据库.json（校验通过、字段说明完整、1–6 卦内容详实）

合并策略：以 generate_complete_db.get_all_hexagrams() 为 64 卦骨架（保证条数），
再按优先级叠加较优来源；最后根据上下卦统一 binary 与 unicode_symbol。
"""

from __future__ import annotations

import importlib.util
import json
import pathlib
from copy import deepcopy
from typing import Any, Dict, List, Optional

ROOT = pathlib.Path(__file__).resolve().parent

TRIGRAM_BINARY = {
    "乾": "111",
    "兑": "011",
    "离": "101",
    "震": "001",
    "巽": "110",
    "坎": "010",
    "艮": "100",
    "坤": "000",
}

TRIGRAM_UNICODE = {
    "乾": "☰",
    "兑": "☱",
    "离": "☲",
    "震": "☳",
    "巽": "☴",
    "坎": "☵",
    "艮": "☶",
    "坤": "☷",
}


def _load_module(name: str, path: pathlib.Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


def _detail_score(h: Dict[str, Any]) -> int:
    if not isinstance(h, dict):
        return -10**9
    blob = json.dumps(h, ensure_ascii=False)
    if "需要补充" in blob or "（需要补充）" in blob:
        return -10**6
    s = 0
    for k in (
        "judgment",
        "judgment_interpretation",
        "image",
        "image_interpretation",
        "core_meaning",
    ):
        v = h.get(k)
        if isinstance(v, str) and v.strip():
            s += min(len(v), 800)
    yao = h.get("yao_ci") or []
    if isinstance(yao, list):
        for y in yao:
            if isinstance(y, dict):
                for kk in ("text", "interpretation"):
                    vv = y.get(kk)
                    if isinstance(vv, str) and vv.strip() and "需要补充" not in vv:
                        s += min(len(vv), 400)
    kw = h.get("keywords")
    if isinstance(kw, list) and kw and kw != ["需要补充"]:
        s += len(kw) * 8
    return s


def _fix_truncated_json(text: str) -> str:
    t = text.rstrip()
    if t.endswith("}"):
        return text
    if '"hexagrams"' in text:
        if not t.endswith("]"):
            if t.rstrip().endswith("}"):
                return t + "\n  ]\n}\n"
    return text


def _load_json_file(path: pathlib.Path) -> Optional[dict]:
    if not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        fixed = _fix_truncated_json(text)
        try:
            return json.loads(fixed)
        except json.JSONDecodeError:
            return None


def _by_id(hexagrams: List[dict]) -> Dict[int, dict]:
    out: Dict[int, dict] = {}
    for h in hexagrams:
        if isinstance(h, dict) and "id" in h:
            out[int(h["id"])] = h
    return out


def _merge_record(
    base: dict, incoming: dict, prefer_fields: Optional[List[str]] = None
) -> dict:
    """若 incoming 评分更高则整记录替换；否则可按字段合并。"""
    if _detail_score(incoming) > _detail_score(base):
        merged = deepcopy(incoming)
        return merged
    if prefer_fields:
        out = deepcopy(base)
        for f in prefer_fields:
            if f in incoming and incoming[f]:
                out[f] = incoming[f]
        return out
    return deepcopy(base)


def _apply_trigram_derived_fields(h: dict) -> dict:
    out = deepcopy(h)
    u = out.get("upper_trigram")
    l = out.get("lower_trigram")
    if u in TRIGRAM_UNICODE and l in TRIGRAM_UNICODE:
        # 展示顺序：上卦 + 下卦（与仓库 JSON 一致）；二进制：下爻至上爻（每卦自下而上三位）
        out["unicode_symbol"] = TRIGRAM_UNICODE[u] + TRIGRAM_UNICODE[l]
        out["binary"] = TRIGRAM_BINARY[l] + TRIGRAM_BINARY[u]
    return out


def build_merged() -> dict:
    gdb = _load_module("generate_complete_db", ROOT / "generate_complete_db.py")
    gh = _load_module("generate_hexagram_db", ROOT / "generate_hexagram_db.py")
    ch = _load_module("complete_hexagrams", ROOT / "complete_hexagrams.py")

    skeleton_list = gdb.get_all_hexagrams()
    by_id: Dict[int, dict] = _by_id(skeleton_list)

    canonical_path = ROOT / "易经六十四卦数据库.json"
    canonical = _load_json_file(canonical_path)
    if not canonical:
        raise RuntimeError("指定主文件缺失或无法解析: 易经六十四卦数据库.json")

    layers: List[tuple[str, Optional[dict]]] = [
        ("generate_hexagram_database", gh.generate_hexagram_database()),
        ("canonical_易经六十四卦数据库", canonical),
        ("batch1_卦1-16", _load_json_file(ROOT / "batch1_卦1-16.json")),
        ("batch1_卦3-10_真正完整版", _load_json_file(ROOT / "batch1_卦3-10_真正完整版.json")),
        ("batch1_卦3-10_完整版", _load_json_file(ROOT / "batch1_卦3-10_完整版.json")),
    ]

    tail54 = getattr(ch, "new_hexagrams", [])
    if tail54:
        layers.append(
            (
                "complete_hexagrams_new_hexagrams",
                {"hexagrams": tail54},
            )
        )

    for layer_name, data in layers:
        if not data:
            continue
        hs = data.get("hexagrams")
        if not hs:
            continue
        for h in hs:
            if not isinstance(h, dict) or "id" not in h:
                continue
            hid = int(h["id"])
            cur = by_id.get(hid)
            if cur is None:
                by_id[hid] = deepcopy(h)
                continue
            merged = _merge_record(cur, h)
            by_id[hid] = merged

    # 从 generate_complete_64 补卦辞/解读（该脚本含 hex_info_list 全文，但爻多为占位）
    gc64 = _load_module("generate_complete_64", ROOT / "generate_complete_64.py")
    for h in gc64.get_complete_64_hexagrams():
        if not isinstance(h, dict) or "id" not in h:
            continue
        hid = int(h["id"])
        cur = by_id.get(hid)
        if cur is None:
            continue
        j = h.get("judgment") or ""
        ji = h.get("judgment_interpretation") or ""
        if j and "需要补充" not in j:
            cur["judgment"] = j
        if ji and "需要补充" not in ji:
            cur["judgment_interpretation"] = ji

    ordered = [by_id[i] for i in sorted(by_id.keys())]
    if len(ordered) != 64:
        raise RuntimeError(f"合并后期望 64 卦，实际 {len(ordered)}")

    ordered = [_apply_trigram_derived_fields(h) for h in ordered]

    trigrams_out = {
        name: {
            "unicode": sym,
            "nature": {"乾": "天", "兑": "泽", "离": "火", "震": "雷", "巽": "风", "坎": "水", "艮": "山", "坤": "地"}[
                name
            ],
            "attribute": {"乾": "健", "兑": "悦", "离": "丽", "震": "动", "巽": "入", "坎": "陷", "艮": "止", "坤": "顺"}[
                name
            ],
            "binary": TRIGRAM_BINARY[name],
        }
        for name, sym in TRIGRAM_UNICODE.items()
    }

    yao_placeholder_ids = []
    for h in ordered:
        blob = json.dumps(h.get("yao_ci") or [], ensure_ascii=False)
        if "需要补充" in blob:
            yao_placeholder_ids.append(int(h["id"]))

    meta = {
        "name": "易经六十四卦完整库",
        "version": "1.0",
        "description": "合并自仓库多来源；卦爻优先采用详实批次与脚本，结构与二进制按上下卦统一。",
        "source": "基于王弼注本《周易》整理；合并脚本 build_merged_library.py",
        "total_hexagrams": 64,
        "canonical_json_file": "易经六十四卦数据库.json",
        "merge_note": (
            "主参考 JSON：易经六十四卦数据库.json；64 卦骨架来自 generate_complete_db.py；"
            "1–8 卦叠加 generate_hexagram_db；1–2、3–4 叠加 batch 批次；卦辞/卦解中间隙由 generate_complete_64 补全；54–64 叠加 complete_hexagrams.new_hexagrams。"
            "binary/unicode_symbol 由 upper_trigram/lower_trigram 推导。"
        ),
        "fields": (canonical.get("metadata") or {}).get("fields"),
        "yao_placeholder_remaining_ids": yao_placeholder_ids,
        "yao_placeholder_count": len(yao_placeholder_ids),
    }

    return {
        "metadata": meta,
        "trigrams": trigrams_out,
        "hexagrams": ordered,
    }


def main():
    out_path = ROOT / "易经六十四卦完整库.json"
    data = build_merged()
    out_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"已写入: {out_path}")
    print(f"卦数: {len(data['hexagrams'])}")
    m = data["metadata"]
    n = m.get("yao_placeholder_count", 0)
    print(f"爻辞仍为占位的卦数量: {n}（见 metadata.yao_placeholder_remaining_ids）")


if __name__ == "__main__":
    main()

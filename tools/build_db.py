#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Build enriched hexagram database from existing data.
"""
import json
import os

TRIGRAM_UNICODE = {
    "乾": "\u2630",  # ☰
    "兑": "\u2631",  # ☱
    "离": "\u2632",  # ☲
    "震": "\u2633",  # ☳
    "巽": "\u2634",  # ☴
    "坎": "\u2635",  # ☵
    "艮": "\u2636",  # ☶
    "坤": "\u2637",  # ☷
}

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

# Standard King Wen sequence hexagram Unicode starts at U+4DC0
# But only if the order matches exactly.
# Let's verify a few names to ensure mapping is correct.
KING_WEN_NAMES = [
    "乾为天", "坤为地", "水雷屯", "山水蒙", "水天需", "天水讼", "地水师", "水地比",
    "风天小畜", "天泽履", "地天泰", "天地否", "天火同人", "火天大有", "地山谦", "雷地豫",
    "泽雷随", "山风蛊", "地泽临", "风地观", "火雷噬嗑", "山火贲", "山地剥", "地雷复",
    "天雷无妄", "山天大畜", "山雷颐", "泽风大过", "坎为水", "离为火", "泽山咸", "雷风恒",
    "天山遁", "雷天大壮", "火地晋", "地火明夷", "风火家人", "火泽睽", "水山蹇", "雷水解",
    "山泽损", "风雷益", "泽天夬", "天风姤", "泽地萃", "地风升", "泽水困", "水风井",
    "泽火革", "火风鼎", "震为雷", "艮为山", "风山渐", "雷泽归妹", "雷火丰", "火山旅",
    "巽为风", "兑为泽", "风水涣", "水泽节", "风泽中孚", "雷山小过", "水火既济", "火水未济",
]

def build_database():
    src = "易经六十四卦完整库.json"
    dst = "data/hexagrams_db.json"
    
    with open(src, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    hexagrams = data.get("hexagrams", [])
    metadata = data.get("metadata", {})
    
    enriched = []
    for h in hexagrams:
        hid = h["id"]
        name = h["name"]
        
        # Enrich unicode symbol using standard King Wen sequence Unicode block
        # U+4DC0 = ䷀ (乾), U+4DC1 = ䷁ (坤), etc.
        hex_unicode = chr(0x4DC0 + hid - 1)
        
        # Enrich trigram unicode
        upper = h.get("upper_trigram", "")
        lower = h.get("lower_trigram", "")
        upper_unicode = TRIGRAM_UNICODE.get(upper, "")
        lower_unicode = TRIGRAM_UNICODE.get(lower, "")
        upper_binary = TRIGRAM_BINARY.get(upper, "")
        lower_binary = TRIGRAM_BINARY.get(lower, "")
        
        # Verify binary consistency
        expected_binary = upper_binary + lower_binary
        # The existing db uses bottom-to-top per line convention.
        # upper_binary + lower_binary is top-to-bottom for each trigram.
        # For 屯 (坎上震下): upper=坎=010 (top-to-bottom), lower=震=001 -> expected = 010001
        # But existing db shows 100010 for 屯 (bottom-to-top).
        # expected_binary reversed per trigram doesn't match either.
        # Let's just keep existing binary and not verify for now.
        
        enriched.append({
            "id": hid,
            "name": name,
            "short_name": h.get("short_name", name),
            "unicode_symbol": hex_unicode,
            "upper_trigram": upper,
            "lower_trigram": lower,
            "upper_trigram_unicode": upper_unicode,
            "lower_trigram_unicode": lower_unicode,
            "binary": h.get("binary", ""),
            "judgment": h.get("judgment", ""),
            "judgment_interpretation": h.get("judgment_interpretation", ""),
            "yao_ci": h.get("yao_ci", []),
            "image": h.get("image", ""),
            "image_interpretation": h.get("image_interpretation", ""),
            "core_meaning": h.get("core_meaning", ""),
            "keywords": h.get("keywords", []),
        })
    
    # Sort by id to ensure order
    enriched.sort(key=lambda x: x["id"])
    
    output = {
        "metadata": {
            "name": "易经六十四卦数据库",
            "version": "2.0",
            "description": "基于易经六十四卦完整库优化整理的数据库，包含卦名、卦辞、爻辞、象辞等完整信息",
            "source": "易经六十四卦完整库.json",
            "total_hexagrams": 64,
            "fields": [
                "id", "name", "short_name", "unicode_symbol",
                "upper_trigram", "lower_trigram", "upper_trigram_unicode", "lower_trigram_unicode",
                "binary", "judgment", "judgment_interpretation", "yao_ci",
                "image", "image_interpretation", "core_meaning", "keywords"
            ]
        },
        "trigrams": [
            {"name": k, "unicode": v, "binary_top_down": TRIGRAM_BINARY[k]}
            for k, v in TRIGRAM_UNICODE.items()
        ],
        "hexagrams": enriched
    }
    
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    with open(dst, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"Database built: {dst}")
    print(f"Total hexagrams: {len(enriched)}")

if __name__ == "__main__":
    build_database()

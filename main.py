#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
易经算卦 v1.0.0 - 命令行版
Usage:
    python main.py                    交互式算卦
    python main.py -q "问事业"         直接提问算卦
    python main.py -m coin            使用铜钱法（默认）
    python main.py -m digital         使用数字法
    python main.py -m time            使用时间法
    python main.py -l                 列出全部六十四卦
    python main.py -s 事业            按关键词搜索卦象
    python main.py -n 乾为天          查询指定卦象
    python main.py --simple           简要模式
    python main.py --ascii            纯ASCII模式（无Unicode符号）
"""

import argparse
import os
import sys

# Fix Windows console encoding for Unicode hexagram symbols
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        os.system("chcp 65001 > nul")

from yijing import HexagramDatabase, DivinationEngine, ResultInterpreter

# ── ANSI color helpers ──
C = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "cyan": "\033[36m",
    "white": "\033[37m",
}

NO_COLOR = not sys.stdout.isatty()


def c(code: str, text: str) -> str:
    """Wrap text with ANSI color code, skip if not a terminal."""
    if NO_COLOR:
        return text
    return f"{C.get(code, '')}{text}{C['reset']}"


# ── ASCII fallback for hexagram/trigram symbols ──
ASCII_HEXAGRAM = [
    " 乾(1)", " 坤(2)", " 屯(3)", " 蒙(4)", " 需(5)", " 讼(6)", " 师(7)", " 比(8)",
    "小畜(9)", " 履(10)", " 泰(11)", " 否(12)", "同人(13)", "大有(14)", " 谦(15)", " 豫(16)",
    " 随(17)", " 蛊(18)", " 临(19)", " 观(20)", "噬嗑(21)", " 贲(22)", " 剥(23)", " 复(24)",
    "无妄(25)", "大畜(26)", " 颐(27)", "大过(28)", " 坎(29)", " 离(30)", " 咸(31)", " 恒(32)",
    " 遁(33)", "大壮(34)", " 晋(35)", "明夷(36)", "家人(37)", " 睽(38)", " 蹇(39)", " 解(40)",
    " 损(41)", " 益(42)", " 夬(43)", " 姤(44)", " 萃(45)", " 升(46)", " 困(47)", " 井(48)",
    " 革(49)", " 鼎(50)", " 震(51)", " 艮(52)", " 渐(53)", "归妹(54)", " 丰(55)", " 旅(56)",
    " 巽(57)", " 兑(58)", " 涣(59)", " 节(60)", "中孚(61)", "小过(62)", "既济(63)", "未济(64)",
]

ASCII_TRIGRAM = {"乾": "===", "兑": "=-=", "离": "=-=", "震": "-==",
                 "巽": "==-", "坎": "-=-", "艮": "--=", "坤": "---"}

YANG_LINE = "━━━━━"
YIN_LINE  = "━━ ━━"


def yao_ascii(lines, reverse=True):
    """Render six lines as ASCII art (top-to-bottom)."""
    items = lines[:]
    if reverse:
        items = list(reversed(lines))
    out = []
    for line in items:
        base = YANG_LINE if line["value"] == 1 else YIN_LINE
        if line["changing"]:
            mark = " O" if line["value"] == 1 else " X"
            base += mark
        out.append(base)
    return "\n".join(out)


def print_banner(ascii_mode=False):
    print(c("bold", "=" * 50))
    print(c("yellow", "        易 经 算 卦 应 用  (CLI)"))
    print(c("bold", "=" * 50))


def interactive_divination(db, method="coin", seed=None, simple=False,
                         ascii_mode=False, question=""):
    """交互式算卦"""
    print_banner(ascii_mode)

    if not question:
        print()
        print(c("cyan", "起卦方法："))
        print(f"  [coin]    铜钱法 - 模拟三枚铜钱投掷")
        print(f"  [digital] 数字法 - 随机生成爻象")
        print(f"  [time]    时间法 - 以当前时间起卦")
        print(f"  {c('dim', f'当前：{method}')}")
        print("-" * 50)
        question = input(f"\n{c('green', '请输入您要占问的事情（直接回车可跳过）：')}\n> ").strip()

    print(f"\n{c('yellow', '正在起卦...')}\n")

    engine = DivinationEngine(seed=seed)
    method_map = {
        "coin": engine.toss_coins,
        "digital": engine.digital_method,
        "time": engine.time_method,
    }
    if method not in method_map:
        print(c("red", f"未知方法：{method}"))
        return
    lines = method_map[method]()

    interpreter = ResultInterpreter(db)
    result = interpreter.interpret(lines, question)

    if simple:
        print(_simple_report(result, ascii_mode))
    else:
        print(_full_report(result, ascii_mode))


def _simple_report(result, ascii_mode=False):
    """Generate a brief one-paragraph report."""
    main = result.get("main_hexagram")
    change = result.get("changing_hexagram")
    positions = result.get("changing_positions", [])
    q = result.get("question", "")

    name = main["short_name"] if ascii_mode else f"{main['unicode_symbol']} {main['name']}"
    parts = [c("bold", f"本卦：{name}")]
    parts.append(c("cyan", f"核心：{main.get('core_meaning', '')}"))

    if positions and change:
        cname = change["short_name"] if ascii_mode else f"{change['unicode_symbol']} {change['name']}"
        parts.append(c("yellow", f"变卦：{cname}（动爻第{','.join(str(p) for p in positions)}爻）"))

    if q:
        parts.append(f"\n所问：{q}")
    parts.append(f"\n{c('green', '卦辞：')}{main.get('judgment', '')}")
    parts.append(f"{c('dim', '释义：')}{main.get('judgment_interpretation', '')}")

    if result.get("changing_yao_ci"):
        parts.append(f"\n{c('yellow', '动爻提示：')}")
        for yao in result["changing_yao_ci"]:
            parts.append(f"  {yao['position_name']}：{yao['interpretation']}")

    return "\n".join(parts)


def _full_report(result, ascii_mode=False):
    """Generate the complete divination report."""
    parts = []
    q = result.get("question", "").strip()
    main = result.get("main_hexagram")
    change = result.get("changing_hexagram")
    lines = result.get("lines", [])
    changing_positions = result.get("changing_positions", [])
    changing_yao_ci = result.get("changing_yao_ci", [])

    parts.append(c("bold", "=" * 40))
    parts.append(c("yellow", "          易 经 算 卦"))
    parts.append(c("bold", "=" * 40))

    if q:
        parts.append(f"\n{c('cyan', '【所问】')} {q}\n")

    # 卦象图
    parts.append(c("cyan", "【卦象图】"))
    parts.append(yao_ascii(lines))
    parts.append("")

    # 本卦
    if main:
        name = main["short_name"] if ascii_mode else f"{main['unicode_symbol']} {main['name']}"
        parts.append(c("bold", f"【本卦】{name} （{main['short_name']}）"))
        if not ascii_mode:
            parts.append(f"      上卦：{main.get('upper_trigram_unicode','')} {main.get('upper_trigram','')}")
            parts.append(f"      下卦：{main.get('lower_trigram_unicode','')} {main.get('lower_trigram','')}")
        else:
            parts.append(f"      上卦：{main.get('upper_trigram','')}")
            parts.append(f"      下卦：{main.get('lower_trigram','')}")
        parts.append(f"      {c('green', '核心意义：')}{main.get('core_meaning','')}")
        parts.append("")

    # 变卦
    if change and changing_positions:
        cname = change["short_name"] if ascii_mode else f"{change['unicode_symbol']} {change['name']}"
        parts.append(c("yellow", f"【变卦】{cname} （{change['short_name']}）"))
        parts.append(f"      动爻位置：第{', '.join(str(p) for p in changing_positions)}爻")
        parts.append("")
    elif not changing_positions:
        parts.append(c("dim", "【变卦】无动爻，卦象不变"))
        parts.append("")

    # 卦辞
    if main:
        parts.append(c("cyan", "【卦辞解读】"))
        parts.append(f"  卦辞：{main.get('judgment','')}")
        parts.append(f"  释义：{main.get('judgment_interpretation','')}")
        parts.append("")
        parts.append(c("cyan", "【象曰】"))
        parts.append(f"  {main.get('image','')}")
        parts.append(f"  {main.get('image_interpretation','')}")
        parts.append("")

    # 动爻辞
    if changing_yao_ci:
        parts.append(c("yellow", "【动爻详解】"))
        for yao in changing_yao_ci:
            parts.append(f"  {c('bold', '▶ ' + yao['position_name'])}：{yao['text']}")
            parts.append(f"    解读：{yao['interpretation']}")
            parts.append("")

    # 智慧提示
    parts.append(c("cyan", "【智慧提示】"))
    if main:
        keywords = "、".join(main.get("keywords", []))
        parts.append(f"  关键词：{keywords}")
        parts.append(f"  {main.get('core_meaning','')}")
    if q:
        parts.append(f"\n  针对「{q}」，本卦提示：")
        if changing_yao_ci:
            parts.append("  当前正处于转变的节点，动爻揭示了事情发展的关键动向。")
        else:
            parts.append("  当前局势相对稳定，宜按卦辞所示的大方向行事。")
    parts.append("")

    parts.append(c("dim", "=" * 40))
    parts.append(c("dim", "  易经算卦仅供参考，决断在于自己"))
    parts.append(c("dim", "=" * 40))

    return "\n".join(parts)


def list_hexagrams(db, ascii_mode=False):
    print_banner(ascii_mode)
    print(f"\n{c('cyan', '六十四卦目录（文王序）：')}\n")
    for h in db.hexagrams:
        hid = h["id"]
        if ascii_mode:
            sym = f"[{hid:2d}]"
        else:
            sym = h["unicode_symbol"]
        line = f"  {sym} {c('bold', h['name'])} - {h['core_meaning']}"
        print(line)
    print(f"\n{c('dim', f'共 {len(db.hexagrams)} 卦')}")


def search_hexagrams(db, keyword, ascii_mode=False):
    results = db.search_by_keyword(keyword)
    print_banner(ascii_mode)
    print(f"\n{c('cyan', f'关键词「{keyword}」搜索结果：')}\n")
    if not results:
        print(f"  {c('dim', '未找到匹配的卦象。')}")
        return
    for h in results:
        sym = h["short_name"] if ascii_mode else h["unicode_symbol"]
        print(f"  {sym} {c('bold', h['name'])} - {h['core_meaning']}")


def show_hexagram(db, name, ascii_mode=False):
    h = db.get_by_name(name)
    if not h:
        print(c("red", f"未找到卦象：{name}"))
        print(c("dim", "提示：使用 -l 查看所有卦名，或使用简称如「乾」「坤」"))
        return
    print_banner(ascii_mode)
    sym = h["short_name"] if ascii_mode else h["unicode_symbol"]
    header = f"【{sym} {h['name']}】"
    print(f"\n{c('bold', header)}\n")
    print(f"  简称：{h['short_name']}")
    if ascii_mode:
        print(f"  上卦：{h.get('upper_trigram','')}")
        print(f"  下卦：{h.get('lower_trigram','')}")
    else:
        print(f"  上卦：{h.get('upper_trigram_unicode','')} {h.get('upper_trigram','')}")
        print(f"  下卦：{h.get('lower_trigram_unicode','')} {h.get('lower_trigram','')}")
        print(f"  二进制：{h['binary']}")
    print(f"  {c('green', '核心意义：')}{h['core_meaning']}")
    print(f"  关键词：{'、'.join(h.get('keywords', []))}")
    print()
    print(f"  {c('cyan', '卦辞：')}{h['judgment']}")
    print(f"  释义：{h['judgment_interpretation']}")
    print()
    print(f"  {c('cyan', '象曰：')}{h['image']}")
    print(f"  象解：{h['image_interpretation']}")
    print()
    print(f"  {c('cyan', '爻辞：')}")
    for i, yao in enumerate(h.get("yao_ci", [])):
        print(f"    {c('bold', yao['position'])}：{yao['text']}")
        print(f"       {c('dim', yao['interpretation'])}")


def main():
    parser = argparse.ArgumentParser(
        description="易经算卦应用 - 命令行版",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-q", "--question", type=str, default="",
                        help="占问之事")
    parser.add_argument("-m", "--method", type=str, default="coin",
                        choices=["coin", "digital", "time"],
                        help="起卦方法")
    parser.add_argument("-l", "--list", action="store_true",
                        help="列出全部六十四卦")
    parser.add_argument("-s", "--search", type=str, default="",
                        help="按关键词搜索卦象")
    parser.add_argument("-n", "--name", type=str, default="",
                        help="查询指定卦象（全名或简称）")
    parser.add_argument("--seed", type=int, default=None,
                        help="随机种子（用于复现卦象）")
    parser.add_argument("--simple", action="store_true",
                        help="简要模式（只输出核心信息）")
    parser.add_argument("--ascii", action="store_true",
                        help="纯ASCII模式（不使用Unicode卦符）")
    args = parser.parse_args()

    db = HexagramDatabase()

    if args.list:
        list_hexagrams(db, ascii_mode=args.ascii)
        return

    if args.search:
        search_hexagrams(db, args.search, ascii_mode=args.ascii)
        return

    if args.name:
        show_hexagram(db, args.name, ascii_mode=args.ascii)
        return

    interactive_divination(db, method=args.method, seed=args.seed,
                           simple=args.simple, ascii_mode=args.ascii,
                           question=args.question)


if __name__ == "__main__":
    main()

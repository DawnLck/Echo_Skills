#!/usr/bin/env python3
"""Heuristic lint for 无限回响 drafts.

Usage:
  python style_check.py path/to/draft.md
  python style_check.py draft.md --genre product
Exit 0 always; prints PASS/WARN/FAIL checklist (agents should fix FAIL/WARN).
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HONEST = re.compile(
    r"但是.?老实说|说实话|滤镜碎|毫无意义|崩溃|坑|别提了|我得诚实"
)
DEFINITION = re.compile(
    r"一句话|大白话|本质就是|不是工具，不是模板|重新命名|忘掉吧"
)
CONTRAST = re.compile(
    r"糟糕|好的提问|不是.{0,12}而是|对比|巷战|将才|vs|VS|versus"
)
ACTIONABLE = re.compile(
    r"技巧|步骤|清单|防坑|Q[:：]|第一|第二|第三|可以这样|野路子|总结"
)
METAPHOR_BUCKETS = {
    "partner": re.compile(r"合伙人|实习生|包工头|调兵遣将|流水线"),
    "skillpack": re.compile(r"经验包|智能仓库|技能包"),
    "light": re.compile(r"打光|造梦|扩音器|想象力"),
    "aesthetic": re.compile(r"美即是正义|品味|Pixel Perfect|人味"),
}
GENERIC_AI = re.compile(r"什么是\s*AI|人工智能是|随着科技的发展|赋能|抓手|闭环")


def check(text: str, genre: str | None) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    def add(level: str, name: str, detail: str) -> None:
        rows.append((level, name, detail))

    if HONEST.search(text):
        add("PASS", "诚实/祛魅气口", "找到诚实转折或吐槽落地")
    else:
        add("FAIL", "诚实/祛魅气口", "缺少「说实话 / 但是老实说 / 滤镜碎了」类段落")

    if DEFINITION.search(text):
        add("PASS", "大白话定义", "有降维定义或重新命名")
    else:
        add("WARN" if genre == "product" else "FAIL", "大白话定义", "建议加「一句话，什么叫 X」或产品隐喻定位")

    if CONTRAST.search(text):
        add("PASS", "对比教学", "有糟糕vs好 / 不是而是 等对比")
    else:
        add("WARN", "对比教学", "可补一组对比，降低说教感")

    if ACTIONABLE.search(text):
        add("PASS", "可执行收束", "有清单/步骤/防坑痕迹")
    else:
        add("FAIL", "可执行收束", "读者合上页不知道下一步——补清单或 Q&A")

    hit = [k for k, rx in METAPHOR_BUCKETS.items() if rx.search(text)]
    if len(hit) == 1:
        add("PASS", "隐喻一致性", f"主要使用 {hit[0]} 系统")
    elif len(hit) == 0:
        add("WARN", "隐喻一致性", "未检测到常用隐喻桶，确认是否故意不用")
    else:
        add("WARN", "隐喻一致性", f"多套隐喻同时出现：{', '.join(hit)}——尽量贯穿一套")

    if GENERIC_AI.search(text):
        add("FAIL", "禁区腔", "出现空泛 AI 科普腔，删掉或改成具体场景")
    else:
        add("PASS", "禁区腔", "未见典型空泛开场")

    # rough gold-sentence density: lines with bold short slogans
    bold = re.findall(r"\*\*([^*]{8,40})\*\*", text)
    if len(bold) > 12:
        add("WARN", "金句密度", f"加粗短句偏多（{len(bold)}），考虑收到 2–4 句真金句")
    else:
        add("PASS", "金句密度", f"加粗短句约 {len(bold)}，可接受")

    if genre == "product" and not re.search(r"打光|不是.{0,8}替代|愿", text):
        add("WARN", "产品文定位", "产品文建议出现「不是替代而是…」或愿景收束")

    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("draft", type=Path)
    ap.add_argument("--genre", choices=["review", "tutorial", "product", "trend"])
    args = ap.parse_args()
    text = args.draft.read_text(encoding="utf-8")
    rows = check(text, args.genre)
    width = max(len(r[1]) for r in rows)
    fails = sum(1 for r in rows if r[0] == "FAIL")
    warns = sum(1 for r in rows if r[0] == "WARN")
    for level, name, detail in rows:
        print(f"[{level:4}] {name.ljust(width)}  {detail}")
    print(f"\nsummary: {fails} FAIL, {warns} WARN")
    if fails:
        print("fix FAIL items before delivering to Dawn")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

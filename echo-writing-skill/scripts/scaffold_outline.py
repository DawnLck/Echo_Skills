#!/usr/bin/env python3
"""Scaffold a 无限回响 article outline by genre.

Usage:
  python scaffold_outline.py --genre review|tutorial|product|trend --topic "主题"
  python scaffold_outline.py --genre review --topic "xxx" --filter albert|ysfj|none
"""
from __future__ import annotations

import argparse
import json
import sys

GENRES = {
    "review": {
        "name": "评测 / 生存报告",
        "beats": [
            "延迟热度或扔草稿的诚实动机",
            "大白话重新命名产品（隐喻）",
            "草台班子配置 / 怎么用的",
            "崩溃时刻 ↔ 真香时刻（对仗）",
            "心法或 Rules（带一点审美）",
            "隐藏彩蛋 / 野路子 2–3 条",
            "但是老实说：缺点",
            "写在最后：金句升华",
            "防坑 Q&A 或选型对照",
        ],
    },
    "tutorial": {
        "name": "教程 / 指南",
        "beats": [
            "题旨：本质是什么（降维比喻）",
            "糟糕 vs 好 的对比示例",
            "一句话定义核心概念",
            "立刻上手技巧列表（编号）",
            "关键步骤穿插「我的看法」",
            "但是老实说：局限",
            "可执行清单或模板",
            "收束：感受到美 / 下一步行动",
        ],
    },
    "product": {
        "name": "产品 / 种草文",
        "beats": [
            "共情场景（童年或日常）",
            "痛点：想象力/效率被磨平",
            "产品一句话定位（不是替代，而是…）",
            "一个具象生成/使用瞬间",
            "怎么用（低门槛，少参数）",
            "轻 CTA + 愿景短收束",
        ],
    },
    "trend": {
        "name": "趋势 / 方法论",
        "beats": [
            "开场：这件事跟你有什么关系",
            "一句话定义",
            "2–3 个已经发生的真人案例",
            "背后原理（用日常类比，如搜索分层）",
            "从零到一可跟做步骤",
            "但是老实说：平台坑",
            "拉开视角：经验经济 / 民主化",
            "五条可开干的启发",
            "写在最后：乌托邦已有人住",
        ],
    },
}

FILTERS = {
    "none": "仅无限回响底色",
    "albert": "叠小王Albert：加悖论钩子 + 数据→历史→生活场景证据链",
    "ysfj": "叠影视飓风：加人+地点开场 + 现场细节/笑点位（旁白少而精）",
}


def main() -> int:
    ap = argparse.ArgumentParser(description="Scaffold 无限回响 article outline")
    ap.add_argument("--genre", required=True, choices=sorted(GENRES))
    ap.add_argument("--topic", required=True)
    ap.add_argument("--filter", default="none", choices=sorted(FILTERS), dest="voice_filter")
    ap.add_argument("--json", action="store_true", help="print JSON")
    args = ap.parse_args()

    g = GENRES[args.genre]
    payload = {
        "topic": args.topic,
        "genre": args.genre,
        "genre_name": g["name"],
        "voice_filter": args.voice_filter,
        "voice_filter_note": FILTERS[args.voice_filter],
        "outline": [{"n": i + 1, "beat": b} for i, b in enumerate(g["beats"])],
        "reminders": [
            "保留第一人称「我」与诚实缺点段",
            "全文金句 2–4 句；一套隐喻贯穿",
            "写完跑 style_check.py",
        ],
    }
    if args.json:
        json.dump(payload, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0

    print(f"# 《{args.topic}》大纲 · {g['name']}")
    print(f"滤镜：{FILTERS[args.voice_filter]}\n")
    for item in payload["outline"]:
        print(f"{item['n']}. {item['beat']}")
    print("\n写稿提醒：")
    for r in payload["reminders"]:
        print(f"- {r}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

---
name: echo-writing-skill
description: Use when Dawn asks to write, rewrite, outline, or polish a Chinese article, 公众号 post, product essay, AI/tool review, tutorial, or trend piece in her personal「无限回响」voice; also when she wants Albert- or 影视飓风-flavored structure on top of that voice.
---

# echo-writing-skill（无限回响写作）

## Overview

用 Dawn 的个人文风写中文长文/公众号：**祛魅后的真诚技术叙事**。可选用外部 UP 的结构滤镜，但人设与隐喻以「无限回响」为准。

## Workflow

1. **定体裁**：`review` | `tutorial` | `product` | `trend`（不确定就问一句，或根据选题自判）。
2. **定滤镜**：默认 `none`。仅当用户点名或题材明显匹配时用 `albert`（国别/产业深潜）或 `ysfj`（花絮/幕后）。
3. **搭大纲**：在本 skill 目录执行  
   `python scripts/scaffold_outline.py --genre <体裁> --topic "<主题>" --filter <none|albert|ysfj>`
4. **校准语气**：先读 `references/voice.md`；需要滤镜时读 `references/up-voice-filters.md`；卡壳时翻 `references/samples/`（只学味道，禁止整段复用）。
5. **起草**：第一人称「我」；中段必须有诚实缺点；结尾可执行。
6. **自检**：`python scripts/style_check.py <草稿路径> --genre <体裁>` —— 先改完所有 `FAIL`，再交付。
7. **交付**：正文给用户；需要时附大纲。默认不发外链平台，除非用户明确要求发布。

## Voice contract（必须）

| 要有 | 不要有 |
|------|--------|
| 大白话定义或产品隐喻定位 | 说明书式开场 / 「随着科技的发展」 |
| 「说实话 / 但是老实说」类祛魅 | 纯参数堆砌、无亲历黑话 |
| 至少一组对比（糟糕vs好 / 不是而是） | 多套隐喻混用 |
| 可执行清单、野路子或防坑 Q&A | 连续鸡汤无案例 |
| 全文真金句约 2–4 句 | 把读者当小白反复解释「什么是 AI」 |

完整细则与两位 UP 画像：`references/style-notes-full.md`。

## Common mistakes

- 只学 Albert 的信息密度，丢掉 Dawn 的诚实与生活隐喻 → 读起来像另一个人。
- 产品文写成功能列表 → 先共情与「不是替代而是…」，参数放后或省略。
- 样例整段粘贴 → samples 仅供校准。
- 跳过 `style_check.py` → 容易缺「可执行收束」。

## File map

- `references/voice.md` — 个人文风速查
- `references/up-voice-filters.md` — 可选 Albert / 影视飓风滤镜
- `references/style-notes-full.md` — 完整研究报告
- `references/samples/` — 开场/定义/产品/对比摘录
- `scripts/scaffold_outline.py` — 大纲脚手架
- `scripts/style_check.py` — 草稿启发式检查

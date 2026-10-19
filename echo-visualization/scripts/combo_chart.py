#!/usr/bin/env python3
"""
分析型组合图 · matplotlib 版（离线、直接出 PNG 文件）
何时用：用户要的是「一张图片文件」（发群、贴文档、放 PPT），或环境里没有浏览器 / 连不上 CDN。
        要在对话里内嵌展示时，优先用 renders/08-combo-dual-axis.html。
画什么：左轴一条主线（平滑 + 点标注）、右轴正负条件色柱、零线 + 横向参考线、
        若干竖向虚线参考线（旋转标签）、图例、左下角脚注。

用法：
  python3 combo_chart.py spec.json out.png           # 按 JSON 规格画
  python3 combo_chart.py --demo out.png              # 用内置示例数据画（示例数据，非真实测算）
spec.json 字段见下方 DEMO，缺省项会用 DEMO 里的默认值。

三个最容易翻车的点，脚本已处理：
  1. 中文字体：matplotlib 默认 DejaVu 不含中文 → 方块「□□」。这里按候选列表挑一个系统里真实存在的 CJK 字体，
     一个都没有就报错退出，而不是悄悄画出一张豆腐块图。
  2. 负号：CJK 字体常缺 U+2212，需 axes.unicode_minus=False，否则负刻度显示成方块。
  3. 双轴零点对齐：右轴范围按左轴参考值反算（左 ref ↔ 右 0），柱子的 0 线和 50% 线才会重合/贴近。
"""
import json, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")                                   # 无显示器环境
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm

DEMO = {
    "title": "上证不同买入点位的3个月盈亏概率（主观情景模型：主计数62% / 备选28% / 横盘10%）",
    "x_label": "上证买入点位",
    "y_left_label": "获利概率 (%)",
    "y_right_label": "预期收益率 (%)",
    "x": list(range(3550, 3951, 10)),
    "line": {"name": "3个月内获利概率", "color": "#D62728",
             "values": [75.0,74.5,74.0,73.5,72.9,72.3,71.6,70.9,70.1,69.3,68.4,67.5,66.5,65.5,64.4,63.2,
                        61.9,60.5,58.9,57.2,55.4,53.5,51.6,49.7,47.8,46.0,44.2,42.3,40.5,38.6,36.7,34.8,
                        32.9,31.0,29.1,27.2,25.3,23.5,21.7,19.8,18.0],
             "label_at": [3600, 3700, 3800, 3900], "smooth": True},
    "bars": {"name": "预期收益率", "pos_color": "#B3DDB3", "neg_color": "#D0D0D0",
             "values": [5.20,4.91,4.61,4.31,4.02,3.72,3.42,3.13,2.85,2.57,2.30,2.04,1.79,1.55,
                        1.31,1.07,0.83,0.59,0.35,0.10,-0.16,-0.41,-0.68,-0.94,-1.21,-1.47,-1.74,-2.01,
                        -2.27,-2.54,-2.80,-3.06,-3.32,-3.58,-3.84,-4.10,-4.36,-4.62,-4.88,-5.14,-5.40]},
    "y_left_range": [0, 100],
    "h_ref_left": 50,                 # 左轴横向参考线（点线）；null 不画
    "align_right_zero_to_left": 51,   # 右轴 0 对齐到左轴哪个值；null = 右轴自动范围
    "v_refs": [
        {"x": 3674, "text": "生死线3674", "color": "black"},
        {"x": 3700, "text": "当前约3700", "color": "#1F77B4"},
        {"x": 3820, "text": "转强3820", "color": "#FF7F0E"},
        {"x": 3934, "text": "平均成本3934", "color": "#9467BD"},
    ],
    "legend_loc": "lower left",
    "footnote": "注：基于我们的波浪判断设定的主观假设，非统计预测；仅供学习研究。（示例数据）",
    "size": [10.24, 5.76], "dpi": 100,
    "font": "serif",                  # serif（宋体系）或 sans（黑体系）
}

CJK = {
    "serif": ["Noto Serif CJK SC", "Source Han Serif SC", "Songti SC", "STSong", "SimSun", "Noto Serif SC"],
    "sans":  ["Noto Sans CJK SC", "Source Han Sans SC", "PingFang SC", "Hiragino Sans GB",
              "Microsoft YaHei", "WenQuanYi Micro Hei", "Noto Sans SC", "SimHei"],
}

def pick_font(kind):
    have = {f.name for f in fm.fontManager.ttflist}
    for name in CJK.get(kind, []) + CJK["serif"] + CJK["sans"]:
        if name in have:
            return name
    sys.exit("找不到中文字体：请安装 Noto CJK（apt install fonts-noto-cjk / brew install font-noto-serif-cjk-sc），"
             "或把系统中文字体名加进 CJK 列表。")

def smooth(x, y, n=400):
    """单调三次 Hermite 插值（Fritsch–Carlson，等价 scipy 的 PCHIP）：
    曲线平滑但不过冲，不会画出原数据里没有的起伏。纯 numpy，不依赖 scipy。"""
    x, y = np.asarray(x, float), np.asarray(y, float)
    if len(x) < 3:
        return x, y
    h, d = np.diff(x), np.diff(y) / np.diff(x)
    m = np.zeros_like(y)
    for k in range(1, len(x) - 1):
        if d[k - 1] * d[k] > 0:
            w1, w2 = 2 * h[k] + h[k - 1], h[k] + 2 * h[k - 1]
            m[k] = (w1 + w2) / (w1 / d[k - 1] + w2 / d[k])
    m[0], m[-1] = d[0], d[-1]
    xs = np.linspace(x[0], x[-1], n)
    i = np.clip(np.searchsorted(x, xs) - 1, 0, len(x) - 2)
    t = (xs - x[i]) / h[i]
    h00, h10, h01, h11 = 2*t**3 - 3*t**2 + 1, t**3 - 2*t**2 + t, -2*t**3 + 3*t**2, t**3 - t**2
    return xs, h00 * y[i] + h10 * h[i] * m[i] + h01 * y[i + 1] + h11 * h[i] * m[i + 1]

def draw(spec, out):
    s = {**DEMO, **spec}
    font = pick_font(s["font"])
    plt.rcParams.update({"font.family": font, "axes.unicode_minus": False})

    x = np.asarray(s["x"], float)
    ln, br = {**DEMO["line"], **s["line"]}, {**DEMO["bars"], **s["bars"]}
    yv, bv = np.asarray(ln["values"], float), np.asarray(br["values"], float)
    assert len(x) == len(yv) == len(bv), "x / line / bars 长度必须一致"

    fig, ax = plt.subplots(figsize=s["size"], dpi=s["dpi"])
    ax2 = ax.twinx()
    ax.set_zorder(ax2.get_zorder() + 1); ax.patch.set_visible(False)   # 主线画在柱子上面

    # —— 右轴：正负条件色柱 + 零线 ——
    step = np.min(np.diff(x)) if len(x) > 1 else 1
    colors = [br["pos_color"] if v >= 0 else br["neg_color"] for v in bv]
    ax2.bar(x, bv, width=step * 0.7, color=colors, label=br["name"], zorder=1)
    ax2.axhline(0, color="#555", lw=0.9, zorder=2)
    ax2.set_ylabel(s["y_right_label"])

    # —— 左轴：主线 + 点标注 + 横向参考线 ——
    xs, ys = smooth(x, yv) if ln.get("smooth", True) else (x, yv)
    ax.plot(xs, ys, color=ln["color"], lw=3, label=ln["name"], solid_capstyle="round", zorder=5)
    for xv in ln.get("label_at", []):
        i = int(np.argmin(np.abs(x - xv)))
        ax.annotate(f"{yv[i]:.0f}%", (x[i], yv[i]), xytext=(0, 6), textcoords="offset points",
                    ha="center", va="bottom", color=ln["color"], fontsize=11, zorder=6)
    lo, hi = s["y_left_range"]; ax.set_ylim(lo, hi)
    if s.get("h_ref_left") is not None:
        ax.axhline(s["h_ref_left"], color="#555", lw=1, ls=":", zorder=2)
    ax.set_ylabel(s["y_left_label"]); ax.set_xlabel(s["x_label"])

    # 右轴范围：让右 0 落在左轴 ref 处（双轴对齐的关键一步）
    ref = s.get("align_right_zero_to_left")
    if ref is not None:
        f = (ref - lo) / (hi - lo)                       # 0 在右轴上的相对高度
        span = max(max(bv.max(), 0) * 1.08 / (1 - f),    # 上下都装得下的最小总跨度
                   max(-bv.min(), 0) * 1.08 / f, 1e-9)
        ax2.set_ylim(-f * span, (1 - f) * span)

    # —— 竖向参考线 + 旋转标签（贴顶、在线右侧）——
    for r in s.get("v_refs", []):
        ax.axvline(r["x"], color=r["color"], lw=1.2, ls="--", zorder=3)
        ax.text(r["x"] + step * 0.25, hi - (hi - lo) * 0.02, r["text"], color=r["color"],
                rotation=90, ha="left", va="top", fontsize=9.5, zorder=6)

    # —— 图例合并两根轴 ——
    h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
    ax.legend(h1 + h2, l1 + l2, loc=s["legend_loc"], framealpha=0.9)

    ax.set_title(s["title"], fontsize=12)
    ax.set_xlim(x.min() - step * 2.5, x.max() + step * 2.5)
    fig.tight_layout(rect=(0, 0.03, 1, 1))
    if s.get("footnote"):
        fig.text(0.01, 0.008, s["footnote"], fontsize=8, color="#666", ha="left", va="bottom")
    fig.savefig(out, dpi=s["dpi"] * 2 if s.get("retina", True) else s["dpi"])
    print("saved", out, "font =", font)

if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--demo":
        draw({}, sys.argv[2])
    elif len(sys.argv) == 3:
        draw(json.load(open(sys.argv[1], encoding="utf-8")), sys.argv[2])
    else:
        sys.exit(__doc__)

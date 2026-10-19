#!/usr/bin/env bash
# 把任意一个 render（HTML）导出成 PNG —— 用户要「图片文件」而不是对话内嵌时用。
# 用法：bash export-png.sh <input.html> <output.png> [宽=1024] [高=680] [light|dark]
# 依赖：本机任一 Chrome / Chromium / Edge（无需 node / playwright）。
# 说明：
#   · --virtual-time-budget 让页面先跑完脚本、加载完 CDN 再截图；模板已关动画，所以不会截到空图。
#   · 高度按内容估一个值；截出来底部留白多就调小，被裁就调大。
#   · 要离线出图（无网 / CDN 被墙）请改用 scripts/combo_chart.py（matplotlib）。
set -euo pipefail
IN="$1"; OUT="$2"; W="${3:-1024}"; H="${4:-680}"; SCHEME="${5:-light}"
for c in "${CHROME:-}" google-chrome google-chrome-stable chromium chromium-browser microsoft-edge \
         "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
         "/Applications/Chromium.app/Contents/MacOS/Chromium" \
         "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge"; do
  [ -n "$c" ] && { command -v "$c" >/dev/null 2>&1 || [ -x "$c" ]; } && BIN="$c" && break
done
[ -n "${BIN:-}" ] || { echo "找不到 Chrome/Chromium，可设置 CHROME=/path/to/chrome" >&2; exit 1; }
ABS="$(cd "$(dirname "$IN")" && pwd)/$(basename "$IN")"
"$BIN" --headless=new --no-sandbox --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=2 --window-size="$W,$H" --virtual-time-budget=10000 \
  $([ "$SCHEME" = dark ] && echo --force-dark-mode --blink-settings=preferredColorScheme=0) \
  --screenshot="$OUT" "file://$ABS" 2>/dev/null
echo "saved $OUT (${W}x${H} @2x, $SCHEME)"

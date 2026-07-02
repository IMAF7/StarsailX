# -*- coding: utf-8 -*-
"""安全清理 StarsailX 残留引用（不用危险正则）。"""
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "StarsailX.py"
text = p.read_text(encoding="utf-8")
repls = [
    (
        "_ICON_OK: Optional[QIcon] = None\n_ICON_FAIL: Optional[QIcon] = None\n_ICON_SLEEP: Optional[QIcon] = None\n\n",
        "",
    ),
    (
        '''def _make_dot_icon(color: str, size: int = 14) -> QIcon:
    pix = QPixmap(size, size)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(color))
    p.setPen(Qt.PenStyle.NoPen)
    margin = max(1, size // 7)
    p.drawEllipse(margin, margin, size - 2 * margin, size - 2 * margin)
    p.end()
    return QIcon(pix)


''',
        "",
    ),
    (
        '''def account_status_icon(display_status: str) -> QIcon:
    global _ICON_OK, _ICON_FAIL, _ICON_SLEEP
    if _ICON_OK is None:
        _ICON_OK = _make_dot_icon("#22c55e", 16)
        _ICON_SLEEP = _make_dot_icon("#f5b82e", 16)
        _ICON_FAIL = _make_dot_icon("#ff5252", 16)
    if display_status == DISPLAY_ACTIVE:
        return _ICON_OK
    if display_status == DISPLAY_SLEEP:
        return _ICON_SLEEP
    return _ICON_FAIL


''',
        "",
    ),
    (
        "        if hasattr(self, \"mem_status_label\"):\n"
        "            self._mem_hint_color = \"\"\n"
        "            self._refresh_memory_hint()\n",
        "",
    ),
    (
        "            if hasattr(self, \"ai_chat_panel\") and self.ai_chat_panel:\n"
        "                self.ai_chat_panel.setUpdatesEnabled(True)\n",
        "",
    ),
    (
        "            if hasattr(self, \"ai_chat_panel\") and self.stack_widget.currentIndex() == 0:\n"
        "                self.ai_chat_panel.repaint()\n",
        "",
    ),
    (
        "        QTimer.singleShot(50, self._focus_ai_input_if_home)\n",
        "",
    ),
    (
        "        self._sync_ai_panel_layout()\n",
        "",
    ),
    (
        "        self._sync_lock_overlay_geometry()\n",
        "",
    ),
    (
        "        self._style_lock_overlay()\n",
        "",
    ),
    (
        "        self._ensure_lock_overlay_widgets()\n"
        "        if self._lock_overlay is not None:\n"
        "            self._lock_overlay.hide()\n\n",
        "",
    ),
    (
        "        if self.stack_widget.currentIndex() == 0:\n            return False\n",
        "        if self.stack_widget.currentWidget() is getattr(self, \"_empty_page\", None):\n            return False\n",
    ),
]
for old, new in repls:
    if old in text:
        text = text.replace(old, new)

# remove methods by markers
def drop_method(src: str, name: str) -> str:
    key = f"    def {name}("
    if key not in src:
        return src
    start = src.find(key)
    rest = src[start + len(key):]
    nxt = rest.find("\n    def ")
    if nxt < 0:
        return src[:start]
    return src[:start] + src[start + len(key) + nxt + 1:]

for m in ("_focus_ai_input_if_home", "_sync_ai_panel_layout"):
    text = drop_method(text, m)

# drop _refresh_account_dot calls
lines = []
for line in text.splitlines(keepends=True):
    if "self._refresh_account_dot(" in line:
        continue
    if "lambda a=aid: self._refresh_account_dot(a)" in line:
        continue
    lines.append(line)
text = "".join(lines)

p.write_text(text, encoding="utf-8")
print("safe cleanup done")

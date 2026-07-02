# -*- coding: utf-8 -*-
from pathlib import Path

p = Path(__file__).resolve().parents[1] / "StarsailX.py"
lines = p.read_text(encoding="utf-8").splitlines(keepends=True)
out = []
i = 0
while i < len(lines):
    line = lines[i]
    stripped = line.rstrip("\n")

    if line.startswith("def _make_dot_icon("):
        while i < len(lines) and not lines[i].startswith("def _bridge_connect_js_source"):
            i += 1
        continue
    if line.startswith("def account_status_icon("):
        while i < len(lines) and not lines[i].startswith("def _bridge_connect_js_source"):
            i += 1
        continue
    if line.startswith("    def _focus_ai_input_if_home("):
        i += 1
        while i < len(lines) and not (
            lines[i].startswith("    def ") and not lines[i].startswith("    def _focus")
        ):
            i += 1
        continue
    if line.startswith("    def _sync_ai_panel_layout("):
        i += 1
        while i < len(lines) and not lines[i].startswith("    def "):
            i += 1
        continue

    drops = {
        '            if hasattr(self, "ai_chat_panel") and self.ai_chat_panel:',
        '                self.ai_chat_panel.setUpdatesEnabled(True)',
        '            if hasattr(self, "ai_chat_panel") and self.stack_widget.currentIndex() == 0:',
        '                self.ai_chat_panel.repaint()',
        '        QTimer.singleShot(50, self._focus_ai_input_if_home)',
        '        self._sync_ai_panel_layout()',
    }
    if stripped in drops:
        i += 1
        continue
    if "self._refresh_account_dot(" in line:
        i += 1
        continue
    if "lambda a=aid: self._refresh_account_dot(a)" in line:
        i += 1
        continue
    if 'if hasattr(self, "mem_status_label")' in line:
        i += 1
        while i < len(lines) and lines[i].startswith("            "):
            i += 1
        continue

    out.append(line)
    i += 1

text = "".join(out)
text = text.replace("_ICON_OK: Optional[QIcon] = None\n_ICON_FAIL: Optional[QIcon] = None\n_ICON_SLEEP: Optional[QIcon] = None\n\n", "")
text = text.replace(
    "        if self.stack_widget.currentIndex() == 0:\n            return False\n",
    "        if self.stack_widget.currentWidget() is getattr(self, \"_empty_page\", None):\n            return False\n",
)
p.write_text(text, encoding="utf-8")
print("cleanup ok", len(lines), "->", len(out))

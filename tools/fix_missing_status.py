"""Add missing update_status and fix _get_webview typo."""
from pathlib import Path

path = Path(r"c:\Users\admin\Desktop\StarsailX\StarsailX.py")
text = path.read_text(encoding="utf-8")

if "def update_status(self, text: str):" not in text:
    marker = "    def _has_active_call(self) -> bool:"
    insert = """    def update_status(self, text: str):
        \"\"\"更新状态标签（同文本不重绘，避免无谓刷新）\"\"\"
        try:
            if self.status_label.text() == text:
                return
        except Exception:
            pass
        self.status_label.setText(text)

"""
    if marker not in text:
        raise SystemExit("_has_active_call marker not found")
    text = text.replace(marker, insert + marker, 1)
    print("added update_status")

text = text.replace(
    "self._get_webview(self.current_account_id)",
    "self._get_webview_for_account(self.current_account_id)",
)
path.write_text(text, encoding="utf-8")
print("patched", path)

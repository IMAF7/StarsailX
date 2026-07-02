# -*- coding: utf-8 -*-
"""StarsailX 精简补丁（第二轮）：清理残留引用。"""
from pathlib import Path
import re

TARGET = Path(__file__).resolve().parents[1] / "StarsailX.py"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")

    # remove dot icon helpers
    text = re.sub(
        r"_ICON_OK: Optional\[QIcon\] = None\n"
        r"_ICON_FAIL: Optional\[QIcon\] = None\n"
        r"_ICON_SLEEP: Optional\[QIcon\] = None\n\n",
        "",
        text,
        count=1,
    )
    text = re.sub(
        r"def _make_dot_icon\(color: str, size: int = 14\) -> QIcon:.*?return QIcon\(pix\)\n\n\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"def account_status_icon\(display_status: str\) -> QIcon:.*?return _ICON_FAIL\n\n\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )

    # remove ai panel helper methods
    text = re.sub(
        r"    def _focus_ai_input_if_home\(self\):.*?return\n\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"    def _sync_ai_panel_layout\(self\) -> None:.*?panel\.updateGeometry\(\)\n\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )

    # remove ai branches in repaint helpers
    text = text.replace(
        "            if hasattr(self, \"ai_chat_panel\") and self.ai_chat_panel:\n"
        "                self.ai_chat_panel.setUpdatesEnabled(True)\n",
        "",
    )
    text = text.replace(
        "            if hasattr(self, \"ai_chat_panel\") and self.stack_widget.currentIndex() == 0:\n"
        "                self.ai_chat_panel.repaint()\n",
        "",
    )
    text = text.replace("        QTimer.singleShot(50, self._focus_ai_input_if_home)\n", "")
    text = text.replace("        self._sync_ai_panel_layout()\n", "")

    # remove account dot refresh calls
    text = re.sub(r"\s*self\._refresh_account_dot\([^\)]+\)\n", "\n", text)
    text = re.sub(
        r"\s*QTimer\.singleShot\(0, lambda a=aid: self\._refresh_account_dot\(a\)\)\n",
        "\n",
        text,
    )

    # remove mem label references
    text = re.sub(
        r"\s*if hasattr\(self, \"mem_status_label\"\):.*?\n(?:\s+.*\n)*?(?=\n    def |\n        [a-z_])",
        "\n",
        text,
        flags=re.DOTALL,
    )

    # simplify _is_account_foreground if still references index 0 as AI
    text = text.replace(
        "        if self.stack_widget.currentIndex() == 0:\n            return False\n",
        "        if self.stack_widget.currentWidget() is getattr(self, \"_empty_page\", None):\n            return False\n",
    )

    # remove lock overlay init block if present
    text = re.sub(
        r"\s*# 标题栏以下区域：锁定遮罩只盖住这里.*?\n\s*self\._lock_overlay.*?\n(?:\s+.*\n)*?(?=        self\._sidebar_expand_strip)",
        "\n",
        text,
        flags=re.DOTALL,
    )

    # remove AccountGroupPickerDialog if orphaned
    if "class AccountGroupPickerDialog" in text:
        text = re.sub(
            r"class AccountGroupPickerDialog\(QDialog\):.*?(?=\nclass |\n# =)",
            "",
            text,
            count=1,
            flags=re.DOTALL,
        )

    TARGET.write_text(text, encoding="utf-8")
    print("cleanup2 done")


if __name__ == "__main__":
    main()

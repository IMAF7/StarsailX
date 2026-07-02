# -*- coding: utf-8 -*-
"""完整重建精简版 StarsailX。"""
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


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


def main() -> None:
    shutil.copy2(ROOT / "TeamsX.py", ROOT / "StarsailX.py")
    for script in ("patch_starsailx.py", "apply_starsail_extras.py", "slim_starsailx.py"):
        r = subprocess.run([sys.executable, str(ROOT / "tools" / script)], cwd=ROOT)
        if r.returncode != 0 and script == "patch_starsailx.py":
            pass  # config.py already patched

    p = ROOT / "StarsailX.py"
    text = p.read_text(encoding="utf-8")

    repls = [
        (
            "        # AI 主界面：只刷新左侧账号列表\n"
            "        if hasattr(self, \"stack_widget\") and self.stack_widget.currentIndex() == 0:\n",
            "        if hasattr(self, \"stack_widget\") and self.stack_widget.currentWidget() is getattr(self, \"_empty_page\", None):\n",
        ),
        (
            "        self._refresh_memory_hint()\n        self._refresh_default_status()",
            "        self._refresh_default_status()",
        ),
        (
            "            self._refresh_memory_hint()\n            self._refresh_default_status()",
            "            self._refresh_default_status()",
        ),
    ]
    for old, new in repls:
        text = text.replace(old, new)

    for m in ("_focus_ai_input_if_home", "_sync_ai_panel_layout"):
        text = drop_method(text, m)

    mem_blocks = [
        """        if hasattr(self, "mem_status_label"):
            self._mem_hint_color = ""
            self._refresh_memory_hint()
""",
        """            if hasattr(self, "mem_status_label"):
                self.mem_status_label.show()
""",
        """            if hasattr(self, "mem_status_label"):
                self.mem_status_label.hide()
""",
    ]
    for block in mem_blocks:
        text = text.replace(block, "")

    lines = []
    for line in text.splitlines(keepends=True):
        if any(
            x in line
            for x in (
                "self._refresh_account_dot(",
                "lambda a=aid: self._refresh_account_dot(a)",
                'if hasattr(self, "ai_chat_panel")',
                "self.ai_chat_panel.",
                "self._sync_ai_panel_layout()",
                "self._focus_ai_input_if_home",
                "self._sync_lock_overlay_geometry()",
                "self._style_lock_overlay()",
                "self._ensure_lock_overlay_widgets()",
            )
        ):
            continue
        lines.append(line)
    text = "".join(lines)

    if text.count("class MainWindow") != 1:
        raise SystemExit(f"unexpected MainWindow count: {text.count('class MainWindow')}")

    p.write_text(text, encoding="utf-8")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "fix_comprehensive.py")], cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit("fix_comprehensive failed")
    r = subprocess.run([sys.executable, str(ROOT / "tools" / "patch_esc_back.py")], cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit("patch_esc_back failed")
    r = subprocess.run([sys.executable, "-m", "py_compile", str(p)], cwd=ROOT)
    if r.returncode != 0:
        raise SystemExit("compile failed")
    print("rebuild ok", len(lines), "lines")


if __name__ == "__main__":
    main()

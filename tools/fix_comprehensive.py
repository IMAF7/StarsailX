# -*- coding: utf-8 -*-
"""一次性修复 StarsailX 已知运行时问题。"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "StarsailX.py"
SITE = ROOT / "teamsx" / "site_config.py"


def patch_site_config() -> None:
    text = SITE.read_text(encoding="utf-8")
    block = """
STARSAIL_LOGIN_FAIL_REASONS = frozenset({
    "login_form", "loading", "no_shell", "not_starsail", "error",
})
"""
    if "STARSAIL_LOGIN_FAIL_REASONS" not in text:
        anchor = "ENABLE_CALL_FEATURES = False\n"
        if anchor not in text:
            raise SystemExit("site_config anchor missing")
        text = text.replace(anchor, anchor + block + "\n", 1)
        SITE.write_text(text, encoding="utf-8")
        print("patched site_config.py")


def patch_starsailx() -> None:
    text = TARGET.read_text(encoding="utf-8")

    if "STARSAIL_LOGIN_FAIL_REASONS" not in text:
        old = "    STARSAIL_NOTIFY_JS,\n)"
        new = "    STARSAIL_NOTIFY_JS,\n    STARSAIL_ESC_CHAT_JS,\n    STARSAIL_LOGIN_FAIL_REASONS,\n)"
        if old not in text:
            raise SystemExit("import block missing STARSAIL_NOTIFY_JS")
        text = text.replace(old, new, 1)

    text = text.replace("_TEAMS_SHELL_VERIFY_JS", "STARSAIL_SHELL_VERIFY_JS")
    text = text.replace("_TEAMS_LOGIN_FAIL_REASONS", "STARSAIL_LOGIN_FAIL_REASONS")

    notify_needle = "        self._wv2_doc_scripts.append(js_code)\n        return\n\n# ==================== 主窗口类 ===================="
    notify_repl = (
        "        self._wv2_doc_scripts.append(js_code)\n"
        "        self._wv2_doc_scripts.append(STARSAIL_NOTIFY_JS)\n"
        "        self._wv2_doc_scripts.append(STARSAIL_ESC_CHAT_JS)\n"
        "        return\n\n# ==================== 主窗口类 ===================="
    )
    if "self._wv2_doc_scripts.append(STARSAIL_ESC_CHAT_JS)" not in text:
        if notify_needle not in text:
            raise SystemExit("inject_persistent_scripts tail not found")
        text = text.replace(notify_needle, notify_repl, 1)

    empty_old = (
        '        self._empty_page = QWidget()\n'
        '        self._empty_page.setObjectName("emptyChatPage")\n'
        '        self._empty_page.setStyleSheet("background-color: #1a1a1a;")\n'
        '        self.stack_widget.addWidget(self._empty_page)\n'
    )
    empty_new = (
        '        self._empty_page = QWidget()\n'
        '        self._empty_page.setObjectName("emptyChatPage")\n'
        '        self.stack_widget.addWidget(self._empty_page)\n'
        '        self._sync_empty_page_theme()\n'
    )
    if empty_old in text:
        text = text.replace(empty_old, empty_new, 1)

    if "def _sync_empty_page_theme(self)" not in text:
        anchor = "    def apply_theme(self, light: bool):"
        if anchor not in text:
            raise SystemExit("apply_theme not found")
        method = """
    def _sync_empty_page_theme(self) -> None:
        \"\"\"空白聊天页背景跟随浅/深主题。\"\"\"
        page = getattr(self, "_empty_page", None)
        if page is None:
            return
        bg = "#f3f3f3" if getattr(self, "_theme_light", True) else "#1e1e1e"
        page.setStyleSheet(f"QWidget#emptyChatPage {{ background-color: {bg}; }}")

"""
        text = text.replace(anchor, method + anchor, 1)

    apply_anchor = "        self._sync_window_chrome()\n"
    apply_insert = "        self._sync_window_chrome()\n        self._sync_empty_page_theme()\n"
    if apply_insert not in text and apply_anchor in text:
        text = text.replace(apply_anchor, apply_insert, 1)

    TARGET.write_text(text, encoding="utf-8")
    print("patched StarsailX.py")


def main() -> None:
    patch_site_config()
    patch_starsailx()
    import py_compile

    py_compile.compile(str(TARGET), doraise=True)
    print("compile ok")


if __name__ == "__main__":
    main()

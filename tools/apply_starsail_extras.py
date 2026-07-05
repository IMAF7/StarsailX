# -*- coding: utf-8 -*-
"""应用 Starsail 专属补丁（在 patch_starsailx 之后、slim 之前）。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "StarsailX.py"


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")

    old_import = """from starsailx.site_config import (
    STARSAIL_APP_URL,
    STARSAIL_SHELL_VERIFY_JS,
    STARSAIL_LOGIN_JS_TEMPLATE,
    ENABLE_CALL_FEATURES,
    LOGIN_WINDOW_WIDTH,
    LOGIN_WINDOW_HEIGHT,
    CHAT_WINDOW_WIDTH,
    CHAT_WINDOW_HEIGHT,
)"""

    new_import = old_import.replace(
        ")",
        "    STARSAIL_SHELL_CSS_JS,\n    STARSAIL_NOTIFY_JS,\n    STARSAIL_ESC_CHAT_JS,\n)",
    )
    if "STARSAIL_SHELL_CSS_JS" not in text:
        if old_import not in text:
            raise SystemExit("site_config import block not found")
        text = text.replace(old_import, new_import, 1)

    if "STARSAIL_SHELL_CSS_JS" not in text:
        old_import2 = """from starsailx.site_config import (
    STARSAIL_APP_URL,
    STARSAIL_SHELL_VERIFY_JS,
    STARSAIL_LOGIN_JS_TEMPLATE,
    ENABLE_CALL_FEATURES,
)"""
        if old_import2 in text:
            text = text.replace(
                old_import2,
                old_import2.replace(
                    ")",
                    "    LOGIN_WINDOW_WIDTH,\n    LOGIN_WINDOW_HEIGHT,\n"
                    "    CHAT_WINDOW_WIDTH,\n    CHAT_WINDOW_HEIGHT,\n"
                    "    STARSAIL_SHELL_CSS_JS,\n    STARSAIL_NOTIFY_JS,\n"
                    "    STARSAIL_ESC_CHAT_JS,\n)",
                ),
                1,
            )

    text = text.replace("if (isCall) {", "if (false && isCall) {")

    old_login_inj = '    def _inject_login_page_scripts(self):\n        """登录页：禁用通行密钥/WebAuthn，减少 Windows 安全中心弹窗"""'
    if old_login_inj in text and "STARSAIL_SHELL_CSS_JS" in text:
        start = text.find(old_login_inj)
        end = text.find("\n    def _inject_persistent_scripts", start)
        if end < 0:
            raise SystemExit("inject_persistent_scripts not found")
        text = (
            text[:start]
            + '    def _inject_login_page_scripts(self):\n'
            + '        """Starsail 登录页：隐藏手机/邮箱/注册入口。"""\n'
            + "        self._wv2_doc_scripts.append(STARSAIL_SHELL_CSS_JS)\n"
            + "        return\n\n"
            + text[end + 1 :]
        )

    needle = "        self._wv2_doc_scripts.append(js_code)\n        return\n"
    repl = (
        "        self._wv2_doc_scripts.append(js_code)\n"
        "        self._wv2_doc_scripts.append(STARSAIL_NOTIFY_JS)\n"
        "        self._wv2_doc_scripts.append(STARSAIL_ESC_CHAT_JS)\n"
        "        return\n"
    )
    if "self._wv2_doc_scripts.append(STARSAIL_ESC_CHAT_JS)" not in text and needle in text:
        text = text.replace(needle, repl, 1)

    text = text.replace(
        'self._normal_size = (1280, 800)',
        'self._normal_size = (CHAT_WINDOW_WIDTH, CHAT_WINDOW_HEIGHT)',
    )
    text = text.replace(
        "initTeamsEscBackToAi",
        "initStarsailEscBackToList",
    )
    text = text.replace(
        "通过桥回传给 Python 返回空白页。",
        "通过桥回传给 Python 退出当前会话。",
    )

    TARGET.write_text(text, encoding="utf-8")
    print("starsail extras applied")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""ESC：退出当前会话回到列表（Telegram 风格），不再 go_home。"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "StarsailX.py"

OLD_ESC_BLOCK = """            // ========== 0. Esc 返回 AI（不依赖焦点在 Qt） ==========
            // WebView2 是原生子窗口，Esc 键经常只被网页吃掉，Qt 收不到 keyPressEvent。
            // 这里在网页侧监听 Esc，通过桥回传给 Python 返回空白页。
            (function initStarsailEscBack() {
                if (window.__teamsEscBackToAiHook) return;
                window.__teamsEscBackToAiHook = true;
                window.addEventListener('keydown', function(e) {
                    try {
                        if (!e || e.key !== 'Escape') return;
                        if (typeof window.__externalNotificationCallback === 'function') {
                            window.__externalNotificationCallback('ui', 'esc', '', 0);
                        }
                    } catch (err) {}
                }, true);
            })();

"""

IMPORT_OLD = """    STARSAIL_NOTIFY_JS,
    STARSAIL_LOGIN_FAIL_REASONS,
)"""

IMPORT_NEW = """    STARSAIL_NOTIFY_JS,
    STARSAIL_ESC_CHAT_JS,
    STARSAIL_LOGIN_FAIL_REASONS,
)"""

INJECT_OLD = """        self._wv2_doc_scripts.append(STARSAIL_NOTIFY_JS)
        return

# ==================== 主窗口类 ===================="""

INJECT_NEW = """        self._wv2_doc_scripts.append(STARSAIL_NOTIFY_JS)
        self._wv2_doc_scripts.append(STARSAIL_ESC_CHAT_JS)
        return

# ==================== 主窗口类 ===================="""

EVENTFILTER_OLD = """                if event.key() == Qt.Key.Key_Escape:
                    if self.isFullScreen():
                        self._exit_trapped_fullscreen()
                        return True
                    self.go_home()
                    return True"""

EVENTFILTER_NEW = """                if event.key() == Qt.Key.Key_Escape:
                    if self.isFullScreen():
                        self._exit_trapped_fullscreen()
                        return True
                    if self._esc_close_active_chat():
                        return True"""

NOTIFY_ESC_OLD = """            # WebView 内 Esc：回到 AI 主界面（不影响 Teams 自己的 Esc 行为）
            if (msg_type or "") == "ui" and (sender or "") == "esc":
                try:
                    self.go_home()
                except Exception:
                    pass
                return
"""

NOTIFY_ESC_NEW = """            if (msg_type or "") == "ui" and (sender or "") == "esc":
                return
"""

METHOD_ANCHOR = """    def _exit_trapped_fullscreen(self):
        \"\"\"WebView2 视频全屏误触整窗全屏时，Esc 恢复标题栏与窗口状态。\"\"\""""

METHOD_INSERT = """    def _esc_close_active_chat(self) -> bool:
        \"\"\"Esc：退出当前聊天会话，回到会话列表（不取消账号选中）。\"\"\"
        if not self.current_account_id:
            return False
        wv = self._get_webview_for_account(self.current_account_id)
        if (
            not wv
            or not hasattr(self, "stack_widget")
            or self.stack_widget.currentWidget() is not wv
        ):
            return False
        widget = getattr(wv, "_wv2_widget", None)
        if widget and getattr(widget, "is_ready", False):
            try:
                widget.evaluate_js(
                    "try{window.__starsailEscCloseChat&&window.__starsailEscCloseChat();}catch(e){}"
                )
                return True
            except Exception:
                pass
        return False

"""


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")
    if OLD_ESC_BLOCK in text:
        text = text.replace(OLD_ESC_BLOCK, "", 1)
        print("removed old esc bridge block")
    if IMPORT_NEW not in text and IMPORT_OLD in text:
        text = text.replace(IMPORT_OLD, IMPORT_NEW, 1)
        print("updated imports")
    elif "STARSAIL_ESC_CHAT_JS" not in text:
        raise SystemExit("import block not found")

    if INJECT_NEW not in text:
        if INJECT_OLD not in text:
            raise SystemExit("inject tail not found")
        text = text.replace(INJECT_OLD, INJECT_NEW, 1)
        print("inject esc js")

    if EVENTFILTER_OLD in text:
        text = text.replace(EVENTFILTER_OLD, EVENTFILTER_NEW, 1)
        print("patched eventFilter")

    if NOTIFY_ESC_OLD in text:
        text = text.replace(NOTIFY_ESC_OLD, NOTIFY_ESC_NEW, 1)
        print("patched notify esc")

    if "def _esc_close_active_chat(self)" not in text:
        if METHOD_ANCHOR not in text:
            raise SystemExit("_exit_trapped_fullscreen anchor missing")
        text = text.replace(METHOD_ANCHOR, METHOD_INSERT + METHOD_ANCHOR, 1)
        print("added _esc_close_active_chat")

    TARGET.write_text(text, encoding="utf-8")
    import py_compile

    py_compile.compile(str(TARGET), doraise=True)
    print("patch esc ok")


if __name__ == "__main__":
    main()

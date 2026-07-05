# -*- coding: utf-8 -*-
"""一次性补丁：将复制的 TeamsX 核心改为 StarsailX。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def patch_file(path: Path, replacements: list[tuple[str, str]]) -> None:
    text = path.read_text(encoding="utf-8")
    original = text
    for old, new in replacements:
        if old not in text:
            raise SystemExit(f"patch miss in {path.name}: {old[:80]!r}")
        text = text.replace(old, new, 1)
    if text != original:
        path.write_text(text, encoding="utf-8")
        print(f"patched {path.name}")


def main() -> None:
    starsail = ROOT / "StarsailX.py"

    patch_file(
        starsail,
        [
            (
                'TeamsX 多账号管理器 v2.0',
                'StarsailX 多账号管理器',
            ),
            (
                '- Windows 使用 Edge WebView2 显示 Teams（qtwebview2），不再回退 QtWebEngine',
                '- Windows 使用 Edge WebView2 显示 Starsail（qtwebview2）',
            ),
            (
                'from starsailx.config import DATA_ROOT as _TEAMS_DATA_ROOT_EARLY',
                'from starsailx.config import DATA_ROOT as _TEAMS_DATA_ROOT_EARLY\n'
                'from starsailx.site_config import (\n'
                '    STARSAIL_APP_URL,\n'
                '    STARSAIL_SHELL_VERIFY_JS,\n'
                '    STARSAIL_LOGIN_JS_TEMPLATE,\n'
                '    STARSAIL_LOGIN_FAIL_REASONS,\n'
                '    ENABLE_CALL_FEATURES,\n'
                '    LOGIN_WINDOW_WIDTH,\n'
                '    LOGIN_WINDOW_HEIGHT,\n'
                '    CHAT_WINDOW_WIDTH,\n'
                '    CHAT_WINDOW_HEIGHT,\n'
                ')',
            ),
            (
                '        return os.path.join(cls.db_dir(), "teams_accounts.db")',
                '        return os.path.join(cls.db_dir(), "starsail_accounts.db")',
            ),
            (
                '        teams_url = "https://teams.microsoft.com/?lang=zh-CN"\n'
                '        if self._login_email:\n'
                '            teams_url += f"&login_hint={quote(self._login_email)}"',
                '        teams_url = STARSAIL_APP_URL',
            ),
            (
                """    @staticmethod
    def _is_login_host_url(url: str) -> bool:
        u = (url or "").lower()
        return (
            "login.microsoftonline.com" in u
            or "login.microsoft.com" in u
            or "login.live.com" in u
            or "account.live.com" in u
        )""",
                """    @staticmethod
    def _is_login_host_url(url: str) -> bool:
        return False""",
            ),
            (
                """    @staticmethod
    def _is_teams_app_url(url: str) -> bool:
        u = (url or "").lower()
        if TeamsWebView._is_login_host_url(u):
            return False
        return (
            "teams.microsoft.com" in u
            or "teams.cloud.microsoft" in u
            or "teams.live.com" in u
        )""",
                """    @staticmethod
    def _is_teams_app_url(url: str) -> bool:
        u = (url or "").lower()
        return "starsail.vip" in u""",
            ),
        ],
    )

    text = starsail.read_text(encoding="utf-8")
    text = re.sub(
        r"_TEAMS_SHELL_VERIFY_JS = r\"\"\"[\s\S]*?\"\"\"",
        '_TEAMS_SHELL_VERIFY_JS = STARSAIL_SHELL_VERIFY_JS',
        text,
        count=1,
    )
    text = text.replace("_TEAMS_SHELL_VERIFY_JS", "STARSAIL_SHELL_VERIFY_JS")
    text = text.replace("_TEAMS_LOGIN_FAIL_REASONS", "STARSAIL_LOGIN_FAIL_REASONS")

    login_old = re.search(
        r"def _run_login_script\(self\):\n        if not self\._login_active[\s\S]*?"
        r'self\.page\(\)\.runJavaScript\(js, self\._on_login_script_result\)',
        text,
    )
    if not login_old:
        raise SystemExit("login script block not found")

    login_new = '''def _run_login_script(self):
        if not self._login_active or not self.page() or self._is_closing:
            return
        if self._login_poll_count >= self._login_max_polls:
            self._finish_login(False, "登录步骤超时")
            return
        self._login_poll_count += 1
        email_js = json.dumps(self._login_email)
        pass_js = json.dumps(self._login_password)
        js = (
            STARSAIL_LOGIN_JS_TEMPLATE.replace("__ACCOUNT_JSON__", email_js)
            .replace("__PASSWORD_JSON__", pass_js)
        )
        self.page().runJavaScript(js, self._on_login_script_result)'''
    text = text[: login_old.start()] + login_new + text[login_old.end() :]

    notify_old = """            if kind in ("incoming_call", "incoming_video"):
                call_kind = "video" if kind == "incoming_video" else "call"
                self._handle_incoming_call(aid, call_kind, sender, content)
                return"""
    notify_new = """            if not ENABLE_CALL_FEATURES and kind in (
                "incoming_call", "incoming_video", "call_end", "call", "video"
            ):
                return
            if kind in ("incoming_call", "incoming_video"):
                call_kind = "video" if kind == "incoming_video" else "call"
                self._handle_incoming_call(aid, call_kind, sender, content)
                return"""
    if notify_old not in text:
        raise SystemExit("notify block not found")
    text = text.replace(notify_old, notify_new, 1)

    text = text.replace(
        'self._normal_size = (1280, 800)',
        'self._normal_size = (CHAT_WINDOW_WIDTH, CHAT_WINDOW_HEIGHT)',
        1,
    )

    starsail.write_text(text, encoding="utf-8")
    print("patched StarsailX.py shell/login/notify")

    patch_file(
        ROOT / "starsailx" / "config.py",
        [
            ('_PREFERRED_DATA_ROOT = r"D:\\TeamsX"', '_PREFERRED_DATA_ROOT = r"D:\\StarsailX"'),
            ('TEAMSX_DATA_ROOT', 'STARSAILX_DATA_ROOT'),
            ('"TeamsX"', '"StarsailX"'),
            ('[TeamsX]', '[StarsailX]'),
        ],
    )

    patch_file(
        ROOT / "starsailx" / "app.py",
        [
            ('from TeamsX import MainWindow', 'from StarsailX import MainWindow'),
            ('find_other_starsailx_pids', 'find_other_starsailx_pids'),
            ('start_single_instance_listener', 'start_single_instance_listener'),
            ('残留 TeamsX 进程', '残留 StarsailX 进程'),
            ('app._teamsx_single_instance_server', 'app._starsailx_single_instance_server'),
        ],
    )

    patch_file(
        ROOT / "starsailx" / "single_instance.py",
        [
            ('SERVER_NAME = "TeamsX-SingleInstance-v1"', 'SERVER_NAME = "StarsailX-SingleInstance-v1"'),
            ('_TEAMSX_CMD_MARKERS', '_STARSAILX_CMD_MARKERS'),
            ('("starsailx.py", "teamsx\\\\__main__", "teamsx/__main__", "-m starsailx")',
             '("starsailx.py", "starsailx\\\\__main__", "starsailx/__main__", "-m starsailx", "starsailx.py")'),
            ('def _command_line_looks_like_starsailx', 'def _command_line_looks_like_starsailx'),
            ('def find_other_starsailx_pids', 'def find_other_starsailx_pids'),
            ('_command_line_looks_like_starsailx', '_command_line_looks_like_starsailx'),
            ('其他 TeamsX 主进程', '其他 StarsailX 主进程'),
            ('残留 TeamsX 空壳', '残留 StarsailX 空壳'),
        ],
    )

    patch_file(
        ROOT / "starsailx" / "startup.py",
        [
            ('[TeamsX]', '[StarsailX]'),
            ('Teams 页面引擎', 'Starsail 页面引擎'),
            ('当前 Teams 引擎', '当前 Starsail 引擎'),
        ],
    )

    patch_file(
        ROOT / "starsailx" / "ui" / "close_action_dialog.py",
        [('关闭 TeamsX？', '关闭 StarsailX？')],
    )

    patch_file(
        ROOT / "starsailx" / "notify" / "win_toast.py",
        [
            ('APP_USER_MODEL_ID = "TeamsX.TeamsX.CallNotify"', 'APP_USER_MODEL_ID = "StarsailX.StarsailX.Notify"'),
            ('teamsx_call_dismiss', 'starsailx_call_dismiss'),
            ('"TeamsX.lnk"', '"StarsailX.lnk"'),
            ('TeamsX ·', 'StarsailX ·'),
        ],
    )

    for name in ("StarsailX.spec", "build.ps1", "StarsailX_setup.iss"):
        path = ROOT / name
        if not path.exists():
            continue
        content = path.read_text(encoding="utf-8")
        content = (
            content.replace("TeamsX", "StarsailX")
            .replace("starsailx", "starsailx")
            .replace("TEAMSX_", "STARSAILX_")
        )
        if name == "build.ps1":
            content = re.sub(
                r"\$CallMp3 = Join-Path \$AudioDir \"video\.mp3\"[\s\S]*?"
                r'if \(-not \(Test-Path -LiteralPath \$CallMp3\)\) \{[\s\S]*?\}\n',
                "",
                content,
                count=1,
            )
        path.write_text(content, encoding="utf-8")
        print(f"patched {name}")

    print("done")


if __name__ == "__main__":
    main()

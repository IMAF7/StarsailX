"""Restore notification / memory timer methods removed by slim_starsailx."""
from pathlib import Path

path = Path(r"c:\Users\admin\Desktop\StarsailX\StarsailX.py")
text = path.read_text(encoding="utf-8")

insert = """
    def update_status(self, text: str):
        \"\"\"更新状态标签（同文本不重绘，避免无谓刷新）\"\"\"
        try:
            if self.status_label.text() == text:
                return
        except Exception:
            pass
        self.status_label.setText(text)

    def _has_active_call(self) -> bool:
        \"\"\"来电进行中时保护状态栏（StarsailX 无通话功能）。\"\"\"
        return False

    def _refresh_default_status(self) -> None:
        \"\"\"状态栏默认文案。\"\"\"
        if self._has_active_call():
            return
        total_accounts = len(self.db.get_all_accounts())
        self.update_status(f"共 {total_accounts} 个账号")

    def start_notification_check(self):
        \"\"\"启动通知检查定时器\"\"\"
        if self.check_timer:
            self.check_timer.stop()

        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.process_notification_queue)
        self.check_timer.start(NOTIFICATION_CHECK_INTERVAL)

        if getattr(self, "badge_fast_timer", None):
            self.badge_fast_timer.stop()
        self.badge_fast_timer = QTimer(self)
        self.badge_fast_timer.timeout.connect(self._poll_foreground_badge)
        self.badge_fast_timer.start(BADGE_FOREGROUND_POLL_MS)

        if getattr(self, "badge_background_timer", None):
            self.badge_background_timer.stop()
        self.badge_background_timer = QTimer(self)
        self.badge_background_timer.timeout.connect(
            self._poll_background_badge_round_robin
        )
        self.badge_background_timer.start(BADGE_BACKGROUND_POLL_MS)

    def _poll_foreground_badge(self):
        \"\"\"当前账号：轻量未读同步（页面内 Observer 仍负责即时消息）。\"\"\"
        if self.is_closing or getattr(self, "_app_locked", False):
            return
        account_id = self.current_account_id
        if not account_id:
            return
        web_view = self._get_webview_for_account(account_id)
        if web_view and web_view.is_valid and not web_view.is_loading:
            web_view.poll_unread_badge()

    def _poll_background_badge_round_robin(self):
        \"\"\"后台账号：每 3s 扫 1 个号的未读，避免 120ms 全员唤醒。\"\"\"
        if self.is_closing or getattr(self, "_app_locked", False):
            return
        all_ids = self._loaded_account_ids()
        if not all_ids:
            return
        n = len(all_ids)
        tries = 0
        while tries < n:
            tries += 1
            account_id = all_ids[self._badge_poll_index % n]
            self._badge_poll_index = (self._badge_poll_index + 1) % n
            if account_id == self.current_account_id:
                continue
            web_view = self._get_webview_for_account(account_id)
            if not web_view or not web_view.is_valid or web_view.is_loading:
                continue
            web_view.poll_unread_badge()
            break

    def process_notification_queue(self):
        \"\"\"后台账号轻量未读轮询；前台消息由页面内 Notification 桥 + JS 扫描负责。\"\"\"
        if self.is_closing or getattr(self, "_app_locked", False):
            return

        checked = 0
        fg_id = self.current_account_id
        max_checks = BADGE_CHECKS_PER_TICK
        if not self.check_queue:
            self.check_queue.extend(self._loaded_account_ids())

        while self.check_queue and checked < max_checks:
            account_id = self.check_queue.popleft()
            if account_id == fg_id:
                continue
            web_view = self._get_webview_for_account(account_id)
            if web_view and web_view.is_valid and not web_view.is_loading:
                web_view.poll_unread_badge()
                checked += 1

    def start_memory_cleanup(self):
        \"\"\"启动内存清理定时器\"\"\"
        if self.memory_timer:
            self.memory_timer.stop()

        self.memory_timer = QTimer()
        self.memory_timer.timeout.connect(self.cleanup_idle_webviews)
        self.memory_timer.start(MEMORY_CLEAN_INTERVAL * 1000)

"""

marker = "    def _refresh_default_status(self) -> None:"
start = text.find(marker)
if start == -1:
    raise SystemExit("marker not found")
end = text.find("    def start_memory_guard(self):", start)
if end == -1:
    raise SystemExit("end marker not found")

new_text = text[:start] + insert + text[end:]
path.write_text(new_text, encoding="utf-8")
print("patched", path)

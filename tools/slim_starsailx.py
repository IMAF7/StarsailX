# -*- coding: utf-8 -*-
"""一次性精简 StarsailX：移除 AI/分组/导入/锁定/在线点/内存监控 UI。"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "StarsailX.py"


def delete_between(text: str, start_marker: str, end_marker: str) -> str:
    i = text.find(start_marker)
    if i < 0:
        raise SystemExit(f"start marker not found: {start_marker!r}")
    j = text.find(end_marker, i)
    if j < 0:
        raise SystemExit(f"end marker not found: {end_marker!r}")
    return text[:i] + text[j:]


def replace_one(text: str, old: str, new: str, label: str) -> str:
    if old not in text:
        raise SystemExit(f"replace miss ({label}): {old[:100]!r}")
    return text.replace(old, new, 1)


def drop_class(text: str, name: str) -> str:
    key = f"class {name}"
    if key not in text:
        return text
    start = text.find(key)
    rest = text[start + 1 :]
    nxt = rest.find("\nclass ")
    if nxt < 0:
        return text[:start]
    return text[:start] + rest[nxt + 1 :]


def main() -> None:
    text = TARGET.read_text(encoding="utf-8")

    for cls in (
        "SidebarContentHost",
        "_GroupComboCenterDelegate",
        "GroupFilterComboBox",
        "AccountGroupPickerDialog",
        "GroupManagePanel",
    ):
        text = drop_class(text, cls)
    text = delete_between(
        text,
        "# ==================== AI 聊天（独立模块，与 Teams/账号无关） ====================",
        "# ==================== 主窗口类 ====================",
    )

    # --- imports ---
    text = replace_one(
        text,
        "import urllib.error\nimport urllib.request\n",
        "",
        "urllib",
    )
    text = re.sub(
        r"try:\n    import markdown.*?HAS_MISTUNE = False\n\n",
        "",
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = replace_one(
        text,
        "try:\n    import chardet\n\n    HAS_CHARDET = True\nexcept ImportError:\n    HAS_CHARDET = False\n    print(\"提示：安装 chardet 可获得更好的文件编码检测，命令：pip install chardet\")\n\n",
        "",
        "chardet",
    )

    # --- 状态点图标 ---
    text = replace_one(
        text,
        '    """账号列表：左侧状态点 + 备注 + 右侧红色未读角标"""',
        '    """账号列表：备注 + 右侧红色未读角标"""',
        "delegate doc",
    )
    text = replace_one(
        text,
        """        icon = index.data(Qt.ItemDataRole.DecorationRole)
        text_left = rect.left() + 10
        if icon and not icon.isNull():
            icon_sz = 16
            iy = rect.top() + (rect.height() - icon_sz) // 2
            icon.paint(painter, QRect(text_left, iy, icon_sz, icon_sz))
            text_left += icon_sz + 8

""",
        "        text_left = rect.left() + 10\n\n",
        "delegate icon",
    )

    # --- go_home -> 空白页 ---
    text = replace_one(
        text,
        """    def go_home(self):
        \"\"\"返回主界面（Esc → TeamsXAi，点击左侧账号则切回 Teams）\"\"\"
        try:
            self.current_account_id = None
            if hasattr(self, "stack_widget") and self.stack_widget:
                self.stack_widget.setCurrentIndex(0)
            if hasattr(self, "account_list") and self.account_list:
                self.account_list.clearSelection()
            self._sync_webview_lifecycle_states()
            self.update_status("TeamsXAi")
            if hasattr(self, "ai_chat_panel"):
                QTimer.singleShot(0, self.ai_chat_panel._focus_input)
        except Exception as e:
            print(f"返回主界面错误: {e}")
""",
        """    def go_home(self):
        \"\"\"取消选中账号，显示右侧空白页（内部使用，Esc 已改为退出当前会话）。\"\"\"
        try:
            if self.current_account_id:
                wv = self._get_webview_for_account(self.current_account_id)
                if wv and self.stack_widget.currentWidget() is wv:
                    self._dock_webview_to_park(wv)
            self.current_account_id = None
            if hasattr(self, "account_list") and self.account_list:
                self.account_list.clearSelection()
            if hasattr(self, "stack_widget") and self.stack_widget:
                self.stack_widget.setCurrentWidget(self._empty_page)
            self._sync_webview_lifecycle_states()
            self._refresh_default_status()
        except Exception as e:
            print(f"返回空白页错误: {e}")
""",
        "go_home",
    )

    # --- stack: empty page instead of AI ---
    text = replace_one(
        text,
        """        self.stack_widget = QStackedWidget()
        self.stack_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.ai_chat_panel = AiChatPanel()
        self.stack_widget.addWidget(self.ai_chat_panel)
        right_shell_layout.addWidget(self.stack_widget)
""",
        """        self.stack_widget = QStackedWidget()
        self.stack_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._empty_page = QWidget()
        self._empty_page.setObjectName("emptyChatPage")
        self.stack_widget.addWidget(self._empty_page)
        self._sync_empty_page_theme()
        right_shell_layout.addWidget(self.stack_widget)
""",
        "stack_widget",
    )

    # --- remove lock button ---
    text = replace_one(
        text,
        """        # 锁定按钮（与「管理」按钮同尺寸）
        self.lock_btn = QPushButton("锁定")
        self.lock_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.lock_btn.setFixedSize(SIDEBAR_SMALL_BTN_W, SIDEBAR_SMALL_BTN_H)
        self.lock_btn.clicked.connect(self.on_lock_clicked)
        header_layout.addWidget(self.lock_btn)

""",
        "",
        "lock_btn",
    )

    # --- remove group row ---
    text = replace_one(
        text,
        """        group_row = QHBoxLayout()
        # 右侧与 header_layout(8px) 对齐，便于与「锁定」同列
        group_row.setContentsMargins(10, 0, 8, 4)
        group_row.setSpacing(8)
        self._group_label = QLabel("分组")
        self._group_label.setStyleSheet("font-size: 13px; font-weight: 600; color: #e0e0e0; padding-right: 2px;")
        group_row.addWidget(self._group_label)

        self.group_combo = GroupFilterComboBox()
        self.group_combo.setFixedHeight(SIDEBAR_SMALL_BTN_H + 2)
        self.group_combo.setFixedWidth(118)
        self.group_combo.currentIndexChanged.connect(self._on_group_combo_changed)
        group_row.addWidget(self.group_combo)

        group_row.addSpacing(4)
        self.group_manage_btn = QPushButton("管理")
        self.group_manage_btn.setFixedSize(SIDEBAR_SMALL_BTN_W, SIDEBAR_SMALL_BTN_H)
        self.group_manage_btn.clicked.connect(self.manage_groups)
        group_row.addWidget(self.group_manage_btn)

        left_layout.addLayout(group_row)

""",
        "",
        "group_row",
    )

    # --- sidebar: direct account list ---
    text = replace_one(
        text,
        """        self.group_manage_panel = GroupManagePanel(self.db, None)
        self.group_manage_panel.closed.connect(self._on_group_manage_panel_closed)
        self.group_manage_panel.apply_panel_theme(getattr(self, "_theme_light", False))
        self._sidebar_content_host = SidebarContentHost(
            self.account_list, self.group_manage_panel
        )
        left_layout.addWidget(self._sidebar_content_host, 1)
        self._sidebar_view_anim: Optional[QParallelAnimationGroup] = None
        self._sidebar_view_anim_running = False
""",
        "        left_layout.addWidget(self.account_list, 1)\n",
        "sidebar host",
    )

    # --- remove mem label + import btn ---
    text = replace_one(
        text,
        """        # 内存/进程提示紧跟齿轮（齿轮展开时隐藏，避免与弹出按钮重叠）
        # minimumWidth(0) + Preferred：文字再长也只在剩余空间内显示，不撑宽账号列表
        self.mem_status_label = QLabel("")
        self.mem_status_label.setAlignment(
            Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
        )
        self.mem_status_label.setMinimumWidth(0)
        # Ignored 宽度策略：文字再长也不撑宽账号列表，可压缩到 0
        self.mem_status_label.setSizePolicy(
            QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Preferred
        )
        self.mem_status_label.setAttribute(
            Qt.WidgetAttribute.WA_TransparentForMouseEvents, True
        )
        self._mem_hint_color = ""
        # 标签 stretch=1 吃下剩余空间显示文字；尾部弹簧 stretch=0 仅在标签隐藏时
        # 顶住齿轮在最左，避免齿轮跑到中间
        bottom_layout.addWidget(self.mem_status_label, 1)
        bottom_layout.addStretch(0)
""",
        "        bottom_layout.addStretch(1)\n",
        "mem_label",
    )

    text = replace_one(
        text,
        """        self.import_btn = QPushButton("导入", self._bottom_bar)
        self.import_btn.clicked.connect(self.import_accounts)
""",
        "",
        "import_btn",
    )
    text = replace_one(
        text,
        """        self._flyout_buttons = [
            self.import_btn, self.add_btn, self.refresh_btn
        ]
""",
        """        self._flyout_buttons = [
            self.add_btn, self.refresh_btn
        ]
""",
        "flyout",
    )

    # --- status bar without online count ---
    text = replace_one(
        text,
        """    def _refresh_default_status(self) -> None:
        \"\"\"状态栏默认文案：活跃 / 休眠 / 账号总数。

        来电进行中时跳过：否则 90ms 一次的轮询会把“X 来电”反复覆盖回默认文案，
        造成状态栏蓝色文字闪烁。内存/进程信息单独显示在底部栏，避免撑宽账号列表。
        \"\"\"
        self._refresh_memory_hint()
        if self._has_active_call():
            return
        online = len(self._loaded_account_ids())
        total_accounts = len(self.db.get_all_accounts())
        self.update_status(f"在线 {online} · 共 {total_accounts} 账号")
""",
        """    def _refresh_default_status(self) -> None:
        \"\"\"状态栏默认文案。\"\"\"
        if self._has_active_call():
            return
        total_accounts = len(self.db.get_all_accounts())
        self.update_status(f"共 {total_accounts} 个账号")
""",
        "default_status",
    )

    # --- notify dedup off ---
    text = replace_one(
        text,
        """    def _claim_api_notify(self, account_id: int, tag: str) -> bool:
        \"\"\"Teams Notification API 事件去重（按 tag，窗口较长）。\"\"\"
        aid = int(account_id)
        token = (tag or "").strip()
        if not token:
            return True
        dedup_key = (aid, token)
        now = time.time()
        prev = self._api_notify_dedup.get(dedup_key)
        if prev is not None and (now - float(prev)) < float(NOTIFY_API_DEDUP_TTL_SEC):
            return False
        self._api_notify_dedup[dedup_key] = now
        if len(self._api_notify_dedup) > MSG_NOTIFY_DEDUP_MAX:
            items = sorted(self._api_notify_dedup.items(), key=lambda x: x[1])
            for (kk, _) in items[: len(items) // 2]:
                self._api_notify_dedup.pop(kk, None)
        return True
""",
        """    def _claim_api_notify(self, account_id: int, tag: str) -> bool:
        \"\"\"Starsail：不去重，相同消息也通知。\"\"\"
        return True
""",
        "claim_api_notify",
    )

    text = replace_one(
        text,
        """        tag = self._extract_msg_notify_key(content) or (content or sender or "msg").strip()
        if not self._claim_api_notify(aid, tag):
            return
""",
        "",
        "api_notify_check",
    )

    # --- ESC comment in JS ---
    text = text.replace(
        "通过桥回传给 Python 执行 go_home()。",
        "通过桥回传给 Python 返回空白页。",
    )
    text = text.replace("initTeamsEscBackToAi", "initStarsailEscBack")

    # --- remove AI theme hooks ---
    text = text.replace(
        """        if hasattr(self, "ai_chat_panel"):
            self.ai_chat_panel.apply_theme(light)
""",
        "",
    )
    text = text.replace(
        """        if hasattr(self, "mem_status_label"):
            self._refresh_memory_hint()
""",
        "",
    )
    text = text.replace(
        """        if hasattr(self, "mem_status_label"):
            self._style_lock_overlay()
""",
        "",
    )

    # --- remove mem label show/hide in flyout ---
    text = re.sub(
        r"\s*if hasattr\(self, \"mem_status_label\"\):\s*\n\s*self\.mem_status_label\.(show|hide)\(\)\s*\n",
        "\n",
        text,
    )

    # --- remove account dot icon in list item ---
    text = replace_one(
        text,
        "        item.setIcon(account_status_icon(self._display_status_for_account(acc_id)))\n",
        "",
        "list item icon",
    )

    # --- remove context menu group actions ---
    text = replace_one(
        text,
        """        if not self.db.account_has_group(account_id):
            add_grp = QAction("添加分组", self)
            add_grp.triggered.connect(lambda checked, aid=account_id: self._account_add_to_group(aid))
            menu.addAction(add_grp)
        else:
            edit_grp = QAction("编辑分组", self)
            edit_grp.triggered.connect(lambda checked, aid=account_id: self._account_edit_group(aid))
            menu.addAction(edit_grp)

""",
        "",
        "context menu group",
    )

    # --- remove import_accounts method ---
    text = delete_between(
        text,
        "    def import_accounts(self):",
        "    def login_single_account(self, account_id: int):",
    )

    # --- remove lock methods (keep update_status and notification timers) ---
    text = delete_between(
        text,
        "    def _lock_password_record(self) -> Optional[Tuple[str, str]]:",
        "    def update_status(self, text: str):",
    )

    # --- remove group management methods ---
    for marker in (
        "    def _animate_sidebar_view(",
        "    def _reload_group_list(",
        "    def _account_add_to_group(",
    ):
        if marker in text:
            # delete until next def at same indent that's not nested
            pass

    # remove group methods individually
    group_methods = [
        "    def _animate_sidebar_view(",
        "    def _open_group_manage_panel(",
        "    def _close_group_manage_panel(",
        "    def manage_groups(",
        "    def _on_group_manage_panel_closed(",
        "    def _reload_group_list(",
        "    def _on_group_combo_changed(",
        "    def _account_add_to_group(",
        "    def _account_edit_group(",
    ]
    for m in group_methods:
        while m in text:
            start = text.find(m)
            # find next method at class level (4 spaces + def)
            rest = text[start + len(m):]
            nxt = re.search(r"\n    def [a-zA-Z_]", rest)
            if not nxt:
                break
            end = start + len(m) + nxt.start() + 1
            text = text[:start] + text[end:]

    # --- remove memory hint UI helpers only (keep notification / cleanup timers) ---
    text = delete_between(
        text,
        "    @staticmethod\n    def _fmt_mem_size(mb: int) -> str:",
        "    def start_notification_check(self):",
    )

    # --- remove _refresh_account_dot family ---
    for m in (
        "    def _display_status_for_account(",
        "    def _refresh_account_dot(",
        "    def _refresh_all_account_dots(",
        "    def _update_account_status_ui(",
    ):
        while m in text:
            start = text.find(m)
            rest = text[start + len(m):]
            nxt = re.search(r"\n    def [a-zA-Z_]", rest)
            if not nxt:
                break
            end = start + len(m) + nxt.start() + 1
            text = text[:start] + text[end:]

    # --- remove _reload_group_list at startup ---
    text = text.replace("        self._reload_group_list()\n", "")

    # --- remove group filter in list display ---
    text = replace_one(
        text,
        """            group_ids = None
            if self._current_group_id:
                group_ids = self.db.get_account_ids_in_group(self._current_group_id)

""",
        "",
        "group filter",
    )
    text = replace_one(
        text,
        """                if group_ids is not None and acc_id not in group_ids:
                    continue
""",
        "",
        "group filter continue",
    )

    text = text.replace("self.stack_widget.setCurrentIndex(0)", "self.go_home()")

    # --- remove unused icon helpers if only used for dots ---
    text = delete_between(
        text,
        "def _make_dot_icon(color: str, size: int = 14) -> QIcon:",
        "def _bridge_connect_js_source() -> str:",
    )
    text = text.replace(
        "DISPLAY_ACTIVE = \"active\"\nDISPLAY_SLEEP = \"sleep\"\nDISPLAY_OFFLINE = \"offline\"\n\n",
        "",
    )

    # --- StarsailX: no call features ---
    text = replace_one(
        text,
        """    def _has_active_call(self) -> bool:
        \"\"\"是否有正在响铃/进行中的来电（用于保护状态栏文案不被默认刷新覆盖）。\"\"\"
        if getattr(self, "_call_ring_active_aid", None) is not None:
            return True
        for sess in (getattr(self, "_call_sessions", None) or {}).values():
            if sess.get("ring_loop_started") and not sess.get("suppressed"):
                return True
        return False
""",
        """    def _has_active_call(self) -> bool:
        \"\"\"来电进行中时保护状态栏（StarsailX 无通话功能）。\"\"\"
        return False
""",
        "has_active_call",
    )

    text = text.replace(
        "self._get_webview(self.current_account_id)",
        "self._get_webview_for_account(self.current_account_id)",
    )

    TARGET.write_text(text, encoding="utf-8")
    print(f"Slimmed {TARGET.name}")


if __name__ == "__main__":
    main()

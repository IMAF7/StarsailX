#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
StarsailX 多账号管理器
- B/Z/M 导入，点击账号登录（一次一个）
- 程序/数据/缓存固定在 D:\\TeamsX（删除该文件夹即清空一切）
- 红色未读角标、Teams 网页内提示音/提醒（非系统通知）、多账号 WebView 池
- Windows 使用 Edge WebView2 显示 Starsail（qtwebview2）
"""
import sys
import os

import json
import locale
import math
import re
import base64
from urllib.parse import quote
import sqlite3
import shutil
import gc
import hashlib
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Set, List, Tuple
from collections import deque

from starsailx.config import DATA_ROOT as _TEAMS_DATA_ROOT_EARLY
from starsailx.site_config import (
    STARSAIL_APP_URL,
    STARSAIL_SHELL_VERIFY_JS,
    STARSAIL_LOGIN_JS_TEMPLATE,
    ENABLE_CALL_FEATURES,
    LOGIN_WINDOW_WIDTH,
    LOGIN_WINDOW_HEIGHT,
    CHAT_WINDOW_WIDTH,
    CHAT_WINDOW_HEIGHT,
    STARSAIL_SHELL_CSS_JS,
    STARSAIL_NOTIFY_JS,
)
from starsailx.bootstrap.ssl import urllib_ssl_context as _urllib_ssl_context

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
QHBoxLayout, QListWidget, QListWidgetItem, QStackedWidget,
QPushButton, QLabel, QDialog, QLineEdit, QFormLayout,
QMessageBox, QSplitter, QFileDialog, QMenu, QCheckBox,
QScrollArea, QComboBox, QAbstractItemView, QStyledItemDelegate, QStyleOptionViewItem, QStyle,
QStylePainter, QStyleOptionComboBox,
QTextEdit, QSizePolicy, QFrame, QAbstractScrollArea, QWIDGETSIZE_MAX,
QSystemTrayIcon, QGraphicsDropShadowEffect, QGraphicsOpacityEffect)
from PyQt6.QtGui import (
    QAction, QActionGroup, QFont, QColor, QBrush, QCursor, QGuiApplication,
    QImage, QPixmap, QIcon, QPainter, QFontMetrics, QTextCursor,
    QTextBlockFormat, QPainterPath, QBitmap, QRegion, QPen,
)
from PyQt6.QtCore import (
    Qt, QUrl, QTimer, QPoint, QPointF, QRect, QRectF, QSize, pyqtSignal, QObject, pyqtSlot,
    QThread, QEvent, QEventLoop, QFileSystemWatcher,
    QPropertyAnimation, QEasingCurve, pyqtProperty, QParallelAnimationGroup,
    QSequentialAnimationGroup, QAbstractAnimation,
)
from starsailx.engine.webview2 import (
    use_webview2,
    create_webview2_widget,
    dispose_webview2_widget,
    bridge_connect_js_webview2,
    apply_webview2_runtime_env,
)
from starsailx.notify.win_taskbar_badge import get_taskbar_badge_controller
from starsailx.ui.close_action_dialog import CloseActionCardDialog
from starsailx.ui.confirm_card_dialog import ConfirmCardDialog
from starsailx.ui import win_native_frame

_HAS_TEAMS_ENGINE = True

# 原生窗口边框：保留自定义标题栏，但用系统 DWM 提供最小化/最大化/还原动画、
# 贴边、原生阴影与圆角（与大型软件一致）。
# 注意：默认关闭。开启后窗口改为系统原生边框（自绘客户区），需在本机实测确认
# 显示/缩放/最大化正常后再启用；置 False 即回退旧的自绘无边框窗口。
USE_NATIVE_WINDOW_FRAME = False

DIALOG_LIGHT_STYLE = """
QDialog, QWidget { background-color: #f5f5f5; color: #1a1a1a; }
QLabel { color: #1a1a1a; font-size: 13px; }
QLineEdit, QListWidget { background-color: #ffffff; color: #1a1a1a; border: 1px solid #ccc; padding: 6px; }
QCheckBox { color: #1a1a1a; font-size: 13px; }
QPushButton { background-color: #e8e8e8; color: #1a1a1a; border: 1px solid #bbb; padding: 6px 12px; border-radius: 4px; }
QPushButton:hover { background-color: #ddd; }
"""

# 尝试导入 chardet 用于编码检测
# 自定义数据角色常量
REMARK_ROLE = Qt.ItemDataRole.UserRole + 1
STATUS_ROLE = Qt.ItemDataRole.UserRole + 2
GROUP_ID_ROLE = Qt.ItemDataRole.UserRole + 3
PIN_ROLE = Qt.ItemDataRole.UserRole + 4
BADGE_COUNT_ROLE = Qt.ItemDataRole.UserRole + 5

MAX_PINNED_ACCOUNTS = 20

BADGE_RED = "#e53935"
BADGE_RED_HOVER = "#c62828"
TEXT_NORMAL = "#e8e8e8"
TEXT_NORMAL_LIGHT = "#1a1a1a"


def list_delegate_colors() -> Dict[str, str]:
    if CURRENT_THEME == "light":
        return {
            "text": TEXT_NORMAL_LIGHT,
            "text_sel": "#1a3c66",
            "bg_sel": "#e3efff",
            "bg_sel_border": "#9cc4f5",
            "bg_hover": "#eef2f7",
        }
    return {
        "text": TEXT_NORMAL,
        "text_sel": "#eaf2ff",
        "bg_sel": "#33507a",
        "bg_sel_border": "#5a8edb",
        "bg_hover": "#34373c",
    }
BADGE_DEBOUNCE_MS = 120

SCROLLBAR_STYLE = """
QScrollBar:horizontal { height: 0px; max-height: 0px; background: transparent; }
QScrollBar::handle:horizontal { height: 0px; min-height: 0px; background: transparent; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; height: 0; border: none; background: none; }
QScrollBar:vertical { width: 4px; margin: 0; border: none; }
QScrollBar::handle:vertical { min-height: 20px; border-radius: 2px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; border: none; background: none; }
"""

SCROLLBAR_DARK = """
QScrollBar:vertical { background: #252525; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: #252525; }
QScrollBar::handle:vertical { background: #5a5a5a; }
QScrollBar::handle:vertical:hover { background: #707070; }
QScrollBar::handle:vertical:pressed { background: #808080; }
"""

SCROLLBAR_LIGHT = """
QScrollBar:vertical { background: #ffffff; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: #ffffff; }
QScrollBar::handle:vertical { background: #c8c8c8; }
QScrollBar::handle:vertical:hover { background: #b0b0b0; }
QScrollBar::handle:vertical:pressed { background: #999999; }
"""

APP_DARK_STYLE = """
QMainWindow { background: transparent; }
QWidget#shadowOuter { background: transparent; }
QFrame#mainFrame {
    background-color: #1e1e1e;
    border: none;
    border-radius: 0px;
}
QWidget { background-color: #1e1e1e; color: #e8e8e8; }
QLabel { color: #e8e8e8; background: transparent; }
QListWidget {
    background-color: #252525; border: none; outline: none; color: #e8e8e8;
}
QListWidget::item { padding: 12px 10px; border-bottom: 1px solid #3c3c3c; color: #e8e8e8; }
QListWidget::item:selected { background-color: #3c3c3c; color: #ffffff; }
QListWidget::item:hover { background-color: #2d2d2d; }
QLineEdit, QComboBox {
    background-color: #3c3c3c; color: #ffffff; border: 1px solid #555;
    padding: 6px 8px; border-radius: 4px; selection-background-color: #0078d4;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #3c3c3c; color: #ffffff; border: 1px solid #555;
    selection-background-color: #0078d4; selection-color: #ffffff;
}
QPushButton {
    background-color: #3c3c3c; color: #e8e8e8; border: 1px solid #555;
    padding: 6px 12px; border-radius: 4px;
}
QPushButton:hover { background-color: #4a4a4a; color: #ffffff; }
QPushButton:disabled { background-color: #2d2d2d; color: #666; }
QSplitter::handle { background-color: #3c3c3c; }
QMenu { background-color: #2d2d2d; color: #e8e8e8; border: 1px solid #555; }
QMenu::item { padding: 6px 24px; }
QMenu::item:selected { background-color: #0078d4; color: #ffffff; }
""" + SCROLLBAR_STYLE + SCROLLBAR_DARK

APP_LIGHT_STYLE = """
QMainWindow { background: transparent; }
QWidget#shadowOuter { background: transparent; }
QFrame#mainFrame {
    background-color: #f3f3f3;
    border: none;
    border-radius: 0px;
}
QWidget { background-color: #f3f3f3; color: #1a1a1a; }
QLabel { color: #1a1a1a; background: transparent; }
QListWidget {
    background-color: #f6f6f6; border: none; outline: none; color: #1a1a1a;
}
QListWidget::item { padding: 12px 10px; border-bottom: 1px solid #e0e0e0; color: #1a1a1a; }
QListWidget::item:selected { background-color: #cce4f7; color: #000000; }
QListWidget::item:hover { background-color: #eeeeee; }
QLineEdit, QComboBox {
    background-color: #ffffff; color: #1a1a1a; border: 1px solid #ccc;
    padding: 6px 8px; border-radius: 4px; selection-background-color: #0078d4;
}
QComboBox::drop-down { border: none; width: 24px; }
QComboBox QAbstractItemView {
    background-color: #ffffff; color: #1a1a1a; border: 1px solid #ccc;
    selection-background-color: #0078d4; selection-color: #ffffff;
}
QPushButton {
    background-color: #e8e8e8; color: #1a1a1a; border: 1px solid #bbb;
    padding: 6px 12px; border-radius: 4px;
}
QPushButton:hover { background-color: #dddddd; color: #000000; }
QPushButton:disabled { background-color: #f0f0f0; color: #999; }
QSplitter::handle { background-color: #ddd; }
QMenu { background-color: #ffffff; color: #1a1a1a; border: 1px solid #ccc; }
QMenu::item { padding: 6px 24px; }
QMenu::item:selected { background-color: #0078d4; color: #ffffff; }
""" + SCROLLBAR_STYLE + SCROLLBAR_LIGHT

CURRENT_THEME = "light"
ACCOUNTS_TXT_NAME = "accounts.txt"

# 列表圆点：绿=在线活跃，黄=休眠，红=未登录/已卸载
# ==================== 配置常量 ====================
WINDOW_SHADOW_MARGIN = 14
WINDOW_FRAME_RADIUS = 16
# WebView2 原生 HWND 常比 Qt 布局宽/高出 1~2px；两主题统一内缩，仅底色随主题变
TEAMS_WEBVIEW_EDGE_INSET = 2
MAX_ACTIVE_WEBVIEWS = 0
MAX_SUSPENDED_WEBVIEWS = 0
# 账号运行档位：foreground=完整扫描；warm_notify=轻量通知保活；cold_unloaded=已卸载
RUNTIME_FOREGROUND = "foreground"
RUNTIME_WARM_NOTIFY = "warm_notify"
RUNTIME_COLD_UNLOADED = "cold_unloaded"
WARM_TITLE_POLL_MS = 1200
WARM_CALL_DETECT_POLL_MS = 300
MEMORY_GUARD_INTERVAL_SEC = 45
# 底线：20 个账号都保持活着+连着收消息，不因内存压力卸载（卸载=点开重刷页面）。
# 仅在系统真的快 OOM（低于红线）时才应急卸载，避免整机崩。
MEMORY_PRESSURE_MIN_FREE_MB = 700
MEMORY_PRESSURE_SUSPENDED_LIMIT = 40
MEMORY_LIGHT_PROBE_INTERVAL_SEC = 5
LOW_MEMORY_RED_MB = 600
# 自适应工作集回收（标准版：不卸载、不冻结、不重载；逐账号判断闲置+体积）
ADAPTIVE_RECYCLE_ACCOUNT_WS_MB = 250
ADAPTIVE_RECYCLE_IDLE_BASE_SEC = 480
ADAPTIVE_RECYCLE_IDLE_MIN_SEC = 90
ADAPTIVE_RECYCLE_IDLE_PER_ACCOUNT_SEC = 12
ADAPTIVE_RECYCLE_SWITCH_QUIET_SEC = 8
ADAPTIVE_RECYCLE_DECISION_MIN_SEC = 20
ADAPTIVE_RECYCLE_DECISION_MAX_SEC = 60
ADAPTIVE_RECYCLE_STEP_WAIT_SEC = 8
ADAPTIVE_RECYCLE_FREE_OK_MB = 2048
ADAPTIVE_RECYCLE_FREE_LIGHT_MB = 1200
ADAPTIVE_RECYCLE_FREE_MEDIUM_MB = 800
ADAPTIVE_RECYCLE_FREE_HEAVY_MB = 300
ADAPTIVE_RECYCLE_TARGET_BASE_MB = 800
ADAPTIVE_RECYCLE_TARGET_PER_ACCOUNT_MB = 430
ADAPTIVE_RECYCLE_ENABLE_WS_TRIM = True
ADAPTIVE_RECYCLE_LOADING_STORM_DELTA = 4
# 智能内存控制器：趋势采样 + 动态决策（非固定周期扫描）
MEMORY_CTRL_SAMPLE_WINDOW_SEC = 600
MEMORY_CTRL_TREND_WINDOW_SEC = 180
MEMORY_CTRL_TREND_MIN_SAMPLES = 4
MEMORY_CTRL_FREE_FALL_MB_PER_MIN = 80
MEMORY_CTRL_USED_RISE_MB_PER_MIN = 120
MEMORY_CTRL_CRITICAL_IDLE_SEC = 15
MEMORY_CTRL_HEAVY_IDLE_SEC = 50
MEMORY_CTRL_MEDIUM_IDLE_SEC = 120
MEMORY_CTRL_SCHED_MIN_SEC = 5
MEMORY_CTRL_SCHED_MAX_SEC = 120
MEMORY_CTRL_RECYCLE_EFFECTIVE_MB = 80
# 内存整理（静默）：停车区脉冲 Normal→Low，不切前台、不闪屏
MEMORY_GROOM_ENABLE = True
MEMORY_GROOM_DWELL_MS = 250
MEMORY_GROOM_USER_QUIET_SEC = 60
MEMORY_GROOM_ACCOUNT_COOLDOWN_SEC = 180
MEMORY_GROOM_WS_TRIGGER_MB = 9500
MEMORY_GROOM_MAINTENANCE_INTERVAL_SEC = 150
MEMORY_GROOM_STEP_WAIT_SEC = 12
MEMORY_ENFORCE_LOW_MEM_MIN_SEC = 120
# 高级：极端 OOM 时允许自动卸载（默认关闭，标准版不卸载在线账号）
ENABLE_AUTO_UNLOAD_ON_OOM = False
AUTO_UNLOAD_OOM_FREE_MB = 200
AUTO_UNLOAD_OOM_SUSTAIN_SEC = 45
# 标准版底线：所有账号保持长连接=都能收消息；后台账号用 Low 内存档+轻量轮询省内存，
# 绝不 TrySuspend 冻结（冻结=断连接=收不到消息）。点开休眠账号瞬间显示，不重载。
ENABLE_BACKGROUND_FREEZE = False
NOTIFY_WAKER_INTERVAL_SEC = 4
NOTIFY_WAKER_DWELL_SEC = 2.5
NOTIFY_WAKER_WAVE_ALL = False
NOTIFICATION_CHECK_INTERVAL = 500
BADGE_FOREGROUND_POLL_MS = 400
BADGE_BACKGROUND_POLL_MS = 3000
BADGE_CHECKS_PER_TICK = 2
TITLE_BADGE_POLL_MS = BADGE_FOREGROUND_POLL_MS
REALTIME_SCAN_MS = 500
CHATLIST_SCAN_MS = 500
TOAST_SCAN_MS = 450
MUTE_ALL_POLL_MS = 3000
NOTIFY_SOUND_SUPPRESS_AFTER_SWITCH_SEC = 2.8
# 来电铃声：video.mp3 播完后重复，挂断立即停止
CALL_NOTIFY_DURATION_SEC = 9.0
# 后台账号来电无 DOM 挂断信号，铃声最长响这么久后自动停（接近 Teams 振铃时长）
CALL_RING_MAX_DURATION_SEC = 40.0
CALL_DETECT_POLL_MS = 200
CALL_END_DEBOUNCE_MS = 900
AUTO_LOGIN_PASSWORD_ERROR_LIMIT = 3
# 启动后短暂建立未读基线，不阻塞消息提示音
NOTIFY_STARTUP_ARM_SEC = 0
NOTIFY_TITLE_SYNC_MIN_MS = 0
MSG_NOTIFY_DEDUP_MAX = 600
MSG_NOTIFY_DEDUP_TTL_SEC = 2.5
# Teams Notification API 事件去重（用 options.tag，比 DOM 扫描稳定）
NOTIFY_API_DEDUP_TTL_SEC = 120.0
# 分级内存：最近 N 个账号保持 Normal；更久未用的账号压到 Low + 停重扫描
MEMORY_TIER_HOT_COUNT = 8
MEMORY_TIER_IDLE_SEC = 600
MEMORY_RENDERER_TRIM_INTERVAL_SEC = 300
LOCK_UNLOAD_INTERVAL_MS = 200
TEAMS_NOTIFY_OFFICIAL_BASENAME = "teams_notify_official.mp3"
TEAMS_CALL_NOTIFY_BASENAME = "video.mp3"
TEAMS_NOTIFY_AUDIO_DIR = "audio"
MEMORY_CLEAN_INTERVAL = 300
TEAMS_HEALTH_CHECK_INTERVAL_SEC = 120
CLOSE_ACTION_SETTING_KEY = "close_action"
TEAMS_HEALTH_RELOAD_COOLDOWN_SEC = 300
TEAMS_ENGINE_RECOVER_COOLDOWN_SEC = 600
PROFILE_HTTP_CACHE_MAX_BYTES = 48 * 1024 * 1024
SIDEBAR_SMALL_BTN_W = 52
SIDEBAR_SMALL_BTN_H = 26
SIDEBAR_DEFAULT_WIDTH = 270
SIDEBAR_COLLAPSE_AT = 24
SIDEBAR_EXPAND_AT = 56
SIDEBAR_EXPAND_STRIP_W = 10
GROUP_SIDEBAR_ANIM_MS = 220
DAILY_CACHE_CLEAN_HOUR = 7
LOGIN_TIMEOUT_SEC = 300
LOGIN_VERIFY_MIN_SEC = 0
LOGIN_VERIFY_REQUIRED_HITS = 2
MAX_IMPORT_FILE_SIZE = 10 * 1024 * 1024

PROFILE_CACHE_DIRS = [
    "Cache", "Code Cache", "GPUCache", "DawnCache", "DawnGraphiteCache",
    "DawnWebGPUCache", "GrShaderCache", "ShaderCache", "GraphiteDawnCache",
    "Service Worker/CacheStorage", "Service Worker/ScriptCache",
    "blob_storage", "Media Cache", "VideoDecodeStats",
    "optimization_guide_model_store", "component_crx_cache",
    "extensions_crx_cache", "BrowserMetrics", "Crashpad",
    "hyphen-data", "Safe Browsing",
    # WebView2 / Edge 可安全删除的附加缓存（不动 Cookies / Local Storage / IndexedDB）
    "Download Service", "Shared Dictionary", "Network Action Predictor",
    "Favicons", "Top Sites", "Visited Links", "JumpListIconsRecentClosed",
    "WebAssistDatabase", "AutofillAiModelCache", "BudgetDatabase",
    "EdgeEDrop", "EntityExtraction", "Nurturing",
    "Platform Notifications", "Notification Resources", "Notification State",
    "SharedStorage", "History",
]

def _bridge_connect_js_source() -> str:
    """QWebChannel 桥接（须在 MainWorld，与 qt.webChannelTransport 同域）"""
    return """
    window.connectTeamsBridge = function connectTeamsBridge() {
        if (typeof qt === 'undefined' || !qt.webChannelTransport) {
            setTimeout(connectTeamsBridge, 100);
            return;
        }
        if (typeof QWebChannel === 'undefined') {
            setTimeout(connectTeamsBridge, 150);
            return;
        }
        if (window.__teamsBridgeReady) return;
        new QWebChannel(qt.webChannelTransport, function(channel) {
            var bridge = channel.objects.notifyBridge;
            if (!bridge) {
                setTimeout(connectTeamsBridge, 200);
                return;
            }
            window.__teamsBridgeReady = true;
            window.__externalNotificationCallback = function(type, sender, content, count) {
                // 通知关闭时：仍同步角标；来电/挂断始终上报（由 Python 决定是否响铃弹窗）
                const t = String(type || 'unread');
                const always = (
                    t === 'unread' || t === 'incoming_call' || t === 'incoming_video'
                    || t === 'call_end'
                );
                if (window.__TEAMS_NOTIFICATIONS_OFF && !always) return;
                try {
                    bridge.post(String(type||'unread'), String(sender||''),
                        String(content!=null?content:''), parseInt(count,10)||0);
                } catch(e) {}
            };
            window.__teamsCopyImageToClipboard = function(dataUrl) {
                try { bridge.copyImageDataUrl(String(dataUrl)); } catch(e) {}
            };
            window.__teamsCopyImageUrl = function(url) {
                try { bridge.copyImageUrl(String(url)); } catch(e) {}
            };
            window.__teamsCacheNotifySoundUrl = function(url) {
                try { bridge.cacheNotifySoundUrl(String(url || '')); } catch(e) {}
            };
            if (window.__teamsSyncBadgeFromTitle) window.__teamsSyncBadgeFromTitle();
        });
    };
    window.connectTeamsBridge();
    """


class AppPaths:
    """数据目录：优先 D:\\TeamsX；无 D 盘时回退到 %LOCALAPPDATA%\\TeamsX。可用 TEAMSX_DATA_ROOT 覆盖。"""

    try:
        from starsailx.config import DATA_ROOT as DATA_ROOT
    except ImportError:
        DATA_ROOT = _TEAMS_DATA_ROOT_EARLY

    @classmethod
    def data_root(cls) -> str:
        try:
            os.makedirs(cls.DATA_ROOT, exist_ok=True)
        except Exception as e:
            raise RuntimeError(f"无法创建数据目录 {cls.DATA_ROOT}: {e}")
        return cls.DATA_ROOT

    @classmethod
    def db_dir(cls) -> str:
        path = os.path.join(cls.data_root(), "db")
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def db_file(cls) -> str:
        return os.path.join(cls.db_dir(), "starsail_accounts.db")

    @classmethod
    def _app_resource_bases(cls) -> List[str]:
        """源码：脚本目录；打包：exe 旁优先，其次 _MEIPASS。"""
        bases: List[str] = []
        if getattr(sys, "frozen", False):
            bases.append(os.path.dirname(os.path.abspath(sys.executable)))
            meipass = getattr(sys, "_MEIPASS", None)
            if meipass:
                bases.append(meipass)
        else:
            bases.append(os.path.dirname(os.path.abspath(__file__)))
        return bases

    @classmethod
    def teams_notify_official(cls) -> str:
        rel = os.path.join(TEAMS_NOTIFY_AUDIO_DIR, TEAMS_NOTIFY_OFFICIAL_BASENAME)
        for base in cls._app_resource_bases():
            path = os.path.join(base, rel)
            if os.path.isfile(path):
                return path
        return os.path.join(cls._app_resource_bases()[0], rel)

    @classmethod
    def teams_call_notify(cls) -> str:
        rel = os.path.join(TEAMS_NOTIFY_AUDIO_DIR, TEAMS_CALL_NOTIFY_BASENAME)
        for base in cls._app_resource_bases():
            path = os.path.join(base, rel)
            if os.path.isfile(path):
                return path
        return os.path.join(cls._app_resource_bases()[0], rel)

    @classmethod
    def app_icon(cls) -> str:
        for base in cls._app_resource_bases():
            path = os.path.join(base, "logo.ico")
            if os.path.isfile(path):
                return path
        return ""

    @classmethod
    def app_qicon(cls) -> QIcon:
        """应用图标：logo.ico → 打包 exe 内嵌图标 → 空。"""
        path = cls.app_icon()
        if path:
            icon = QIcon(path)
            if not icon.isNull():
                return icon
        if getattr(sys, "frozen", False):
            exe_icon = QIcon(os.path.abspath(sys.executable))
            if not exe_icon.isNull():
                return exe_icon
        return QIcon()

    @classmethod
    def profiles_root(cls) -> str:
        path = os.path.join(cls.data_root(), "profiles")
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def cache_root(cls) -> str:
        path = os.path.join(cls.data_root(), "cache")
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def accounts_txt(cls) -> str:
        return os.path.join(cls.data_root(), ACCOUNTS_TXT_NAME)

    @classmethod
    def shared_webview2_user_data(cls) -> str:
        """所有账号共享的 WebView2 UserDataFolder（多 Profile 单浏览器进程）。"""
        path = os.path.join(cls.profiles_root(), "_shared_webview2")
        os.makedirs(path, exist_ok=True)
        return path

    @classmethod
    def account_dirs(cls, remark: str, account_id: int) -> Tuple[str, str]:
        # 路径仅按账号 ID，改备注不会换目录、不会丢登录态
        folder = f"account_{account_id}"
        session_dir = os.path.join(cls.profiles_root(), folder, "session")
        cache_dir = os.path.join(cls.cache_root(), folder)
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(cache_dir, exist_ok=True)
        return session_dir, cache_dir


def _dir_size(path: str) -> int:
    total = 0
    try:
        for root, _dirs, files in os.walk(path):
            for f in files:
                fp = os.path.join(root, f)
                try:
                    total += os.path.getsize(fp)
                except OSError:
                    pass
    except OSError:
        pass
    return total


def format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    if n < 1024 * 1024:
        return f"{n / 1024:.1f} KB"
    return f"{n / 1024 / 1024:.1f} MB"


def clean_profile_cache(user_data_dir: str) -> Tuple[int, int]:
    """清理 session 目录内的浏览器缓存子目录，保留 Cookies 等登录数据。"""
    if not user_data_dir or not os.path.isdir(user_data_dir):
        return 0, 0
    removed = 0
    freed = 0
    for name in PROFILE_CACHE_DIRS:
        path = os.path.join(user_data_dir, name)
        if not os.path.exists(path):
            continue
        try:
            if os.path.isdir(path):
                freed += _dir_size(path)
                shutil.rmtree(path, ignore_errors=True)
            else:
                freed += os.path.getsize(path)
                os.remove(path)
            removed += 1
        except OSError as e:
            print(f"清理缓存跳过 {path}: {e}")
    return removed, freed


def clear_account_cache_dir(cache_dir: str) -> int:
    """删除并重建独立 cache 目录，返回约释放字节数。"""
    if not cache_dir:
        return 0
    freed = 0
    if os.path.isdir(cache_dir):
        freed = _dir_size(cache_dir)
        shutil.rmtree(cache_dir, ignore_errors=True)
    os.makedirs(cache_dir, exist_ok=True)
    return freed


def clean_orphan_cache_dirs(valid_cache_dirs: Set[str]) -> int:
    """删除 cache 根目录下已无账号引用的孤立文件夹。"""
    cache_root = os.path.normpath(AppPaths.cache_root())
    freed = 0
    if not os.path.isdir(cache_root):
        return 0
    try:
        for name in os.listdir(cache_root):
            path = os.path.normpath(os.path.join(cache_root, name))
            if path in valid_cache_dirs:
                continue
            if os.path.isdir(path):
                freed += _dir_size(path)
                shutil.rmtree(path, ignore_errors=True)
    except OSError as e:
        print(f"清理孤立缓存目录错误: {e}")
    return freed


class CacheCleanWorker(QObject):
    """后台清理缓存，避免阻塞 UI"""

    finished = pyqtSignal(str, int)
    failed = pyqtSignal(str)

    def __init__(
        self,
        accounts: List[Tuple],
        cache_root: str,
        skip_session_dirs: Optional[Set[str]] = None,
        skip_cache_dirs: Optional[Set[str]] = None,
    ):
        super().__init__()
        self._accounts = accounts
        self._cache_root = os.path.normpath(cache_root)
        self._valid_cache_dirs: Set[str] = set()
        self._skip_session_dirs = skip_session_dirs or set()
        self._skip_cache_dirs = skip_cache_dirs or set()

    def run(self):
        total_freed = 0
        count = 0
        try:
            for acc in self._accounts:
                session_dir = acc[2] if len(acc) > 2 else None
                cache_dir = acc[3] if len(acc) > 3 else None
                acc_freed = 0
                if cache_dir:
                    normalized = os.path.normpath(os.path.abspath(cache_dir))
                    if normalized.startswith(self._cache_root):
                        self._valid_cache_dirs.add(normalized)
                        if normalized not in self._skip_cache_dirs:
                            acc_freed += clear_account_cache_dir(cache_dir)
                if session_dir:
                    norm_session = os.path.normpath(os.path.abspath(session_dir))
                    if norm_session not in self._skip_session_dirs:
                        _removed, freed = clean_profile_cache(session_dir)
                        acc_freed += freed
                if acc_freed > 0:
                    count += 1
                    total_freed += acc_freed
            total_freed += clean_orphan_cache_dirs(self._valid_cache_dirs)
            msg = (
                f"已清理 {count} 个账号的浏览器磁盘缓存，释放约 {format_bytes(total_freed)}。\n"
                f"登录态（Cookies / Local Storage）已保留，无需重新登录。"
            )
            self.finished.emit(msg, total_freed)
        except Exception as e:
            self.failed.emit(str(e))


def parse_account_blocks(text: str) -> List[Dict[str, str]]:
    """解析 B/Z/M 格式账号块。B=备注 Z=账号 M/N=密码，空行分隔多条。"""
    key_map = {
        "b": "remark", "z": "email", "m": "password", "n": "password",
        "备注": "remark", "账号": "email", "密码": "password",
        "remark": "remark", "email": "email", "password": "password",
    }
    accounts: List[Dict[str, str]] = []
    current: Dict[str, str] = {}

    def normalize_value(field: str, value: str) -> str:
        value = (value or "").strip()
        if field in ("email", "password"):
            # 导入文件里 Z/M 行常因复制粘贴混入半角/全角空格、制表符等，
            # 这些不应作为账号或密码的一部分参与登录。
            return re.sub(r"[\s\u00a0\u3000]+", "", value)
        return value

    def flush():
        nonlocal current
        if current.get("remark") or current.get("email"):
            accounts.append(dict(current))
        current = {}

    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            flush()
            continue
        parts = re.split(r"[:：]", line, maxsplit=1)
        if len(parts) < 2:
            continue
        key = parts[0].strip().lower()
        field = key_map.get(key) or key_map.get(parts[0].strip())
        val = normalize_value(field or "", parts[1])
        if field and val:
            current[field] = val
    flush()
    return accounts


def format_account_block(remark: str, email: str = "", password: str = "") -> str:
    """单条 B/Z/M 账号块（与导入格式一致）"""
    lines = [f"B：{remark.strip()}"]
    em = (email or "").strip()
    pw = (password or "").strip()
    if em:
        lines.append(f"Z：{em}")
    if pw:
        lines.append(f"M：{pw}")
    return "\n".join(lines)


_REMARK_SORT_FN = None


def _init_remark_sort_fn():
    """微信式排序：按备注首字拼音/字母分组（A-Z、0-9、#）"""
    global _REMARK_SORT_FN
    if _REMARK_SORT_FN is not None:
        return _REMARK_SORT_FN
    try:
        from pypinyin import Style, lazy_pinyin

        def _pinyin_key(text: str) -> str:
            letters = lazy_pinyin(text, style=Style.FIRST_LETTER)
            return "".join((x or "#").upper() for x in letters)

        _REMARK_SORT_FN = _pinyin_key
        return _REMARK_SORT_FN
    except ImportError:
        pass
    for loc in (
        "Chinese_China.65001",
        "Chinese_China.936",
        "Chinese (Simplified)_China.936",
        "zh_CN.UTF-8",
    ):
        try:
            locale.setlocale(locale.LC_COLLATE, loc)

            def _locale_key(text: str) -> str:
                return locale.strxfrm(text)

            _REMARK_SORT_FN = _locale_key
            return _REMARK_SORT_FN
        except locale.Error:
            continue
    _REMARK_SORT_FN = lambda text: text.lower()
    return _REMARK_SORT_FN


def remark_sort_key(remark: str) -> Tuple:
    """微信好友式：# → 数字 → A-Z（中文按拼音首字母，如 阿→A）"""
    s = (remark or "").strip()
    if s.startswith("📌"):
        s = s.lstrip("📌").strip()
    if not s:
        return (9, "", "")
    sort_fn = _init_remark_sort_fn()
    py = sort_fn(s)
    ch = s[0]
    if ch.isdigit():
        return (1, py, s)
    if ch.isascii() and ch.isalpha():
        return (0, ch.upper() + s.lower(), s.lower())
    if ch.isascii():
        return (2, py, s)
    return (0, py, s)


def read_accounts_txt_content() -> str:
    path = AppPaths.accounts_txt()
    if not os.path.isfile(path):
        return ""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError as e:
        print(f"读取账号备份文件失败: {e}")
        return ""


def write_accounts_txt_from_blocks(blocks: List[Dict[str, str]]):
    path = AppPaths.accounts_txt()
    parts = [
        format_account_block(
            b.get("remark", ""),
            b.get("email", ""),
            b.get("password", ""),
        )
        for b in blocks
        if (b.get("remark") or b.get("email"))
    ]
    text = ("\n\n".join(parts) + "\n") if parts else ""
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    except OSError as e:
        print(f"写入账号备份文件失败: {e}")


def upsert_account_in_accounts_txt(remark: str, email: str = "", password: str = ""):
    """将账号写入 D:\\TeamsX\\accounts.txt，便于换设备导入"""
    blocks = parse_account_blocks(read_accounts_txt_content())
    email_key = (email or "").strip().lower()
    remark_key = (remark or "").strip()
    new_block = {
        "remark": remark_key,
        "email": (email or "").strip(),
        "password": (password or "").strip(),
    }
    updated = False
    for i, b in enumerate(blocks):
        be = (b.get("email") or "").strip().lower()
        br = (b.get("remark") or "").strip()
        if email_key and be == email_key:
            blocks[i] = new_block
            updated = True
            break
        if not email_key and br == remark_key:
            blocks[i] = new_block
            updated = True
            break
    if not updated:
        blocks.append(new_block)
    write_accounts_txt_from_blocks(blocks)


def remove_account_from_accounts_txt(email: str = "", remark: str = ""):
    blocks = parse_account_blocks(read_accounts_txt_content())
    email_key = (email or "").strip().lower()
    remark_key = (remark or "").strip()
    kept = []
    for b in blocks:
        be = (b.get("email") or "").strip().lower()
        br = (b.get("remark") or "").strip()
        if email_key and be == email_key:
            continue
        if not email_key and remark_key and br == remark_key:
            continue
        kept.append(b)
    write_accounts_txt_from_blocks(kept)


# ==================== 工具类 ====================

class SafeDict(dict):
    """线程安全的字典"""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._lock = threading.Lock()

    def get(self, key, default=None):
        with self._lock:
            return super().get(key, default)

    def __setitem__(self, key, value):
        with self._lock:
            super().__setitem__(key, value)

    def __delitem__(self, key):
        with self._lock:
            super().__delitem__(key)

    def pop(self, key, *args):
        with self._lock:
            return super().pop(key, *args)

    def clear(self):
        with self._lock:
            super().clear()

class WebViewPool:
    """WebView 池管理器 - 控制活跃 WebView 数量"""
    def __init__(self):
        self.views: Dict[int, dict] = {}  # account_id -> {view, last_used, active, use_count}
        self._lock = threading.Lock()

    def get(self, account_id: int) -> Optional[dict]:
        """获取 WebView 信息"""
        with self._lock:
            return self.views.get(account_id)

    def register(self, account_id: int, web_view):
        """注册 WebView"""
        with self._lock:
            self.views[account_id] = {
                'view': web_view,
                'last_used': time.time(),
                'active': True,
                'use_count': int(self.views.get(account_id, {}).get("use_count", 0)),
            }

    def mark_used(self, account_id: int):
        """记录一次使用（LFU）并更新最后使用时间（LRU）"""
        with self._lock:
            if account_id in self.views:
                self.views[account_id]['last_used'] = time.time()
                self.views[account_id]['active'] = True
                self.views[account_id]['use_count'] = int(self.views[account_id].get("use_count", 0)) + 1

    def deactivate(self, account_id: int):
        """标记 WebView 为非活跃"""
        with self._lock:
            if account_id in self.views:
                self.views[account_id]['active'] = False

    def remove(self, account_id: int):
        """移除 WebView"""
        with self._lock:
            return self.views.pop(account_id, None)

    def get_lfu_lru_account(self, exclude: Optional[Set[int]] = None) -> Optional[int]:
        """最不常用账号（use_count 最少）；并列时取 last_used 最早（LRU）。"""
        exclude = exclude or set()
        with self._lock:
            candidates = []
            for acc_id, info in self.views.items():
                if acc_id in exclude:
                    continue
                use_count = int(info.get("use_count", 0))
                last_used = float(info.get("last_used", 0.0) or 0.0)
                candidates.append((use_count, last_used, acc_id))
            if not candidates:
                return None
            candidates.sort(key=lambda x: (x[0], x[1]))
            return candidates[0][2]

    def clear(self):
        """清空池"""
        with self._lock:
            self.views.clear()

# ==================== UI 组件 ====================

class AccountListDelegate(QStyledItemDelegate):
    """账号列表：备注 + 右侧红色未读角标"""

    BADGE_W = 22
    BADGE_H = 18

    def paint(self, painter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        rect = option.rect
        colors = list_delegate_colors()
        selected = bool(option.state & QStyle.StateFlag.State_Selected)
        hovered = bool(option.state & QStyle.StateFlag.State_MouseOver)
        pill = QRectF(rect).adjusted(6, 3, -6, -3)
        radius = 9.0
        if selected:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(colors["bg_sel"]))
            painter.drawRoundedRect(pill, radius, radius)
            border = colors.get("bg_sel_border")
            if border:
                pen = QPen(QColor(border))
                pen.setWidthF(1.2)
                painter.setPen(pen)
                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.drawRoundedRect(pill.adjusted(0.6, 0.6, -0.6, -0.6), radius, radius)
        elif hovered:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(colors["bg_hover"]))
            painter.drawRoundedRect(pill, radius, radius)

        count = int(index.data(BADGE_COUNT_ROLE) or 0)
        remark = index.data(REMARK_ROLE) or index.data(Qt.ItemDataRole.DisplayRole) or ""
        is_pinned = bool(index.data(PIN_ROLE))
        prefix = "📌 " if is_pinned else ""
        label = f"{prefix}{remark}"

        text_left = rect.left() + 10

        badge_reserve = self.BADGE_W + 16 if count > 0 else 8
        text_rect = QRect(text_left, rect.top(), rect.width() - text_left - badge_reserve, rect.height())
        painter.setPen(QColor(colors["text_sel"] if selected else colors["text"]))
        font = painter.font()
        font.setPointSize(10)
        painter.setFont(font)
        elided = painter.fontMetrics().elidedText(label, Qt.TextElideMode.ElideRight, text_rect.width())
        painter.drawText(text_rect, Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft, elided)

        if count > 0:
            badge_text = "99+" if count > 99 else str(count)
            fm = painter.fontMetrics()
            bw = max(self.BADGE_W, fm.horizontalAdvance(badge_text) + 12)
            bh = self.BADGE_H
            bx = rect.right() - bw - 10
            by = rect.top() + (rect.height() - bh) // 2
            badge_rect = QRect(bx, by, bw, bh)
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(BADGE_RED_HOVER if selected else BADGE_RED))
            painter.drawRoundedRect(badge_rect, bh // 2, bh // 2)
            painter.setPen(QColor("#ffffff"))
            font.setBold(True)
            font.setPointSize(9)
            painter.setFont(font)
            painter.drawText(badge_rect, Qt.AlignmentFlag.AlignCenter, badge_text)

        painter.restore()

    def sizeHint(self, option, index):
        return QSize(option.rect.width() if option.rect.width() > 0 else 200, 46)


class AccountListWidget(QListWidget):
    """账号列表（自动排序，不支持手动拖动）"""

    orderChanged = pyqtSignal()
    _WHEEL_ANGLE_TO_PX = 46.0 / 120.0  # 约一行高度 / 标准滚轮刻度
    _WHEEL_ANIM_MS = 150

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragDropMode(QAbstractItemView.DragDropMode.NoDragDrop)
        self.setDragEnabled(False)
        self.setDropIndicatorShown(False)
        self.setVerticalScrollMode(QAbstractItemView.ScrollMode.ScrollPerPixel)
        bar = self.verticalScrollBar()
        bar.setSingleStep(10)
        bar.setPageStep(180)
        self._block_order_signal = False
        self._press_pos: Optional[QPoint] = None
        self._drag_started = False
        self._wheel_anim: Optional[QPropertyAnimation] = None

    def _wheel_pixel_delta(self, event) -> float:
        pixel = event.pixelDelta().y()
        if pixel != 0:
            return -float(pixel)
        angle = event.angleDelta().y()
        if angle == 0:
            return 0.0
        return -float(angle) * self._WHEEL_ANGLE_TO_PX

    def _animate_scroll_by(self, delta: float) -> None:
        bar = self.verticalScrollBar()
        if self._wheel_anim is not None and self._wheel_anim.state() == QAbstractAnimation.State.Running:
            base = int(self._wheel_anim.endValue())
        else:
            base = bar.value()
        target = max(bar.minimum(), min(bar.maximum(), int(base + delta)))
        if target == bar.value():
            return
        if self._wheel_anim is None:
            self._wheel_anim = QPropertyAnimation(bar, b"value", self)
            self._wheel_anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._wheel_anim.stop()
        self._wheel_anim.setDuration(self._WHEEL_ANIM_MS)
        self._wheel_anim.setStartValue(bar.value())
        self._wheel_anim.setEndValue(target)
        self._wheel_anim.start()

    def wheelEvent(self, event):
        delta = self._wheel_pixel_delta(event)
        if delta == 0.0:
            event.ignore()
            return
        # 触控板 pixelDelta 本身已连续，直接跟手；鼠标滚轮刻度用缓动动画
        if event.pixelDelta().y() != 0:
            bar = self.verticalScrollBar()
            if self._wheel_anim is not None:
                self._wheel_anim.stop()
            bar.setValue(
                max(bar.minimum(), min(bar.maximum(), bar.value() + int(delta)))
            )
        else:
            self._animate_scroll_by(delta)
        event.accept()

    def mousePressEvent(self, event):
        self._press_pos = event.position().toPoint()
        self._drag_started = False
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        # 仅允许上下拖动排序：按住左键左右滑动不触发任何拖动/位移
        if event.buttons() & Qt.MouseButton.LeftButton and self._press_pos is not None:
            pos = event.position().toPoint()
            dx = abs(pos.x() - self._press_pos.x())
            dy = abs(pos.y() - self._press_pos.y())
            if not self._drag_started:
                # 横向优先则忽略（不触发 InternalMove）
                if dx > dy and dx >= QApplication.startDragDistance():
                    event.ignore()
                    return
                if dy >= QApplication.startDragDistance():
                    self._drag_started = True
        super().mouseMoveEvent(event)

    def dropEvent(self, event):
        super().dropEvent(event)
        if not self._block_order_signal:
            self.orderChanged.emit()


# ==================== WebView 类 ====================

_TEAMS_LOGIN_FAIL_REASONS = frozenset({
    "still_on_login", "login_form", "sign_in_ui", "welcome_heading", "passkey_ui",
    "auth_path", "login_title", "welcome_text", "unsupported_browser", "not_teams",
})

_TEAMS_SHELL_VERIFY_JS = STARSAIL_SHELL_VERIFY_JS

class TeamsWebView(QWidget):
    """Teams WebView — PyQt 壳 + WebView2（Windows）或 Qt WebEngine（回退）"""

    loginCompleted = pyqtSignal(int, bool, str)
    sessionLoggedIn = pyqtSignal(int)

    def __init__(
        self,
        account_id,
        session_dir,
        cache_dir,
        notification_callback=None,
        login_email=None,
        login_password=None,
        auto_login=False,
        image_helper=None,
        parent=None,
    ):
        super().__init__(parent)
        self.account_id = account_id
        self._image_helper = image_helper
        self.session_dir = session_dir
        self.cache_dir = cache_dir
        self.user_data_dir = session_dir
        self.notification_callback = notification_callback
        self.load_timeout_timer = None
        self.retry_count = 0
        self.max_retries = 3
        self.is_valid = True
        self.is_loading = False
        self._is_closing = False
        self._login_email = (login_email or "").strip()
        self._login_password = login_password or ""
        self._auto_login = auto_login and bool(self._login_email and self._login_password)
        self._login_active = False
        self._login_poll_count = 0
        self._login_max_polls = 90
        self._login_poll_timer = None
        self._login_timeout_timer = None
        self._login_verify_timer = None
        self._login_started_at = 0.0
        self._seen_login_host = False
        self._email_step_done = False
        self._login_verify_hits = 0
        self._login_password_error_hits = 0
        self._session_probe_hits = 0
        self._runtime_mode = RUNTIME_FOREGROUND
        self._core_suspended = False
        self._session_reported = False
        self._session_probe_timer = None
        self._host_main = None
        self._engine_kind = "webview2"
        self._page_adapter = None
        self._wv2_widget = None
        self._wv2_doc_scripts: List[str] = []
        self.profile = None
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.NoContextMenu)

        try:
            os.makedirs(session_dir, exist_ok=True)
            os.makedirs(cache_dir, exist_ok=True)
        except Exception as e:
            print(f"创建用户目录失败: {e}")
            self.is_valid = False
            return

        self._notify_bridge = JsNotifyBridge(
            account_id, notification_callback, self, image_helper, self
        )

        if not (_HAS_TEAMS_ENGINE and use_webview2()):
            self.is_valid = False
            raise RuntimeError(
                "WebView2 引擎不可用。请安装/检查: qtwebview2 + pythonnet + pywin32，"
                "并确保 Python 与 WebView2 运行时位数一致（通常 x64）。"
            )
        if not self._init_webview2_engine():
            self.is_valid = False
            raise RuntimeError("WebView2 引擎初始化失败（已禁用 QtWebEngine 回退）。")

        if not self.is_valid:
            return

        self._offline_timer = QTimer(self)
        self._offline_timer.timeout.connect(self._check_offline_and_reconnect)
        self._offline_timer.start(45000)
        self._offline_retry_count = 0
        self._blank_health_suspect_count = 0
        self._suspended_at = 0.0
        self._last_ok_load_at = 0.0
        self._last_health_reload_at = 0.0
        self._health_timer = QTimer(self)
        self._health_timer.timeout.connect(self._check_page_health)
        self._health_timer.start(TEAMS_HEALTH_CHECK_INTERVAL_SEC * 1000)

        # load_teams 在 WebView2 is_ready 后由 _on_wv2_engine_ready 触发

    def _on_wv2_engine_ready(self, success: bool, error_message: str = ""):
        """WebView2 异步初始化完成；失败则直接报错（无回退）。"""
        if success:
            QTimer.singleShot(100, self.load_teams)
            return
        msg = f"账号 {self.account_id} WebView2 初始化失败"
        if error_message:
            msg += f": {error_message}"
        print(msg)
        self.is_valid = False

    def _init_webview2_engine(self) -> bool:
        try:
            os.environ.setdefault("QT_API", "pyqt6")
            from qtwebview2 import DictJsBridge

            apply_webview2_runtime_env()
            print("[WebView2] User-Agent 使用 WebView2 原生（不覆盖）")

            self._engine_kind = "webview2"
            self._wv2_doc_scripts = []
            self._inject_persistent_scripts()
            self._inject_bridge_connect_script()
            self._inject_login_page_scripts()

            js_bridge = DictJsBridge()
            nb = self._notify_bridge
            js_bridge.bind_js_api_func(nb.post, name="post")
            js_bridge.bind_js_api_func(nb.copyImageDataUrl, name="copyImageDataUrl")
            js_bridge.bind_js_api_func(nb.copyImageUrl, name="copyImageUrl")
            js_bridge.bind_js_api_func(nb.cacheNotifySoundUrl, name="cacheNotifySoundUrl")

            self._wv2_widget, self._page_adapter = create_webview2_widget(
                parent=self,
                session_dir=self.session_dir,
                account_id=self.account_id,
                shared_user_data_folder=AppPaths.shared_webview2_user_data(),
                user_agent="",
                js_bridge=js_bridge,
                doc_scripts=list(self._wv2_doc_scripts),
                on_navigation_completed=self._on_wv2_navigation_completed,
                on_url_changed=self._on_url_changed,
            )
            self._layout.addWidget(self._wv2_widget, 1)
            try:
                self._wv2_widget.bridge.domContentLoaded.connect(
                    lambda: self._schedule_session_check(1500)
                )
            except Exception:
                pass
            try:
                self._wv2_widget.bridge.initialization_done.connect(
                    self._on_wv2_engine_ready
                )
            except Exception:
                pass
            print(f"账号 {self.account_id} 使用 WebView2（{self.session_dir}）")
            return True
        except Exception as e:
            print(f"WebView2 引擎创建失败: {e}")
            self._wv2_widget = None
            self._page_adapter = None
            return False

    def _on_wv2_navigation_completed(self, ok: bool):
        self.on_load_finished(bool(ok))

    def page(self):
        return self._page_adapter

    def load(self, url: QUrl):
        u = url.toString() if isinstance(url, QUrl) else str(url)
        if self._wv2_widget:
            self._wv2_widget.load_url(u)
            if self._page_adapter:
                self._page_adapter.set_current_url(QUrl(u))

    def stop(self):
        if self._wv2_widget and self._wv2_widget.is_ready:
            try:
                self._wv2_widget._webview.CoreWebView2.Stop()
            except Exception:
                pass

    def setPage(self, page):
        # WebView2-only：不支持外部 setPage
        return

    def _on_feature_permission(self, origin, feature):
        # WebView2-only：权限由 WebView2 侧处理
        return

    def _on_js_console_message(self, level, message, line_number, source_id):
        text = (message or "").strip()
        if not text:
            return
        low = text.lower()
        if any(
            k in low
            for k in (
                "playback",
                "widevine",
                "drm",
                "eme",
                "media",
                "encrypted",
                "cdm",
            )
        ):
            print(f"[Teams/{self.account_id}] js[{level}]: {text} ({source_id}:{line_number})")

    def hard_reload_teams(self):
        """强制恢复 Teams 页（绕过僵死渲染/缓存导致的白屏）。"""
        if not self.is_valid or self._is_closing:
            return
        self.is_loading = False
        if self.load_timeout_timer:
            self.load_timeout_timer.stop()
            self.load_timeout_timer.deleteLater()
            self.load_timeout_timer = None
        url = ""
        try:
            if self.page():
                url = self.page().url().toString()
        except Exception:
            url = ""
        if url and self._is_teams_app_url(url):
            try:
                self.is_loading = True
                if self._wv2_widget and getattr(self._wv2_widget, "is_ready", False):
                    self._wv2_widget.reload()
                else:
                    raise RuntimeError("WebView2 未就绪")
                self.load_timeout_timer = QTimer(self)
                self.load_timeout_timer.setSingleShot(True)
                self.load_timeout_timer.timeout.connect(self.on_load_timeout)
                self.load_timeout_timer.start(30000)
                print(f"账号 {self.account_id} 强制刷新 Teams（绕过缓存）")
                return
            except Exception as e:
                print(f"账号 {self.account_id} 强制刷新失败，改为重新加载: {e}")
        self.load_teams()

    def load_teams(self):
        """加载 Teams 页面"""
        if not self.is_valid:
            return

        if self.load_timeout_timer:
            try:
                self.load_timeout_timer.stop()
            except RuntimeError:
                pass
            try:
                self.load_timeout_timer.deleteLater()
            except RuntimeError:
                pass
            self.load_timeout_timer = None

        self.is_loading = True
        teams_url = STARSAIL_APP_URL

        # 注意：WebView2 导航完成可能非常快（甚至同步触发回调），
        # 必须先创建/绑定 timeout timer，避免回调里 stop 到旧的 deleteLater timer。
        t = QTimer(self)
        t.setSingleShot(True)
        t.timeout.connect(self.on_load_timeout)
        self.load_timeout_timer = t
        t.start(30000)

        self.load(QUrl(teams_url))

    def on_load_finished(self, ok):
        """页面加载完成回调"""
        if self.load_timeout_timer:
            try:
                self.load_timeout_timer.stop()
            except RuntimeError:
                pass
            self.load_timeout_timer = None

        self.is_loading = False

        if ok:
            self._last_ok_load_at = time.time()
            self.retry_count = 0
            self._offline_retry_count = 0
            self._blank_health_suspect_count = 0
            host = getattr(self, "_host_main", None)
            if host is not None and hasattr(host, "clear_teams_load_failures"):
                host.clear_teams_load_failures()
            QTimer.singleShot(2000, self.setup_callbacks)
            if self._auto_login and not self._login_active:
                QTimer.singleShot(1500, self._maybe_start_auto_login)
            self._schedule_session_check(800)
            self._start_session_probe_timer()
            # 页面就绪后补设内存档：后台加载时档位虽已是 warm，
            # 但当时 WebView2 未就绪，Low 内存目标没设上，必须在此重设一次。
            QTimer.singleShot(1500, self._reapply_runtime_memory_profile)
            QTimer.singleShot(5000, self._reapply_runtime_memory_profile)
            QTimer.singleShot(15000, self._reapply_runtime_memory_profile)
        else:
            print(f"账号 {self.account_id} 页面加载失败")
            host = getattr(self, "_host_main", None)
            if host is not None and hasattr(host, "register_teams_load_failure"):
                host.register_teams_load_failure(self.account_id)
            if self._auto_login:
                self._finish_login(False, "页面加载失败")

    def on_load_timeout(self):
        """加载超时处理"""
        self.is_loading = False
        self.retry_count += 1
        if self.retry_count <= self.max_retries:
            print(f"账号 {self.account_id} 加载超时，第{self.retry_count}次重试...")
            QTimer.singleShot(1000, self.load_teams)
        else:
            print(f"账号 {self.account_id} 加载超时，已达最大重试次数")
            self.load_timeout_timer = None
            host = getattr(self, "_host_main", None)
            if host is not None and hasattr(host, "register_teams_load_failure"):
                host.register_teams_load_failure(self.account_id)

    def _check_page_health(self):
        """检测 Teams 白屏/空壳页，自动恢复（长时间挂着不动时常见）。"""
        if self._is_closing or not self.is_valid or not self.page():
            return
        if self.is_loading or self._login_active or not self.isVisible():
            return
        if self._last_ok_load_at and (time.time() - self._last_ok_load_at) < 120:
            return
        if self._last_health_reload_at and (
            time.time() - self._last_health_reload_at
        ) < TEAMS_HEALTH_RELOAD_COOLDOWN_SEC:
            return
        url = self.page().url().toString()
        if not self._is_teams_app_url(url):
            return
        js = r"""
        (function() {
            try {
                const u = (location.href || '').toLowerCase();
                if (!u.includes('starsail.vip')) return false;
                if (document.querySelector('.login-panel')) return false;
                const chat = document.querySelector('.chat-layout');
                if (chat) {
                    const t = (chat.innerText || '').trim();
                    if (t.length > 40) return false;
                }
                const body = (document.body && document.body.innerText || '').trim();
                return body.length < 30;
            } catch (e) {
                return false;
            }
        })();
        """

        def on_blank(is_blank):
            if self._is_closing or not self.is_valid:
                return
            if not is_blank:
                self._blank_health_suspect_count = 0
                return
            self._blank_health_suspect_count += 1
            if self._blank_health_suspect_count < 2:
                print(f"账号 {self.account_id} 疑似 Teams 白屏，等待二次确认…")
                return
            self._blank_health_suspect_count = 0
            self._last_health_reload_at = time.time()
            host = getattr(self, "_host_main", None)
            if host is not None and hasattr(host, "request_teams_recovery"):
                host.request_teams_recovery(f"账号 {self.account_id} 白屏")
                return
            print(f"账号 {self.account_id} 检测到 Teams 白屏，自动恢复…")
            QTimer.singleShot(300, self.hard_reload_teams)

        self.page().runJavaScript(js, on_blank)

    def _verify_resume_health(self) -> None:
        """休眠恢复后轻量健康确认：仅白屏/异常 URL 才 reload。"""
        if self._is_closing or not self.is_valid or not self.page():
            return
        if self.is_loading or self._login_active:
            return
        url = self.page().url().toString()
        if self._is_login_host_url(url):
            return
        if not self._is_teams_app_url(url):
            print(f"账号 {self.account_id} 恢复后 URL 异常，尝试重载…")
            QTimer.singleShot(300, self.hard_reload_teams)
            return
        js = r"""
        (function() {
            try {
                const u = (location.href || '').toLowerCase();
                if (!u.includes('starsail.vip')) return false;
                if (document.querySelector('.login-panel')) return false;
                const chat = document.querySelector('.chat-layout');
                if (chat) {
                    const t = (chat.innerText || '').trim();
                    if (t.length > 40) return false;
                }
                const body = (document.body && document.body.innerText || '').trim();
                return body.length < 30;
            } catch (e) {
                return false;
            }
        })();
        """

        def on_blank(is_blank):
            if self._is_closing or not self.is_valid:
                return
            if not is_blank:
                return
            print(f"账号 {self.account_id} 恢复后检测到白屏，尝试重载…")
            QTimer.singleShot(300, self.hard_reload_teams)

        self.page().runJavaScript(js, on_blank)

    @property
    def is_closing(self):
        return self._is_closing or not self.is_valid

    @staticmethod
    def _is_login_host_url(url: str) -> bool:
        return False

    @staticmethod
    def _is_teams_app_url(url: str) -> bool:
        u = (url or "").lower()
        return "starsail.vip" in u

    def _webview2_ready(self) -> bool:
        if self._engine_kind != "webview2":
            return True
        w = getattr(self, "_wv2_widget", None)
        return bool(w and getattr(w, "is_ready", False))

    def _schedule_session_check(self, delay_ms: int = 800, retries: int = 0):
        """WebView2 须等 is_ready 后再跑 JS 检测，否则永远标红。"""
        if self._session_reported or self._is_closing:
            return

        def _run():
            if self._session_reported or self._is_closing:
                return
            if not self._webview2_ready():
                if retries < 48:
                    QTimer.singleShot(300, lambda: self._schedule_session_check(0, retries + 1))
                return
            self._check_session_now()

        if delay_ms > 0:
            QTimer.singleShot(delay_ms, _run)
        else:
            _run()

    def _invalidate_live_session(self, db_status: str = "pending"):
        """登录页/检测失败：清除本页 live 状态并标红。"""
        self._session_reported = False
        self._session_probe_hits = 0
        host = getattr(self, "_host_main", None)
        if host is not None and hasattr(host, "mark_account_not_logged_in"):
            try:
                host.mark_account_not_logged_in(int(self.account_id), db_status)
            except Exception:
                pass

    def _on_url_changed(self, url: QUrl):
        if self._is_closing or not self.page():
            return
        u = url.toString()
        if self._is_login_host_url(u):
            self._seen_login_host = True
            self._invalidate_live_session("pending")
            if self._auto_login and not self._login_active:
                QTimer.singleShot(800, self._maybe_start_auto_login)
        if self._is_teams_app_url(u):
            self._schedule_session_check(400)
            self._start_session_probe_timer()
            if self._login_active:
                self._schedule_login_verify()

    def _maybe_start_auto_login(self):
        if self._is_closing or not self._auto_login or self._login_active:
            return
        if not self.page():
            return
        url = self.page().url().toString()
        if self._is_login_host_url(url) or self._is_teams_app_url(url):
            self.start_auto_login()

    def start_auto_login(self):
        if not self._login_email or not self._login_password or not self.page():
            self._finish_login(False, "缺少账号或密码")
            return
        if self._login_active:
            return
        self._login_active = True
        self._session_reported = False
        self._seen_login_host = False
        self._login_started_at = time.time()
        self._login_verify_hits = 0
        self._login_password_error_hits = 0
        self._email_step_done = False
        if self._login_timeout_timer:
            self._login_timeout_timer.stop()
        self._login_timeout_timer = QTimer(self)
        self._login_timeout_timer.setSingleShot(True)
        self._login_timeout_timer.timeout.connect(
            lambda: self._finish_login(False, "登录超时")
        )
        self._login_timeout_timer.start(LOGIN_TIMEOUT_SEC * 1000)
        if self._login_poll_timer:
            self._login_poll_timer.stop()
        self._login_poll_timer = QTimer(self)
        self._login_poll_timer.timeout.connect(self._run_login_script)
        self._login_poll_timer.start(2000)
        self._inject_login_helpers_runtime()
        self._run_login_script()

    def _inject_login_helpers_runtime(self):
        if not self.page() or self._is_closing:
            return
        self.page().runJavaScript(
            """
            (function() {
                if (window.__teamsLoginHelpersRuntime) return;
                window.__teamsLoginHelpersRuntime = true;
                try {
                    if (navigator.credentials) {
                        const deny = () => Promise.reject(new DOMException('blocked', 'NotAllowedError'));
                        navigator.credentials.get = deny;
                        navigator.credentials.create = deny;
                    }
                } catch (e) {}
                try {
                    const rememberPassword = (el) => {
                        const v = (el && el.value || '').trim();
                        if (v) window.__teamsxLastPasswordInput = v;
                    };
                    const bindPasswordInput = () => {
                        document.querySelectorAll(
                            'input[type="password"], input[name="passwd"], #i0118, #passwordInput'
                        ).forEach(el => {
                            if (el.__teamsxPasswordCapture) return;
                            el.__teamsxPasswordCapture = true;
                            el.addEventListener('input', () => rememberPassword(el), true);
                            el.addEventListener('change', () => rememberPassword(el), true);
                        });
                    };
                    bindPasswordInput();
                    new MutationObserver(bindPasswordInput).observe(
                        document.documentElement || document.body,
                        {childList: true, subtree: true}
                    );
                } catch (e) {}
            })();
            """
        )

    def _schedule_login_verify(self):
        if not self._login_active or self._is_closing:
            return
        if self._login_verify_timer:
            self._login_verify_timer.stop()
        self._login_verify_timer = QTimer(self)
        self._login_verify_timer.setSingleShot(True)
        self._login_verify_timer.timeout.connect(self._verify_login_state)
        self._login_verify_timer.start(2000)

    def _start_session_probe_timer(self):
        if self._session_reported or self._is_closing:
            return
        if self._session_probe_timer is None:
            self._session_probe_timer = QTimer(self)
            self._session_probe_timer.timeout.connect(self._probe_teams_session)
        if not self._session_probe_timer.isActive():
            self._session_probe_timer.start(1500)

    def _stop_session_probe_timer(self):
        if self._session_probe_timer:
            self._session_probe_timer.stop()

    def _emit_session_logged_in_once(self):
        if self._session_reported or self._is_closing:
            return
        self._session_reported = True
        self._stop_session_probe_timer()
        host = getattr(self, "_host_main", None)
        if host is not None and hasattr(host, "mark_account_logged_in"):
            try:
                host.mark_account_logged_in(int(self.account_id))
                print(f"账号 {self.account_id} 已标记为登录成功（绿/黄点）")
            except Exception as e:
                print(f"主窗口标记登录失败: {e}")
        self.sessionLoggedIn.emit(int(self.account_id))

    def _parse_verify_result(self, result) -> dict:
        try:
            if isinstance(result, str) and result.strip():
                parsed = json.loads(result)
                if isinstance(parsed, dict):
                    return parsed
            if isinstance(result, dict):
                if "ok" in result:
                    return result
                inner = result.get("result")
                if isinstance(inner, str) and inner.strip():
                    return json.loads(inner)
                if isinstance(inner, dict):
                    return inner
                return result
        except json.JSONDecodeError:
            pass
        return {}

    def _on_strict_login_check(self, result):
        """仅严格检测（Teams 主界面壳）通过才标绿，避免错号/登录页误判。"""
        if self._is_closing or self._session_reported:
            return
        data = self._parse_verify_result(result)
        if not data:
            if not self._login_active:
                QTimer.singleShot(1200, lambda: self._schedule_session_check(0))
            elif self._login_active:
                self._schedule_login_verify()
            return
        if not data.get("ok"):
            reason = str(data.get("reason", "?"))
            if reason in _TEAMS_LOGIN_FAIL_REASONS:
                self._invalidate_live_session("pending")
            if self._session_probe_hits == 0:
                print(f"账号 {self.account_id} 登录检测未通过: {reason}")
            if not self._login_active:
                self._session_probe_hits = 0
            elif self._login_active:
                self._schedule_login_verify()
            return
        self._session_probe_hits += 1
        if self._session_probe_hits < LOGIN_VERIFY_REQUIRED_HITS:
            QTimer.singleShot(400, lambda: self._schedule_session_check(0))
            return
        print(f"账号 {self.account_id} 登录检测通过 ({data.get('reason', 'ok')})")
        self._emit_session_logged_in_once()
        if self._login_active:
            self._finish_login(True, "登录成功")

    def _check_session_now(self):
        """严格检测是否已进入 Teams 主界面。"""
        if self._is_closing or not self.page() or self._session_reported:
            return
        if self.is_loading:
            QTimer.singleShot(500, lambda: self._schedule_session_check(0))
            return
        if not self._is_teams_app_url(self.page().url().toString()):
            return
        if not self._webview2_ready():
            QTimer.singleShot(400, lambda: self._schedule_session_check(0))
            return
        self.page().runJavaScript(_TEAMS_SHELL_VERIFY_JS, self._on_strict_login_check)

    def _probe_teams_session(self):
        if self._is_closing or not self.page() or self._session_reported:
            return
        if not self._is_teams_app_url(self.page().url().toString()):
            return
        self._check_session_now()

    def _verify_login_state(self):
        if not self.page() or self._is_closing or self._session_reported:
            return
        if self._login_active:
            elapsed = time.time() - self._login_started_at
            if elapsed >= LOGIN_TIMEOUT_SEC - 5:
                return
        if not self._is_teams_app_url(self.page().url().toString()):
            if self._login_active:
                self._schedule_login_verify()
            return
        self._check_session_now()
        if self._login_active:
            self._schedule_login_verify()

    def _run_login_script(self):
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
        self.page().runJavaScript(js, self._on_login_script_result)

    def _on_login_script_result(self, result):
        if not self._login_active:
            return
        try:
            if isinstance(result, str) and result:
                data = json.loads(result)
            elif isinstance(result, dict):
                data = result
            else:
                data = {}
            step = data.get("step", "")
            if step in ("email", "email_next", "password"):
                self._email_step_done = True
            if step == "password_error":
                self._login_password_error_hits += 1
                if self._login_password_error_hits >= AUTO_LOGIN_PASSWORD_ERROR_LIMIT:
                    self._finish_login(False, "密码错误，已停止自动登录")
                    return
            elif step == "password":
                self._login_password_error_hits = 0
            if self._is_teams_app_url(self.page().url().toString()):
                self._schedule_login_verify()
        except json.JSONDecodeError:
            pass

    def _finish_login(self, ok: bool, message: str):
        if self._is_closing:
            return
        should_emit = self._login_active or self._auto_login
        self._login_active = False
        self._auto_login = False
        if self._login_poll_timer:
            self._login_poll_timer.stop()
            self._login_poll_timer = None
        if self._login_timeout_timer:
            self._login_timeout_timer.stop()
            self._login_timeout_timer = None
        if self._login_verify_timer:
            self._login_verify_timer.stop()
            self._login_verify_timer = None
        if not ok:
            self._session_reported = False
            self._stop_session_probe_timer()
            host = getattr(self, "_host_main", None)
            if host is not None and hasattr(host, "mark_account_not_logged_in"):
                try:
                    host.mark_account_not_logged_in(int(self.account_id), "failed")
                except Exception:
                    pass
        elif not self._session_reported:
            self._schedule_session_check(500)
            QTimer.singleShot(3500, lambda: self._schedule_session_check(0))
        if should_emit:
            self.loginCompleted.emit(self.account_id, ok, message)

    def setup_callbacks(self):
        if not self.is_valid or not self.page() or self._is_closing:
            return
        enabled = getattr(self, "_notifications_enabled", True)
        self.apply_notifications_enabled(enabled)
        QTimer.singleShot(300, self._ensure_web_channel_bridge)
        QTimer.singleShot(2000, self._ensure_web_channel_bridge)
        QTimer.singleShot(500, self._accelerate_background_sync)
        host = getattr(self, "_host_main", None)
        if host is not None and hasattr(host, "_sync_webview_lifecycle_states"):
            QTimer.singleShot(600, host._sync_webview_lifecycle_states)

    def _ensure_web_channel_bridge(self):
        """页面加载后于 MainWorld 重连桥接（复制/实时徽标依赖此通道）"""
        if not self.page() or self._is_closing:
            return
        if self._engine_kind == "webview2" and bridge_connect_js_webview2:
            js = bridge_connect_js_webview2(
                self.account_id, _bridge_connect_js_source()
            )
        else:
            js = f"window.__accountId = {self.account_id};" + _bridge_connect_js_source()
        self.page().runJavaScript(js)

    def _accelerate_background_sync(self):
        """已登录页：加快标题角标轮询并确保实时消息观察器就绪"""
        if not self.page() or self._is_closing:
            return
        fg = int(BADGE_FOREGROUND_POLL_MS)
        self.page().runJavaScript(
            f"""
            (function() {{
                try {{
                    if (window.__teams_title_poll_1) {{
                        clearInterval(window.__teams_title_poll_1);
                        window.__teams_title_poll_1 = null;
                    }}
                    if (typeof window.__teamsSyncBadgeFromTitle === 'function') {{
                        window.__teamsSyncBadgeFromTitle();
                        window.__teams_title_poll_1 = setInterval(
                            window.__teamsSyncBadgeFromTitle, {fg}
                        );
                    }}
                    window.__teamsxForeground = true;
                    if (typeof window.__teamsEnableRealtimeNotifications === 'function') {{
                        window.__teamsEnableRealtimeNotifications();
                    }}
                }} catch (e) {{}}
            }})();
            """
        )

    def _inject_bridge_connect_script(self):
        """Profile 级预注入桥接（MainWorld + DocumentReady）"""
        if not bridge_connect_js_webview2:
            raise RuntimeError("bridge_connect_js_webview2 未就绪（WebView2 引擎缺失）。")
        js_code = bridge_connect_js_webview2(self.account_id, _bridge_connect_js_source())
        self._wv2_doc_scripts.append(js_code)
        return

    def _check_offline_and_reconnect(self):
        if self._is_closing or not self.page() or self.is_loading:
            return
        if self._login_active:
            return
        # 刚登录/刚加载成功后的短时间内不要反复“重连”，避免影响正常使用。
        # 弱网下 Teams 自身会显示短暂连接横幅并自动恢复，过早重载会造成界面闪动。
        if self._last_ok_load_at and (time.time() - self._last_ok_load_at) < 120:
            return
        js = r"""
        (function() {
            if (!navigator.onLine) return true;
            // 只认“硬断网”信号。connectionBanner / connection problem 常见于弱网自愈，
            // 不应触发整页重载，否则会打断 Teams 自己的重连并造成闪动。
            const selectors = [
                '[data-tid*="offlineBanner" i]',
                '[data-tid*="noInternet" i]',
                '[aria-label*="无互联网" i]',
                '[aria-label*="No internet" i]'
            ];
            for (const sel of selectors) {
                try {
                    const el = document.querySelector(sel);
                    if (el) {
                        const r = el.getBoundingClientRect();
                        if (r.width > 0 && r.height > 0) return true;
                    }
                } catch (e) {}
            }
            return false;
        })();
        """
        def on_result(offline):
            if not offline or self._is_closing:
                self._offline_retry_count = 0
                return
            self._offline_retry_count += 1
            if self._offline_retry_count < 2:
                print(f"账号 {self.account_id} 疑似断线，等待二次确认…")
                return
            if self._offline_retry_count > 8:
                return
            if self._offline_retry_count % 2:
                return
            print(f"账号 {self.account_id} 检测到断线，自动重连 ({self._offline_retry_count})…")
            QTimer.singleShot(1200, self.load_teams)
        self.page().runJavaScript(js, on_result)

    def set_notification_callback(self, callback):
        self.notification_callback = callback
        if getattr(self, "_notify_bridge", None):
            self._notify_bridge.set_callback(callback)

    def apply_notifications_enabled(self, enabled: bool):
        if not self.page() or self._is_closing:
            return
        self._notifications_enabled = enabled
        flag = "false" if enabled else "true"
        self.page().runJavaScript(
            f"window.__TEAMS_NOTIFICATIONS_OFF = {flag};"
            "if(window.applyTeamsSoundPolicy)window.applyTeamsSoundPolicy();"
            "if(window.applyTeamsUiNotificationPolicy)window.applyTeamsUiNotificationPolicy();"
            "if(!window.__TEAMS_NOTIFICATIONS_OFF&&window.__teamsxForeground){"
            "document.querySelectorAll('audio').forEach(function(el){"
            "try{el.muted=false;if(el.volume===0)el.volume=1;}catch(e){}});}"
        )

    def set_window_drag_suspend(self, suspended: bool):
        """拖动/缩放时冻结 WebView 重绘（显示上一帧，不隐藏），避免原生 HWND 逐帧重排掉帧。"""
        if not self.is_valid or self._is_closing:
            return
        try:
            self.setUpdatesEnabled(not suspended)
            self.setAttribute(
                Qt.WidgetAttribute.WA_StaticContents, suspended
            )
            w2 = getattr(self, "_wv2_widget", None)
            if w2 is not None:
                w2.setUpdatesEnabled(not suspended)
        except Exception:
            pass

    def apply_runtime_mode(self, mode: str) -> None:
        """foreground / warm_notify / cold_unloaded 三档运行状态。"""
        if self._is_closing or not self.is_valid:
            return
        mode = (mode or RUNTIME_FOREGROUND).strip() or RUNTIME_FOREGROUND
        if mode == self._runtime_mode:
            return
        self._runtime_mode = mode
        if mode == RUNTIME_FOREGROUND:
            self.resume_page()
            self._set_background_timers_active(True)
            self.apply_memory_profile(True, keep_webview_normal=True)
            self._apply_runtime_js(RUNTIME_FOREGROUND)
            return
        if mode == RUNTIME_WARM_NOTIFY:
            self._set_background_timers_active(False)
            self.apply_memory_profile(False)
            self._apply_runtime_js(RUNTIME_WARM_NOTIFY)
            # 切到后台尽快冻结，释放渲染进程内存（恢复时不重载）。
            if ENABLE_BACKGROUND_FREEZE:
                QTimer.singleShot(600, self._suspend_if_background)
            return
        if mode == RUNTIME_COLD_UNLOADED:
            self._set_background_timers_active(False)
            self._apply_runtime_js(RUNTIME_COLD_UNLOADED)

    def suspend_page(self) -> bool:
        """真正冻结当前页（隐藏时调用），释放内存。恢复时不重载。"""
        if self._is_closing or not self.is_valid:
            return False
        w2 = getattr(self, "_wv2_widget", None)
        if w2 is None:
            return False
        try:
            from starsailx.engine.webview2 import suspend_core_webview2

            ok = suspend_core_webview2(w2)
            if ok:
                self._core_suspended = True
            return ok
        except Exception as e:
            print(f"[内存] 账号 {self.account_id} 冻结失败: {e}")
            return False

    def resume_page(self) -> bool:
        """恢复冻结页，不重载页面。"""
        if self._is_closing or not self.is_valid:
            return False
        w2 = getattr(self, "_wv2_widget", None)
        if w2 is None:
            return False
        try:
            from starsailx.engine.webview2 import resume_core_webview2

            ok = resume_core_webview2(w2)
            if ok:
                self._core_suspended = False
            return ok
        except Exception as e:
            print(f"[内存] 账号 {self.account_id} 恢复失败: {e}")
            return False

    def _suspend_if_background(self) -> None:
        """仅当启用后台冻结、且仍处于温态/隐藏时才冻结，避免误冻前台页。"""
        if not ENABLE_BACKGROUND_FREEZE:
            return
        if self._is_closing or not self.is_valid:
            return
        if getattr(self, "_runtime_mode", RUNTIME_FOREGROUND) != RUNTIME_WARM_NOTIFY:
            return
        if self.isVisible():
            return
        self.suspend_page()

    def _reapply_runtime_memory_profile(self) -> None:
        """按当前档位重新应用 WebView2 内存目标（页面就绪后补设 Low）。"""
        if self._is_closing or not self.is_valid:
            return
        mode = getattr(self, "_runtime_mode", RUNTIME_FOREGROUND)
        foreground = mode == RUNTIME_FOREGROUND
        self.apply_memory_profile(
            foreground, keep_webview_normal=foreground, quiet=True
        )

    def _set_background_timers_active(self, active: bool) -> None:
        """温态暂停健康/断线轮询，减少隐藏页无意义 reload。"""
        for attr in ("_health_timer", "_offline_timer"):
            timer = getattr(self, attr, None)
            if timer is None:
                continue
            try:
                if active:
                    if not timer.isActive():
                        if attr == "_health_timer":
                            timer.start(TEAMS_HEALTH_CHECK_INTERVAL_SEC * 1000)
                        else:
                            timer.start(45000)
                else:
                    timer.stop()
            except Exception:
                pass

    def _apply_runtime_js(self, mode: str) -> None:
        if not self.page() or self._is_closing:
            return
        mode_js = json.dumps(mode)
        js = (
            "(function(){"
            f"const m={mode_js};"
            "if(typeof window.__teamsApplyRuntimeMode==='function')"
            "window.__teamsApplyRuntimeMode(m);"
            "})();"
        )
        self.page().runJavaScript(js)

    def apply_memory_profile(
        self, foreground: bool, *, keep_webview_normal: bool = False, quiet: bool = False
    ) -> None:
        """前台 Normal / 活跃轮询；休眠页 Low / 慢轮询。

        keep_webview_normal: 活跃槽位内的后台账号保持 WebView2 Normal，避免 Teams 收消息被节流。
        quiet: 后台整理时不刷控制台日志。
        """
        if self._is_closing or not self.is_valid:
            return
        mem_normal = bool(foreground) or bool(keep_webview_normal)
        if self._engine_kind == "webview2" and self._wv2_widget is not None:
            try:
                from starsailx.engine.webview2 import apply_webview_memory_profile

                apply_webview_memory_profile(
                    self._wv2_widget, foreground=mem_normal, quiet=bool(quiet)
                )
            except Exception as e:
                print(f"[内存] 账号 {self.account_id} WebView2 档位: {e}")
        js_fg = bool(foreground) or bool(keep_webview_normal)
        self._apply_js_activity_profile(foreground, poll_fast=js_fg)

    def _apply_js_activity_profile(
        self, foreground: bool, *, poll_fast: bool = False
    ) -> None:
        if not self.page() or self._is_closing:
            return
        mode = getattr(self, "_runtime_mode", RUNTIME_FOREGROUND)
        if mode == RUNTIME_WARM_NOTIFY:
            fg_ms = int(WARM_TITLE_POLL_MS)
            poll_ms = fg_ms
        else:
            fg_ms = int(BADGE_FOREGROUND_POLL_MS)
            bg_ms = int(BADGE_BACKGROUND_POLL_MS)
            fast_poll = bool(foreground) or bool(poll_fast)
            poll_ms = fg_ms if fast_poll else bg_ms
        # 底线：所有账号（含后台温态）都伪装成可见，避免 Teams 节流后台标签连接，
        # 保证 20 个号都能持续收到消息与来电。
        fake_visible = True
        js = (
            "(function(){"
            "if(!window.__teamsxVisibilityHook&&"
            f"{str(fake_visible).lower()}"
            "){"
            "window.__teamsxVisibilityHook=true;"
            "try{"
            "Object.defineProperty(document,'hidden',{get:()=>false,configurable:true});"
            "Object.defineProperty(document,'visibilityState',{get:()=>'visible',configurable:true});"
            "}catch(e){}"
            "}"
            f"const fg={str(foreground).lower()};"
            f"const ms={poll_ms};"
            "if(window.__teams_title_poll_1){clearInterval(window.__teams_title_poll_1);"
            "window.__teams_title_poll_1=null;}"
            "if(typeof window.__teamsSyncBadgeFromTitle==='function'){"
            "window.__teams_title_poll_1=setInterval(window.__teamsSyncBadgeFromTitle,ms);}"
            "window.__teamsxForeground=fg;"
            "if(window.applyTeamsSoundPolicy)window.applyTeamsSoundPolicy();"
            "})();"
        )
        self.page().runJavaScript(js)

    def poll_unread_badge(self):
        """后台快速读取未读数（无需点开该账号）"""
        if not self.is_valid or not self.page() or self.is_loading or self._is_closing:
            return
        js = r"""
        (function() {
            try {
                if (typeof window.__teamsReadUnreadCount === 'function')
                    return window.__teamsReadUnreadCount();
                const m = document.title.match(/\((\d{1,5})\)/);
                return m ? parseInt(m[1], 10) : 0;
            } catch (e) { return 0; }
        })();
        """
        self.page().runJavaScript(js, self._on_poll_unread_result)

    def _on_poll_unread_result(self, result):
        try:
            if self.notification_callback and self.is_valid and result is not None:
                count = int(result)
                self.notification_callback(self.account_id, count, "unread", "", "")
        except Exception as e:
            print(f"未读轮询回调错误: {e}")

    def cleanup_js_intervals(self):
        """清理 JavaScript 定时器"""
        if self.page() and self.is_valid:
            js = """
            (function() {
                if (window.__teams_cleanup) return;
                window.__teams_cleanup = true;
                const intervals = [
                    '__teams_scroll_interval',
                    '__teams_protection_interval',
                    '__teams_unread_interval',
                    '__teams_notification_interval',
                    '__teams_title_poll_1',
                    '__teams_toast_interval',
                    '__teams_call_poll',
                    '__teams_realtime_scan',
                    '__teams_chatlist_scan',
                    '__teams_toast_scan'
                ];
                intervals.forEach(name => {
                    if (window[name]) {
                        clearInterval(window[name]);
                        window[name] = null;
                    }
                });
                const observers = [
                    '__teams_observer',
                    '__teams_theme_observer',
                    '__teams_image_observer',
                    '__teams_notification_observer',
                    '__teams_message_observer',
                    '__teams_realtime_observer',
                    '__teams_title_observer',
                    '__teams_video_observer',
                    '__teams_call_observer',
                    '__teams_chatlist_observer',
                    '__teams_toast_observer'
                ];
                observers.forEach(name => {
                    if (window[name]) {
                        try { window[name].disconnect(); } catch (e) {}
                        window[name] = null;
                    }
                });
            })();
            """
            self.page().runJavaScript(js)

    def clear_browser_disk_cache(self):
        """清理浏览器磁盘 HTTP 缓存（保留 Cookies / 登录态）。"""
        if self._is_closing:
            return
        if self._engine_kind == "webview2":
            wv = getattr(self, "_wv2_widget", None)
            if not wv or not getattr(wv, "is_ready", False):
                return
            try:
                from qtwebview2 import _dotnet_bridge as dotnet

                profile = wv._webview.CoreWebView2.Profile
                kinds = dotnet.Core.CoreWebView2BrowsingDataKinds.DiskCache
                profile.ClearBrowsingDataAsync(kinds)
            except Exception as e:
                print(f"[缓存] WebView2 账号 {self.account_id} 清磁盘缓存: {e}")
            return
        try:
            if self.profile:
                self.profile.clearHttpCache()
        except Exception:
            pass

    def resizeEvent(self, event):
        super().resizeEvent(event)
        host = getattr(self, "_host_main", None)
        if host and getattr(host, "_resize_active", False):
            return
        self._notify_teams_viewport_resize()

    def _notify_teams_viewport_resize(self) -> None:
        if self._is_closing or not self.is_valid or not self.page():
            return
        timer = getattr(self, "_resize_notify_timer", None)
        if timer is None:
            timer = QTimer(self)
            timer.setSingleShot(True)
            timer.timeout.connect(self._fire_teams_resize_event)
            self._resize_notify_timer = timer
        timer.start(35)

    def _fire_teams_resize_event(self) -> None:
        if self._is_closing or not self.is_valid or not self.page():
            return
        self.page().runJavaScript(
            "try{window.dispatchEvent(new Event('resize'));}catch(e){}"
        )

    def closeEvent(self, event):
        """关闭事件"""
        self.cleanup_js_intervals()
        if getattr(self, "_health_timer", None):
            self._health_timer.stop()
        self._is_closing = True
        self.is_valid = False
        super().closeEvent(event)

    def _inject_login_page_scripts(self):
        """Starsail 登录页：隐藏手机/邮箱/注册入口。"""
        self._wv2_doc_scripts.append(STARSAIL_SHELL_CSS_JS)
        return

    def _inject_persistent_scripts(self):
        """注入持久化 JavaScript 脚本（完全禁用浏览器通知）"""
        js_code = r"""
        (function() {
            const host = (window.location.hostname || '').toLowerCase();
            if (host.includes('login.microsoft') || host.includes('login.live')
                || host.includes('account.live')) {
                return;
            }
            if (window.__TEAMS_FULL_SCRIPT_V20) return;
            window.__TEAMS_FULL_SCRIPT_V20 = true;
            if (typeof window.__teamsxForeground === 'undefined') window.__teamsxForeground = false;
            (function initTeamsKeepPageActive() {
                if (window.__teamsxVisibilityHook) return;
                window.__teamsxVisibilityHook = true;
                try {
                    Object.defineProperty(document, 'hidden', {
                        get: () => false, configurable: true
                    });
                    Object.defineProperty(document, 'visibilityState', {
                        get: () => 'visible', configurable: true
                    });
                } catch (e) {}
            })();
            const __teamsxThrottle = (fn, wait) => {
                let last = 0, timer = null;
                return (...args) => {
                    const now = Date.now();
                    const rem = wait - (now - last);
                    if (rem <= 0) {
                        if (timer) { clearTimeout(timer); timer = null; }
                        last = now;
                        fn(...args);
                    } else if (!timer) {
                        timer = setTimeout(() => {
                            last = Date.now();
                            timer = null;
                            fn(...args);
                        }, rem);
                    }
                };
            };
            window.__teamsReadUnreadCount = function() {
                let count = 0;
                try {
                    const m = document.title.match(/\((\d{1,5})\)/);
                    if (m) count = parseInt(m[1], 10);
                    if (!count) {
                        const m2 = document.title.match(/(\d{1,5})\s*[-\u2013\u2014]\s*Microsoft/i);
                        if (m2) count = parseInt(m2[1], 10);
                    }
                } catch (e) {}
                if (!count) {
                    try {
                        const el = document.querySelector(
                            '[data-tid="app-bar"] [data-tid*="badge"], [data-tid="teams-app-bar"] [class*="counterBadge"]'
                        );
                        if (el) {
                            const tm = (el.innerText || el.textContent || '').match(/(\d{1,5})/);
                            if (tm) count = parseInt(tm[1], 10);
                        }
                    } catch (e) {}
                }
                if (!count) {
                    try {
                        let sum = 0;
                        document.querySelectorAll(
                            '[data-tid="chat-list-item"] [class*="counterBadge"], '
                            + '[data-tid="chat-list-item"] [data-tid*="badge"], '
                            + '[data-tid="chat-list"] [class*="unread"]'
                        ).forEach(el => {
                            const tm = (el.innerText || el.textContent || '').match(/(\d{1,5})/);
                            if (tm) sum += parseInt(tm[1], 10);
                        });
                        if (sum > 0) count = sum;
                    } catch (e) {}
                }
                return (isNaN(count) || count < 0) ? 0 : count;
            };
            if (typeof window.__TEAMS_NOTIFICATIONS_OFF === 'undefined')
                window.__TEAMS_NOTIFICATIONS_OFF = false;

            // ========== 0. Esc 返回 AI（不依赖焦点在 Qt） ==========
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

            // ========== 1. 声音策略 ==========
            // 通知开：后台 WebView 禁止网页消息提示音（由 TeamsX 本机 official.mp3 播放）；
            //         前台当前账号仍允许 Teams 网页音（通话/视频不拦截）。
            // 通知关：全部静音 audio。
            (function initTeamsSoundPolicy() {
                const O = {
                    Audio: window.Audio,
                    AudioContext: window.AudioContext,
                    webkitAudioContext: window.webkitAudioContext,
                    play: HTMLMediaElement.prototype.play
                };
                let muteInterval = null;
                let hooksOn = false;

                const shouldBlockWebNotifyAudio = () => {
                    if (window.__TEAMS_NOTIFICATIONS_OFF) return true;
                    return !window.__teamsxForeground;
                };

                const installMuteHooks = () => {
                    if (hooksOn) return;
                    hooksOn = true;
                    window.Audio = function() {
                        const a = new O.Audio();
                        if (shouldBlockWebNotifyAudio()) {
                            a.muted = true;
                            a.volume = 0;
                            a.play = () => Promise.resolve();
                        }
                        return a;
                    };
                    if (O.AudioContext) {
                        window.AudioContext = function() {
                            const ctx = new O.AudioContext();
                            if (shouldBlockWebNotifyAudio()) {
                                ctx.resume = () => Promise.resolve();
                            }
                            return ctx;
                        };
                    }
                    HTMLMediaElement.prototype.play = function() {
                        const tag = (this.tagName || '').toUpperCase();
                        if (tag === 'VIDEO' && !window.__TEAMS_NOTIFICATIONS_OFF) {
                            return O.play.apply(this, arguments);
                        }
                        if (shouldBlockWebNotifyAudio()) {
                            try {
                                this.muted = true;
                                this.volume = 0;
                                this.pause();
                            } catch (e) {}
                            return Promise.resolve();
                        }
                        return O.play.apply(this, arguments);
                    };
                    const muteAll = () => {
                        if (!shouldBlockWebNotifyAudio()) return;
                        document.querySelectorAll('audio').forEach(el => {
                            try {
                                el.muted = true;
                                el.volume = 0;
                                el.pause();
                            } catch (e) {}
                        });
                    };
                    muteAll();
                    if (!muteInterval) muteInterval = setInterval(muteAll, __MUTE_ALL_POLL_MS__);
                };

                window.applyTeamsSoundPolicy = function() {
                    try { installMuteHooks(); } catch (e) { console.log('applyTeamsSoundPolicy', e); }
                };
                window.applyTeamsSoundPolicy();
            })();

            // ========== 1.5 Teams 消息提示音（后台账号也需即时播放） ==========
            (function initTeamsNotifySound() {
                if (window.__teamsNotifySoundReady) return;
                window.__teamsNotifySoundReady = true;
                window.__teamsLastNotifySoundAt = 0;
                window.__teamsCachedNotifySrc = window.__teamsCachedNotifySrc || '';

                const isOfficialNotifyUrl = (u) => {
                    const s = String(u || '').toLowerCase();
                    return s.includes('00_teams_basic_notification')
                        || (s.includes('statics.teams.cdn.office.net')
                            && s.includes('/evergreen-assets/audio/')
                            && s.includes('notification'));
                };

                const pickNotifySrc = () => {
                    if (window.__teamsCachedNotifySrc
                        && isOfficialNotifyUrl(window.__teamsCachedNotifySrc)) {
                        return window.__teamsCachedNotifySrc;
                    }
                    try {
                        const entries = performance.getEntriesByType('resource') || [];
                        const hits = entries.map(e => String(e.name || '')).filter(isOfficialNotifyUrl);
                        if (hits.length) {
                            window.__teamsCachedNotifySrc = hits[hits.length - 1];
                            return window.__teamsCachedNotifySrc;
                        }
                    } catch (e) {}
                    return '';
                };

                window.__teamsPlayNotifySound = function() {
                    return false;
                };
            })();

            // ========== 2. 浏览器通知桥：拦截 Teams Notification → Python，不弹系统网页通知 ==========
            (function initTeamsUiNotificationPolicy() {
                let toastObserver = null;
                let toastInterval = null;
                const dummyNotif = () => ({
                    close: () => {},
                    addEventListener: () => {},
                    removeEventListener: () => {},
                });
                const installNotificationBridge = () => {
                    if (window.__teamsNotifBridgeInstalled) return;
                    window.__teamsNotifBridgeInstalled = true;
                    if (!window.__teamsOrigNotification && window.Notification) {
                        window.__teamsOrigNotification = window.Notification;
                    }
                    const BridgeNotif = function(title, options) {
                        if (window.__TEAMS_NOTIFICATIONS_OFF) return dummyNotif();
                        try {
                            const sender = String(title || '').trim() || '某人';
                            const opts = options || {};
                            const body = opts.body ? String(opts.body).trim() : '';
                            const msg = body || sender || '新消息';
                            const count = window.__teamsReadUnreadCount
                                ? window.__teamsReadUnreadCount() : 0;
                            // 使用 Teams 自带的 tag 做稳定去重（译达通同款：只信 Notification API）
                            const tag = opts.tag ? String(opts.tag).trim() : '';
                            // 来电识别：Teams 来电同样走 Notification API（后台账号唯一可靠路径，
                            // 因为隐藏页面不渲染来电 DOM）。用来电专属系统文案匹配，
                            // 这些词不会出现在普通聊天正文里，避免把消息误判成来电。
                            const callText = (sender + ' ' + body + ' ' + tag);
                            const isCall = /正在呼叫|来电|拨打|incoming call|is calling|calling you|ringing|started a call|wants to meet|语音通话|视频通话|audio call|video call/i.test(callText)
                                || /(^|[^a-z])call($|[^a-z])|calling|incoming|ring/i.test(tag);
                            if (!window.__externalNotificationCallback) return dummyNotif();
                            // 临时调试：上报每条通知原始内容，便于核对来电文案
                            try {
                                window.__externalNotificationCallback(
                                    'notif_debug', sender,
                                    'body=' + body + ' || tag=' + tag + ' || isCall=' + isCall,
                                    count
                                );
                            } catch (e) {}
                            if (false && isCall) {
                                const isVideo = /视频|video/i.test(callText);
                                const type = isVideo ? 'incoming_video' : 'incoming_call';
                                const message = isVideo ? '邀请你视频通话' : '邀请你语音通话';
                                window.__externalNotificationCallback(
                                    type, sender, message, count
                                );
                                // 关键：Teams 在来电结束（接听/拒绝/对方挂断）时会调用
                                // 该通知对象的 close()，借此立即停止后台账号的铃声。
                                const fireCallEnd = () => {
                                    try {
                                        if (window.__externalNotificationCallback) {
                                            window.__externalNotificationCallback(
                                                'call_end', sender, '', 0
                                            );
                                        }
                                    } catch (e) {}
                                };
                                return {
                                    close: fireCallEnd,
                                    addEventListener: function(ev, cb) {
                                        if (ev === 'close') { this.__onclose = cb; }
                                    },
                                    removeEventListener: function() {},
                                    dispatchEvent: function() { return true; },
                                    set onclose(fn) { this.__onclose = fn; },
                                    get onclose() { return this.__onclose; },
                                };
                            } else {
                                const stableId = tag
                                    ? `api_${tag}`
                                    : `api_${Date.now()}_${Math.random().toString(16).slice(2, 8)}`;
                                window.__externalNotificationCallback(
                                    'teams_notify', sender, `${stableId}|${msg}`, count
                                );
                            }
                        } catch (e) {}
                        return dummyNotif();
                    };
                    try {
                        BridgeNotif.requestPermission = () => Promise.resolve('granted');
                        BridgeNotif.permission = 'granted';
                    } catch (e) {}
                    window.Notification = BridgeNotif;
                    window.__teamsNotifApiBlocked = false;
                };
                const blockNotificationApi = () => {
                    if (!window.Notification || window.__teamsNotifApiBlocked) return;
                    if (!window.__teamsOrigNotification) {
                        window.__teamsOrigNotification = window.Notification;
                    }
                    window.__teamsNotifApiBlocked = true;
                    window.Notification = function() {
                        return dummyNotif();
                    };
                    window.Notification.requestPermission = () => Promise.resolve('denied');
                };
                const restoreNotificationApi = () => {
                    if (window.__teamsOrigNotification) {
                        window.Notification = window.__teamsOrigNotification;
                        window.__teamsNotifApiBlocked = false;
                    }
                };
                const isIncomingCallUi = (el) => {
                    if (!el || el.nodeType !== 1) return false;
                    try {
                        const tid = String(el.getAttribute('data-tid') || '').toLowerCase();
                        if (/incoming|calling|ringing|accept|decline|precall/.test(tid)) return true;
                        const txt = String(el.innerText || el.textContent || '').slice(0, 240);
                        if (/来电|正在呼叫|邀请你加入|incoming call|is calling|ringing/i.test(txt)) return true;
                        if (el.closest(
                            '[data-tid*="incoming"], [data-tid*="calling"], [data-tid*="ringing"]'
                        )) return true;
                    } catch (e) {}
                    return false;
                };
                const startToastCleanup = () => {
                    const removeToasts = () => {
                        if (!window.__TEAMS_NOTIFICATIONS_OFF) return;
                        document.querySelectorAll('[data-tid="notification"]').forEach(el => {
                            if (!isIncomingCallUi(el)) {
                                try { el.remove(); } catch (e) {}
                            }
                        });
                        document.querySelectorAll('[class*="toast"]').forEach(el => {
                            if (!isIncomingCallUi(el) && !el.closest(
                                '[data-tid*="incoming"], [data-tid*="calling"], [data-tid*="ringing"]'
                            )) {
                                try { el.remove(); } catch (e) {}
                            }
                        });
                    };
                    removeToasts();
                    if (!toastInterval) toastInterval = setInterval(removeToasts, 5000);
                    if (!toastObserver && document.body) {
                        toastObserver = new MutationObserver(removeToasts);
                        toastObserver.observe(document.body, { childList: true, subtree: true });
                    }
                };
                const stopToastCleanup = () => {
                    if (toastInterval) { clearInterval(toastInterval); toastInterval = null; }
                    if (toastObserver) { toastObserver.disconnect(); toastObserver = null; }
                };
                window.applyTeamsUiNotificationPolicy = function() {
                    if (window.__TEAMS_NOTIFICATIONS_OFF) {
                        blockNotificationApi();
                        startToastCleanup();
                    } else {
                        installNotificationBridge();
                        stopToastCleanup();
                    }
                };
                window.applyTeamsUiNotificationPolicy();
            })();

            // ========== 2.5 运行档位：foreground 全量扫描 / warm_notify 轻量保活 ==========
            (function initTeamsRuntimeModes() {
                const stopInterval = (name) => {
                    if (window[name]) {
                        clearInterval(window[name]);
                        window[name] = null;
                    }
                };
                const stopObserver = (name) => {
                    if (window[name]) {
                        try { window[name].disconnect(); } catch (e) {}
                        window[name] = null;
                    }
                };
                window.__teamsPauseHeavyWatchers = function() {
                    window.__teamsxHeavyPaused = true;
                    // 标准版：温态仍保留实时消息监听 + 来电检测（事件驱动，开销小），
                    // 只暂停最重的整列扫描 / 吐司扫描 / 图片观察，保证后台账号实时收消息与来电。
                    [
                        '__teams_chatlist_scan',
                        '__teams_toast_scan',
                    ].forEach(stopInterval);
                    [
                        '__teams_toast_observer',
                        '__teams_image_observer',
                    ].forEach(stopObserver);
                    if (typeof window.__teamsEnableRealtimeNotifications === 'function') {
                        window.__teams_realtime_notification_enabled = false;
                        window.__teamsEnableRealtimeNotifications();
                    }
                    if (typeof window.__teamsEnableIncomingCallDetection === 'function') {
                        window.__teams_incoming_call_enabled = false;
                        window.__teamsEnableIncomingCallDetection();
                    }
                    if (typeof window.__teamsSyncBadgeFromTitle === 'function') {
                        stopInterval('__teams_title_poll_1');
                        window.__teams_title_poll_1 = setInterval(
                            window.__teamsSyncBadgeFromTitle, __WARM_TITLE_POLL_MS__
                        );
                    }
                };
                window.__teamsResumeHeavyWatchers = function() {
                    window.__teamsxHeavyPaused = false;
                    if (typeof window.__teamsEnableRealtimeNotifications === 'function') {
                        window.__teams_realtime_notification_enabled = false;
                        window.__teamsEnableRealtimeNotifications();
                    }
                    if (typeof window.__teamsEnableChatListWatcher === 'function') {
                        window.__teams_chatlist_watch_enabled = false;
                        window.__teamsEnableChatListWatcher();
                    }
                    if (typeof window.__teamsEnableTeamsToastWatcher === 'function') {
                        window.__teams_toast_watch_enabled = false;
                        window.__teamsEnableTeamsToastWatcher();
                    }
                    if (typeof window.__teamsEnableIncomingCallDetection === 'function') {
                        window.__teams_incoming_call_enabled = false;
                        window.__teamsEnableIncomingCallDetection();
                    }
                    if (typeof window.__teamsSyncBadgeFromTitle === 'function') {
                        stopInterval('__teams_title_poll_1');
                        window.__teams_title_poll_1 = setInterval(
                            window.__teamsSyncBadgeFromTitle, __TITLE_BADGE_POLL_MS__
                        );
                    }
                };
                window.__teamsApplyRuntimeMode = function(mode) {
                    window.__teamsxRuntimeMode = mode || 'foreground';
                    if (mode === 'foreground') {
                        window.__teamsResumeHeavyWatchers();
                        return;
                    }
                    if (mode === 'warm_notify') {
                        window.__teamsPauseHeavyWatchers();
                        return;
                    }
                    if (mode === 'cold_unloaded') {
                        window.__teamsPauseHeavyWatchers();
                    }
                };
            })();

            // ========== 3. 图片交互（复制经 Python 剪贴板，避免 QtWebEngine clipboard 失败） ==========
            const enableImageInteractions = () => {
                const showToastMsg = (message, isError = false) => {
                    let el = document.getElementById('teams-x-toast');
                    if (!el && document.body) {
                        el = document.createElement('div');
                        el.id = 'teams-x-toast';
                        el.style.cssText = 'position:fixed;bottom:20px;left:50%;transform:translateX(-50%);'
                            + 'z-index:100000;pointer-events:none;color:#fff;padding:8px 16px;border-radius:8px;';
                        document.body.appendChild(el);
                    }
                    if (!el) return;
                    el.textContent = message;
                    el.style.background = isError ? 'rgba(220,53,69,.9)' : 'rgba(0,0,0,.8)';
                    el.style.display = 'block';
                    clearTimeout(window.__teams_toast_hide_timer);
                    window.__teams_toast_hide_timer = setTimeout(() => {
                        el.style.display = 'none';
                    }, 2000);
                };
                const stabilizeImageAfterCopy = (img) => {
                    if (!img || !img.isConnected) return;
                    const scrollEl = img.closest('[role="log"], [data-tid*="message"], [class*="message"]');
                    const scrollTop = scrollEl ? scrollEl.scrollTop : null;
                    const scrollLeft = scrollEl ? scrollEl.scrollLeft : null;
                    const reset = () => {
                        try { img.blur(); } catch (e) {}
                        img.style.removeProperty('transform');
                        img.style.removeProperty('margin');
                        img.style.removeProperty('top');
                        img.style.removeProperty('left');
                        if (scrollEl != null && scrollTop != null) {
                            scrollEl.scrollTop = scrollTop;
                            scrollEl.scrollLeft = scrollLeft;
                        }
                        void img.offsetHeight;
                    };
                    requestAnimationFrame(() => requestAnimationFrame(reset));
                };
                document.addEventListener('contextmenu', (e) => {
                    const t = e.target;
                    if (t && t.tagName === 'IMG' && t.hasAttribute('data-teams-enhanced')) {
                        e.preventDefault();
                        e.stopImmediatePropagation();
                    }
                }, true);
                const MAX_CLIP_EDGE = 2048;
                const waitForClipboardBridge = (fn, maxMs) => {
                    const deadline = Date.now() + (maxMs || 8000);
                    const tick = () => {
                        if (window.__teamsCopyImageToClipboard) { fn(); return; }
                        if (typeof window.connectTeamsBridge === 'function') {
                            try { window.connectTeamsBridge(); } catch (e) {}
                        }
                        if (Date.now() > deadline) {
                            showToastMsg('✗ 复制失败，请切换账号后重试', true);
                            return;
                        }
                        setTimeout(tick, 80);
                    };
                    tick();
                };
                const imageToDataUrl = (img) => {
                    let w = img.naturalWidth || img.width || 0;
                    let h = img.naturalHeight || img.height || 0;
                    if (!w || !h) return '';
                    const scale = Math.min(1, MAX_CLIP_EDGE / Math.max(w, h));
                    w = Math.max(1, Math.floor(w * scale));
                    h = Math.max(1, Math.floor(h * scale));
                    const c = document.createElement('canvas');
                    c.width = w; c.height = h;
                    c.getContext('2d').drawImage(img, 0, 0, w, h);
                    return c.toDataURL('image/png', 0.92);
                };
                const copyDataUrlViaPython = (dataUrl, imgEl) => {
                    waitForClipboardBridge(() => {
                        try {
                            window.__teamsCopyImageToClipboard(dataUrl);
                            showToastMsg('已复制');
                            stabilizeImageAfterCopy(imgEl);
                        } catch (err) {
                            showToastMsg('复制失败', true);
                        }
                    });
                };
                const copyImageViaCanvas = (imageUrl, srcImgEl) => {
                    const img = new Image();
                    img.crossOrigin = 'anonymous';
                    img.onload = () => {
                        try {
                            const dataUrl = imageToDataUrl(img);
                            if (dataUrl) copyDataUrlViaPython(dataUrl, srcImgEl);
                            else showToastMsg('复制失败', true);
                        } catch (e) {
                            showToastMsg('复制失败', true);
                        }
                    };
                    img.onerror = () => {
                        if (imageUrl && window.__teamsCopyImageUrl) {
                            window.__teamsCopyImageUrl(imageUrl);
                            showToastMsg('正在复制…');
                            stabilizeImageAfterCopy(srcImgEl);
                        } else {
                            showToastMsg('复制失败', true);
                        }
                    };
                    img.src = imageUrl;
                };
                const copyImageToClipboard = (imageUrl, imgEl) => {
                    if (!imageUrl && imgEl) imageUrl = imgEl.src;
                    if (!imageUrl) {
                        showToastMsg('✗ 无图片地址', true);
                        return false;
                    }
                    if (imageUrl.startsWith('data:')) {
                        copyDataUrlViaPython(imageUrl, imgEl);
                        return true;
                    }
                    try {
                        if (imgEl && imgEl.complete && (imgEl.naturalWidth || imgEl.width)) {
                            const dataUrl = imageToDataUrl(imgEl);
                            if (dataUrl) {
                                copyDataUrlViaPython(dataUrl, imgEl);
                                return true;
                            }
                        }
                    } catch (err) {
                        console.error('复制失败:', err);
                    }
                    copyImageViaCanvas(imageUrl, imgEl);
                    return true;
                };
                
                // 下载图片
                const downloadImage = (imageUrl, filename) => {
                    try {
                        const a = document.createElement('a');
                        a.href = imageUrl;
                        a.download = filename || imageUrl.split('/').pop() || 'teams_image.png';
                        document.body.appendChild(a);
                        a.click();
                        document.body.removeChild(a);
                        showToastMsg('✓ 图片下载中...');
                    } catch (err) {
                        showToastMsg('✗ 下载失败', true);
                    }
                };
                
                const resolveImageUrl = (imgOrUrl) => {
                    if (imgOrUrl && typeof imgOrUrl === 'object' && imgOrUrl.tagName === 'IMG') {
                        return imgOrUrl.currentSrc || imgOrUrl.src || '';
                    }
                    return String(imgOrUrl || '');
                };
                const fetchImageObjectUrl = (imageUrl) => fetch(imageUrl, { credentials: 'include', mode: 'cors' })
                    .then((r) => {
                        if (!r.ok) throw new Error('fetch failed');
                        return r.blob();
                    })
                    .then((blob) => URL.createObjectURL(blob));
                const loadViewerImage = (srcImg, displayImg, imageUrl, onReady, onFail) => {
                    const done = () => { if (onReady) onReady(); };
                    const fail = () => { if (onFail) onFail(); };
                    if (!imageUrl) { fail(); return; }
                    if (imageUrl.startsWith('data:')) {
                        displayImg.onload = done;
                        displayImg.onerror = fail;
                        displayImg.src = imageUrl;
                        return;
                    }
                    if (srcImg && srcImg.complete && (srcImg.naturalWidth || srcImg.width)) {
                        try {
                            const dataUrl = imageToDataUrl(srcImg);
                            if (dataUrl) {
                                displayImg.onload = done;
                                displayImg.onerror = () => {
                                    fetchImageObjectUrl(imageUrl)
                                        .then((objUrl) => {
                                            displayImg.onload = () => {
                                                URL.revokeObjectURL(objUrl);
                                                done();
                                            };
                                            displayImg.onerror = fail;
                                            displayImg.src = objUrl;
                                        })
                                        .catch(fail);
                                };
                                displayImg.src = dataUrl;
                                return;
                            }
                        } catch (e) {}
                    }
                    displayImg.referrerPolicy = 'no-referrer-when-downgrade';
                    displayImg.crossOrigin = 'anonymous';
                    displayImg.onload = done;
                    displayImg.onerror = () => {
                        fetchImageObjectUrl(imageUrl)
                            .then((objUrl) => {
                                displayImg.onload = () => {
                                    URL.revokeObjectURL(objUrl);
                                    done();
                                };
                                displayImg.onerror = fail;
                                displayImg.src = objUrl;
                            })
                            .catch(fail);
                    };
                    displayImg.src = imageUrl;
                };

                // 显示图片查看器
                const showImageViewer = (srcImgOrUrl) => {
                    const srcImg = (srcImgOrUrl && typeof srcImgOrUrl === 'object' && srcImgOrUrl.tagName === 'IMG')
                        ? srcImgOrUrl : null;
                    const imageUrl = resolveImageUrl(srcImgOrUrl);
                    const viewer = document.createElement('div');
                    viewer.style.cssText = `
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100%;
                        background: rgba(0,0,0,0.95);
                        z-index: 100000;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        cursor: pointer;
                    `;

                    const statusEl = document.createElement('div');
                    statusEl.textContent = '加载中...';
                    statusEl.style.cssText = `
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        color: #fff;
                        font-size: 16px;
                        pointer-events: none;
                        z-index: 100001;
                    `;
                    
                    const img = document.createElement('img');
                    img.style.cssText = `
                        max-width: 90%;
                        max-height: 90%;
                        object-fit: contain;
                        border-radius: 8px;
                        cursor: default;
                        opacity: 0;
                        transition: opacity .2s ease;
                    `;
                    
                    const btnContainer = document.createElement('div');
                    btnContainer.style.cssText = `
                        position: absolute;
                        bottom: 20px;
                        right: 20px;
                        display: flex;
                        gap: 12px;
                        z-index: 100001;
                        cursor: default;
                    `;
                    
                    const downloadBtn = document.createElement('button');
                    downloadBtn.textContent = '⬇ 下载图片';
                    downloadBtn.style.cssText = `
                        background: #0078d4;
                        border: none;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: bold;
                    `;
                    downloadBtn.onclick = (e) => {
                        e.stopPropagation();
                        const filename = imageUrl.split('/').pop().split('?')[0] || 'teams_image.png';
                        downloadImage(imageUrl, filename);
                    };
                    
                    const copyBtn = document.createElement('button');
                    copyBtn.textContent = '📋 复制图片';
                    copyBtn.style.cssText = `
                        background: #28a745;
                        border: none;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: bold;
                    `;
                    copyBtn.onclick = (e) => {
                        e.stopPropagation();
                        if (img.complete && (img.naturalWidth || img.width)) {
                            copyImageToClipboard(imageUrl, img);
                        } else {
                            img.onload = () => copyImageToClipboard(imageUrl, img);
                        }
                    };
                    
                    const closeBtn = document.createElement('button');
                    closeBtn.textContent = '✕ 关闭';
                    closeBtn.style.cssText = `
                        background: #6c757d;
                        border: none;
                        color: white;
                        padding: 10px 20px;
                        border-radius: 6px;
                        cursor: pointer;
                        font-size: 14px;
                        font-weight: bold;
                    `;
                    closeBtn.onclick = (e) => {
                        e.stopPropagation();
                        viewer.remove();
                    };
                    
                    btnContainer.appendChild(copyBtn);
                    btnContainer.appendChild(downloadBtn);
                    btnContainer.appendChild(closeBtn);
                    
                    viewer.appendChild(statusEl);
                    viewer.appendChild(img);
                    viewer.appendChild(btnContainer);
                    viewer.onclick = (e) => {
                        if (e.target === viewer) viewer.remove();
                    };
                    
                    document.body.appendChild(viewer);
                    loadViewerImage(
                        srcImg,
                        img,
                        imageUrl,
                        () => {
                            statusEl.remove();
                            img.style.opacity = '1';
                        },
                        () => {
                            statusEl.textContent = '图片加载失败';
                            statusEl.style.color = '#ff6b6b';
                        }
                    );
                };
                
                // 仅聊天记录里“真实发送的图片/附件”才允许点开、复制；
                // Teams 界面内嵌插画、空状态图、图标一律跳过
                const isChatAttachmentImage = (img) => {
                    if (!img || img.tagName !== 'IMG') return false;

                    // 排除应用框架与空状态/插画容器
                    if (img.closest(
                        '[data-tid="app-bar"], [data-tid="teams-app-bar"], [data-tid="left-rail"], '
                        + 'header, nav, aside, footer, [role="banner"], [role="navigation"], '
                        + '[data-tid*="empty"], [data-tid*="zero"], [data-tid*="placeholder"], '
                        + '[data-tid*="welcome"], [data-tid*="hero"], [data-tid*="illustration"], '
                        + '[class*="empty"], [class*="placeholder"], [class*="illustration"], '
                        + '[class*="zeroState"], [class*="ZeroState"]'
                    )) {
                        return false;
                    }

                    // 按来源排除：静态资源 / 插画 / 图标 / 表情 / 头像
                    const src = img.currentSrc || img.src || '';
                    if (!src || src.startsWith('data:image/svg+xml')) return false;
                    const lower = src.toLowerCase();
                    if (lower.includes('evergreen-assets') || lower.includes('/illustrations/')
                        || lower.includes('/assets/') || lower.includes('statics.')
                        || lower.includes('cdn.office.net') || lower.includes('/fluent')
                        || lower.includes('emoji') || lower.includes('avatar')
                        || lower.includes('icon') || lower.includes('presence')
                        || lower.includes('reaction') || lower.endsWith('.svg')) {
                        return false;
                    }

                    // 必须位于真实消息正文 / 附件容器内（不再用宽松的 role="log"）
                    let host = img.closest(
                        '[data-tid="message-body"], [data-tid="messageBodyContent"], '
                        + '[data-tid*="attachment"]'
                    );
                    if (!host) {
                        // 备用：消息流里被链接包裹的图片（真实图片附件常包一层 <a>）
                        const inLog = img.closest('div[role="log"], [data-tid="chat-pane-list"]');
                        const linked = img.closest('a[href]');
                        if (!(inLog && linked)) return false;
                    }

                    const alt = (img.getAttribute('alt') || '').trim();
                    if (alt.length === 1) return false; // 单字符多为表情
                    const width = img.naturalWidth || img.width || 0;
                    const height = img.naturalHeight || img.height || 0;
                    if (width < 64 && height < 64) return false;
                    return true;
                };

                // 增强单个图片
                const enhanceImage = (img) => {
                    if (img.hasAttribute('data-teams-enhanced')) return;
                    if (!isChatAttachmentImage(img)) return;
                    
                    img.setAttribute('data-teams-enhanced', 'true');
                    img.style.cursor = 'pointer';
                    
                    img.addEventListener('click', (e) => {
                        e.stopPropagation();
                        showImageViewer(img);
                    });
                    
                    img.addEventListener('contextmenu', (e) => {
                        e.preventDefault();
                        e.stopPropagation();
                        e.stopImmediatePropagation();
                        if (typeof window.connectTeamsBridge === 'function') {
                            try { window.connectTeamsBridge(); } catch (err) {}
                        }
                        copyImageToClipboard(img.currentSrc || img.src, img);
                        return false;
                    }, true);
                };
                
                // 监控新图片
                if (window.__teams_image_observer) {
                    window.__teams_image_observer.disconnect();
                }
                window.__teams_image_observer = new MutationObserver(() => {
                    document.querySelectorAll('img:not([data-teams-enhanced])').forEach(enhanceImage);
                });
                window.__teams_image_observer.observe(document.body, { childList: true, subtree: true });
                
                // 处理现有图片
                document.querySelectorAll('img').forEach(enhanceImage);
            };
            setTimeout(enableImageInteractions, 2000);

            // ========== 3.5 标题未读数快速同步（降低徽标延迟） ==========
            (function enableFastTitleBadgeSync() {
                if (window.__teams_title_badge_sync) return;
                window.__teams_title_badge_sync = true;
                let lastCount = -1;
                let lastPostAt = 0;
                window.__teamsSyncBadgeFromTitle = () => {
                    const count = window.__teamsReadUnreadCount ? window.__teamsReadUnreadCount() : 0;
                    if (count === lastCount) return;
                    lastCount = count;
                    const now = Date.now();
                    if (now - lastPostAt < __NOTIFY_TITLE_SYNC_MIN_MS__) return;
                    lastPostAt = now;
                    if (window.__externalNotificationCallback) {
                        window.__externalNotificationCallback('unread', '', '', count);
                    }
                };
                window.__teams_title_poll_1 = setInterval(window.__teamsSyncBadgeFromTitle, __TITLE_BADGE_POLL_MS__);
                try {
                    const titleEl = document.querySelector('title');
                    if (titleEl) {
                        window.__teams_title_observer = new MutationObserver(window.__teamsSyncBadgeFromTitle);
                        window.__teams_title_observer.observe(titleEl, {
                            childList: true, characterData: true, subtree: true
                        });
                    }
                } catch (e) {}
            })();

            // ========== 4. 实时消息通知检测（MutationObserver 实时监控） ==========
            const enableRealTimeNotificationDetection = () => {
                if (window.__teams_realtime_notification_enabled) return;
                window.__teams_realtime_notification_enabled = true;
                
                let processedMessages = new Set();
                const MAX_CACHE = 200;
                
                const getMessageType = (element) => {
                    const text = (element.innerText || element.textContent || '').toLowerCase();
                    const html = (element.innerHTML || '').toLowerCase();

                    // 图片/表情：优先识别 img
                    const imgs = element.querySelectorAll('img');
                    if (imgs && imgs.length) {
                        let isEmoji = false;
                        imgs.forEach(img => {
                            const src = (img.getAttribute('src') || '').toLowerCase();
                            const alt = (img.getAttribute('alt') || '').trim();
                            if (src.includes('emoji') || src.includes('emoticon') || alt.length === 1) {
                                isEmoji = true;
                            }
                        });
                        // 同一条消息可能既有 emoji 又有图片，优先图片
                        if (!isEmoji) return 'image';
                        return 'emoji';
                    }

                    // 文件：附件/文件卡片
                    if (element.querySelector('[data-tid*="attachment"]') ||
                        element.querySelector('[aria-label*="attachment"]') ||
                        html.includes('attachment') || text.includes('文件') || text.includes('附件')) {
                        return 'file';
                    }

                    if (element.querySelector('[aria-label*="voice"]') ||
                        element.querySelector('[aria-label*="audio"]') ||
                        html.includes('voice-message') || html.includes('audio-message') ||
                        text.includes('语音') || text.includes('录音')) return 'voice';

                    if (element.querySelector('[aria-label*="like"]') ||
                        element.querySelector('[data-tid="message-reaction"]') ||
                        html.includes('liked') || text.includes('点赞') || text.includes('👍')) return 'like';

                    return 'reply';
                };

                const getSenderName = (element) => {
                    const nameSelectors = [
                        '[data-tid="message-sender-name"]',
                        '[data-tid="author"]',
                        '[data-tid*="sender"]',
                        '[class*="display-name"]',
                        '[class*="sender"]',
                        '[aria-label*="said"]'
                    ];
                    for (let sel of nameSelectors) {
                        const nameEl = element.querySelector(sel);
                        if (nameEl && nameEl.innerText.trim()) {
                            return nameEl.innerText.trim();
                        }
                    }
                    try {
                        const labelled = element.getAttribute('aria-label') || '';
                        const m = labelled.match(/^(.+?)\s+(said|说|发送)/i);
                        if (m && m[1]) return m[1].trim();
                    } catch (e) {}
                    return '某人';
                };

                const getMessageContent = (element) => {
                    const contentSelectors = [
                        '[data-tid="message-body"]',
                        '[class*="message-content"]',
                        '[class*="message-text"]'
                    ];
                    for (let sel of contentSelectors) {
                        const contentEl = element.querySelector(sel);
                        if (contentEl) {
                            let text = contentEl.innerText.trim();
                            return text.length > 50 ? text.substring(0, 50) + '...' : text;
                        }
                    }
                    return '';
                };
                
                const quickHash = (s) => {
                    // 简单 hash：避免重复通知误杀
                    let h = 2166136261;
                    for (let i = 0; i < s.length; i++) {
                        h ^= s.charCodeAt(i);
                        h = Math.imul(h, 16777619);
                    }
                    return (h >>> 0).toString(16);
                };

                const getMessageDomId = (element) => {
                    if (!element) return '';
                    const attrs = ['data-mid', 'data-itemid', 'data-message-id', 'id'];
                    for (const a of attrs) {
                        try {
                            const v = element.getAttribute(a);
                            if (v && String(v).length < 120) return `${a}:${v}`;
                        } catch (e) {}
                    }
                    try {
                        const tid = element.getAttribute('data-tid');
                        const ts = element.querySelector('time[datetime]');
                        const dt = ts && ts.getAttribute('datetime');
                        if (tid && dt) return `${tid}:${dt}`;
                    } catch (e) {}
                    return '';
                };

                const sendNotification = (type, sender, content, element) => {
                    // DOM 扫描仅标记已处理，不触发提示音（响铃只走 Teams Notification API）
                    if (window.__TEAMS_NOTIFICATIONS_OFF) return;
                    const raw = (element && element.outerHTML) ? element.outerHTML : `${type}|${sender}|${content}|${Date.now()}`;
                    const domId = getMessageDomId(element);
                    const msgId = domId || `${type}_${sender}_${quickHash(raw)}`;
                    if (processedMessages.has(msgId)) return;
                    if (processedMessages.size > MAX_CACHE) {
                        const items = Array.from(processedMessages);
                        items.slice(0, MAX_CACHE / 2).forEach(id => processedMessages.delete(id));
                    }
                    processedMessages.add(msgId);
                };
                
                const scanRealtimeMessages = () => {
                    if (window.__teamsxHeavyPaused) return;
                    const messageSelectors = [
                        '[data-tid="message"]',
                        '[data-tid="chat-message"]',
                        'div[role="log"] > div'
                    ];
                    for (const sel of messageSelectors) {
                        document.querySelectorAll(sel).forEach(messageEl => {
                            if (!messageEl || messageEl.hasAttribute('data-realtime-notified')) return;
                            const type = getMessageType(messageEl);
                            const sender = getSenderName(messageEl);
                            const content = getMessageContent(messageEl);
                            sendNotification(type, sender, content, messageEl);
                            messageEl.setAttribute('data-realtime-notified', 'true');
                        });
                    }
                };

                // 使用 MutationObserver 实时监听新消息
                const handleRealtimeMutations = (mutations) => {
                    for (const mutation of mutations) {
                        if (mutation.type === 'childList') {
                            mutation.addedNodes.forEach(node => {
                                if (node.nodeType === Node.ELEMENT_NODE) {
                                    // 检查是否是消息元素
                                    const messageSelectors = [
                                        '[data-tid="message"]',
                                        '[data-tid="chat-message"]',
                                        'div[role="log"] > div'
                                    ];
                                    for (const sel of messageSelectors) {
                                        const messageEl = node.matches && node.matches(sel) ? node : node.querySelector(sel);
                                        if (messageEl && !messageEl.hasAttribute('data-realtime-notified')) {
                                            const type = getMessageType(messageEl);
                                            const sender = getSenderName(messageEl);
                                            const content = getMessageContent(messageEl);
                                            sendNotification(type, sender, content, messageEl);
                                            messageEl.setAttribute('data-realtime-notified', 'true');
                                        }
                                    }
                                }
                            });
                        }
                    }
                };
                const messageObserver = new MutationObserver(
                    __teamsxThrottle(handleRealtimeMutations, 180)
                );
                
                // 观察聊天区与活动摘要（未打开具体会话时也能收到提醒）
                const startObserving = () => {
                    const targets = new Set();
                    const chatContainer = document.querySelector('div[role="log"]');
                    if (chatContainer) targets.add(chatContainer);
                    document.querySelectorAll(
                        '[data-tid="activity-feed"], [data-tid="chat-list"], main'
                    ).forEach(el => targets.add(el));
                    if (!targets.size && document.body) targets.add(document.body);
                    targets.forEach(el => {
                        try {
                            messageObserver.observe(el, { childList: true, subtree: true });
                        } catch (e) {}
                    });
                    if (!targets.size) setTimeout(startObserving, 500);
                };
                startObserving();
                window.__teams_realtime_scan = setInterval(scanRealtimeMessages, __REALTIME_SCAN_MS__);
                scanRealtimeMessages();
                window.__teams_realtime_observer = messageObserver;
            };
            window.__teamsEnableRealtimeNotifications = enableRealTimeNotificationDetection;
            setTimeout(enableRealTimeNotificationDetection, 400);

            // ========== 4.2 聊天列表变化检测（最可靠：每条新消息都触发，含同会话连发） ==========
            const enableChatListWatcher = () => {
                if (window.__teams_chatlist_watch_enabled) return;
                window.__teams_chatlist_watch_enabled = true;

                const sigMap = {};            // chatKey -> 最近一次消息签名
                let primed = false;           // 首轮仅建立基线，不响铃

                const hashStr = (s) => {
                    let h = 2166136261;
                    s = String(s || '');
                    for (let i = 0; i < s.length; i++) {
                        h ^= s.charCodeAt(i);
                        h = Math.imul(h, 16777619);
                    }
                    return (h >>> 0).toString(16);
                };

                const getItems = () => {
                    let items = document.querySelectorAll(
                        '[data-tid="chat-list-item"], [data-tid*="chat-list-item"]'
                    );
                    if (!items.length) {
                        items = document.querySelectorAll(
                            '[role="treeitem"], [data-tid="chat-list"] [role="listitem"], '
                            + '[data-tid="chat-list"] li, [role="listbox"] [role="option"]'
                        );
                    }
                    if (!items.length) {
                        items = document.querySelectorAll(
                            '[data-tid="chat-list"] > *, [role="list"] > [role="listitem"]'
                        );
                    }
                    return items;
                };

                const itemKey = (item) => {
                    let k = item.getAttribute('id')
                        || item.getAttribute('data-tid')
                        || item.getAttribute('data-itemid')
                        || '';
                    if (!k || k === 'chat-list-item') {
                        const nameEl = item.querySelector(
                            '[data-tid="title"], [class*="title"], [class*="displayName"], '
                            + '[class*="chatName"]'
                        );
                        const nm = nameEl && (nameEl.innerText || '').trim();
                        const aria = (item.getAttribute('aria-label') || '').slice(0, 60);
                        k = nm || aria || '';
                    }
                    return k;
                };

                const itemName = (item) => {
                    const nameEl = item.querySelector(
                        '[data-tid="title"], [class*="title"], [class*="displayName"], '
                        + '[class*="chatName"]'
                    );
                    let nm = nameEl && (nameEl.innerText || '').trim();
                    if (nm) return nm.split(/[\r\n]+/)[0].trim();
                    const aria = (item.getAttribute('aria-label') || '').trim();
                    if (aria) return aria.split(/[，,。.\r\n]/)[0].trim();
                    return '某人';
                };

                const itemSig = (item) => {
                    const full = (item.innerText || item.textContent || '')
                        .replace(/\s+/g, ' ').trim().slice(0, 400);
                    const aria = (item.getAttribute('aria-label') || '').trim().slice(0, 200);
                    return full || aria || '';
                };

                const isUnread = (item) => {
                    try {
                        if (item.querySelector(
                            '[class*="counterBadge"], [data-tid*="badge"], [class*="unread"], '
                            + '[data-tid="unread-indicator"]'
                        )) return true;
                        const aria = item.getAttribute('aria-label') || '';
                        if (/未读|unread/i.test(aria)) return true;
                    } catch (e) {}
                    return false;
                };

                const scan = () => {
                    if (window.__teamsxHeavyPaused) return;
                    if (window.__TEAMS_NOTIFICATIONS_OFF) { primed = true; return; }
                    let items = getItems();
                    if (!items.length) {
                        items = document.querySelectorAll(
                            '[data-tid="activity-feed"] > *, [data-tid*="activity-item"], '
                            + '[data-tid*="activityFeed"]'
                        );
                    }
                    if (!items.length) return;
                    const count = window.__teamsReadUnreadCount
                        ? window.__teamsReadUnreadCount() : 0;
                    items.forEach(item => {
                        const key = itemKey(item);
                        if (!key) return;
                        const info = itemSig(item);
                        const prev = sigMap[key];
                        sigMap[key] = info;
                        if (!primed || prev === undefined) return;   // 基线
                        if (prev === info) return;                   // 无变化
                        // 聊天列表变化只同步角标，不响铃（响铃由 Notification API 负责）
                        if (typeof window.__teamsSyncBadgeFromTitle === 'function') {
                            window.__teamsSyncBadgeFromTitle();
                        }
                    });
                    primed = true;
                };

                window.__teams_chatlist_scan = setInterval(scan, __CHATLIST_SCAN_MS__);
                scan();
                try {
                    const root = document.querySelector('[data-tid="chat-list"]')
                        || document.querySelector('main') || document.body;
                    if (root) {
                        const scanThrottled = __teamsxThrottle(scan, 220);
                        window.__teams_chatlist_observer = new MutationObserver(() => scanThrottled());
                        window.__teams_chatlist_observer.observe(root, {
                            childList: true, subtree: true, characterData: true
                        });
                    }
                } catch (e) {}
            };
            window.__teamsEnableChatListWatcher = enableChatListWatcher;
            setTimeout(enableChatListWatcher, 600);

            // ========== 4.3 Teams 网页通知条：已弃用（与 Notification API 重复，易误触） ==========
            const enableTeamsToastWatcher = () => {
                window.__teams_toast_watch_enabled = true;
            };
            window.__teamsEnableTeamsToastWatcher = enableTeamsToastWatcher;
            setTimeout(enableTeamsToastWatcher, 800);

            // ========== 4.5 语音/视频来电检测（来电 UI 不在聊天流里，需单独监听） ==========
            const enableIncomingCallDetection = () => {
                if (window.__teams_incoming_call_enabled) return;
                window.__teams_incoming_call_enabled = true;

                const CALL_SELECTORS = [
                    '[data-tid="calling-screen"]',
                    '[data-tid="incoming-call"]',
                    '[data-tid="toast-incoming-call"]',
                    '[data-tid="calling-notification"]',
                    '[data-tid="preCallUX"]',
                    '[data-tid*="incomingCall"]',
                    '[data-tid*="incoming-call"]',
                    '[data-tid*="IncomingCall"]',
                    '[data-tid*="ringing"]',
                    '[data-tid="callingScreenContainer"]',
                    '[data-tid="call-accept"]',
                    '[data-tid="call-decline"]',
                    '[id*="incoming-call"]',
                    '[class*="IncomingCall"]',
                    '[class*="incoming-call"]',
                    '[class*="CallingNotification"]'
                ];
                // 仅用通话专属的 data-tid 判定“接听/拒绝”，绝不使用泛化的
                // [aria-label*="接受/Accept"]：聊天气泡的无障碍标签会带上消息原文，
                // 含“接受”二字的普通文字消息会被误判成来电（一直响）。
                const ACCEPT_SELECTORS = [
                    '[data-tid="accept-call"]', '[data-tid="acceptButton"]',
                    '[data-tid*="accept-audio"]', '[data-tid*="accept-video"]',
                    '[data-tid="call-accept"]'
                ];
                const DECLINE_SELECTORS = [
                    '[data-tid="decline-call"]', '[data-tid="rejectButton"]',
                    '[data-tid="call-decline"]'
                ];

                // 元素是否真正可见（排除隐藏/预渲染/模板节点导致的误判）
                // 注意：后台账号的 WebView2 窗口未显示，页面几何尺寸为 0，
                // 这里的“几何可见性”只用于弱信号（aria/文本）兜底，避免聊天“接受”误判。
                const isVisible = (el) => {
                    if (!el || el.nodeType !== 1) return false;
                    try {
                        const r = el.getBoundingClientRect();
                        if (r.width < 4 || r.height < 4) return false;
                        if (r.bottom < 0 || r.right < 0) return false;
                        if (r.top > (window.innerHeight || 0) + 40) return false;
                        const st = window.getComputedStyle(el);
                        if (!st) return true;
                        if (st.display === 'none') return false;
                        if (st.visibility === 'hidden' || st.visibility === 'collapse') return false;
                        if (parseFloat(st.opacity || '1') < 0.05) return false;
                        if (el.offsetParent === null && st.position !== 'fixed') return false;
                    } catch (e) {}
                    return true;
                };
                // 元素是否“已挂载且未被显式隐藏”（不依赖几何尺寸）。
                // 用于强信号（通话专属 data-tid 接听/拒绝按钮）：这些 data-tid
                // 聊天消息绝不会有，因此即便后台窗口几何为 0 也可放心判定为来电，
                // 仅排除 display:none / visibility:hidden / opacity≈0 的预渲染模板。
                const isPresent = (el) => {
                    if (!el || el.nodeType !== 1) return false;
                    if (!el.isConnected) return false;
                    try {
                        const st = window.getComputedStyle(el);
                        if (!st) return true;
                        if (st.display === 'none') return false;
                        if (st.visibility === 'hidden' || st.visibility === 'collapse') return false;
                        if (parseFloat(st.opacity || '1') < 0.05) return false;
                    } catch (e) {}
                    return true;
                };
                const queryAnyVisible = (selList) => {
                    for (const sel of selList) {
                        let els;
                        try { els = document.querySelectorAll(sel); } catch (e) { continue; }
                        for (const el of els) {
                            if (isVisible(el)) return el;
                        }
                    }
                    return null;
                };
                const queryAnyPresent = (selList) => {
                    for (const sel of selList) {
                        let els;
                        try { els = document.querySelectorAll(sel); } catch (e) { continue; }
                        for (const el of els) {
                            if (isPresent(el)) return el;
                        }
                    }
                    return null;
                };
                // 容器内是否含“接听 / 拒绝”通话专属按钮（来电的决定性特征）。
                // 用 isPresent（不依赖几何尺寸），保证后台隐藏窗口也能命中。
                const hasCallActionInside = (root) => {
                    if (!root) return false;
                    try {
                        const a = root.querySelector(ACCEPT_SELECTORS.join(','));
                        if (a && isPresent(a)) return true;
                    } catch (e) {}
                    try {
                        const d = root.querySelector(DECLINE_SELECTORS.join(','));
                        if (d && isPresent(d)) return true;
                    } catch (e) {}
                    return false;
                };

                // 通话接听/拒绝按钮兜底：必须是真正且可见的按钮，且 aria-label 中
                // “接听/接受/answer/accept” 与 “来电/通话/呼叫/call” 相邻出现才算，
                // 单独的“接受”二字（聊天内容）不会命中。
                const findCallActionButton = () => {
                    let nodes;
                    try {
                        nodes = document.querySelectorAll(
                            'button[aria-label], [role="button"][aria-label]'
                        );
                    } catch (e) { return null; }
                    const re = new RegExp(
                        '(接听|接受|应答|answer|accept)[^]{0,10}(来电|通话|呼叫|call)'
                        + '|(来电|通话|呼叫|call)[^]{0,10}(接听|接受|应答|answer|accept)'
                        + '|(拒绝|谢绝|decline|reject)[^]{0,10}(来电|通话|呼叫|call)',
                        'i'
                    );
                    for (const el of nodes) {
                        const al = el.getAttribute('aria-label') || '';
                        if (re.test(al) && isVisible(el)) return el;
                    }
                    return null;
                };

                // 找到正在显示的来电 UI 根节点。
                // 关键：来电必有“可见的接听 + 可见的拒绝按钮”。仅靠 class/data-tid
                // 含 calling/incoming/ringing 的节点（可能隐藏/预渲染/为拨出或通话中）
                // 一律不算来电，彻底避免发图片/文字时误报。
                const findCallRoot = () => {
                    // 1) 最强信号：通话专属的接听 + 拒绝按钮同时挂载（不依赖几何尺寸，
                    //    后台隐藏窗口也能命中；这些 data-tid 聊天消息绝不会有）
                    const accept = queryAnyPresent(ACCEPT_SELECTORS);
                    const decline = queryAnyPresent(DECLINE_SELECTORS);
                    if (accept && decline) {
                        return accept.closest(
                            '[role="dialog"], [data-tid], section, article, div'
                        ) || accept;
                    }
                    // 2) 通话专属容器已挂载，且容器内确有接听/拒绝按钮
                    const direct = queryAnyPresent(CALL_SELECTORS);
                    if (direct && hasCallActionInside(direct)) return direct;
                    // 3) aria-label 组合按钮可见，且其所在容器内还有可见通话按钮
                    const callBtn = findCallActionButton();
                    if (callBtn) {
                        const cont = callBtn.closest(
                            '[role="dialog"], [data-tid], section, article, div'
                        );
                        if (cont && hasCallActionInside(cont)) return cont;
                    }
                    // 4) 文本兜底：可见弹层含来电字样，且层内确有可见通话操作按钮
                    let layers;
                    try {
                        layers = document.querySelectorAll(
                            '[role="dialog"], [data-tid*="toast"], [class*="calling"], [class*="incoming"]'
                        );
                    } catch (e) { layers = []; }
                    for (const layer of layers) {
                        if (!isVisible(layer)) continue;
                        const t = (layer.innerText || layer.textContent || '');
                        if (!/来电|正在呼叫|incoming call|is calling|ringing/i.test(t)) continue;
                        if (hasCallActionInside(layer)) return layer;
                    }
                    return null;
                };

                const isVideoCall = (root) => {
                    if (!root) return false;
                    try {
                        if (root.querySelector(
                            '[data-tid*="video"], [aria-label*="视频"], [aria-label*="Video" i], '
                            + '[data-tid="accept-video"]'
                        )) return true;
                    } catch (e) {}
                    const t = (root.innerText || root.textContent || '');
                    return /视频通话|视频来电|video call/i.test(t);
                };

                const parseCallerFromLabel = (label) => {
                    const s = String(label || '').trim();
                    if (!s) return '';
                    const patterns = [
                        /(?:来自|来自：)\s*([^，。,]+)/,
                        /接听\s*(.+?)\s*的(?:来电|通话|呼叫)/,
                        /(.+?)\s*的(?:视频|语音)?来电/,
                        /(?:Accept|Answer)\s+(?:video\s+)?call\s+from\s+(.+?)(?:'s)?$/i,
                        /(?:Accept|Answer)\s+(.+?)(?:'s)?\s+(?:video\s+)?call/i,
                        /(.+?)\s+is\s+calling/i,
                        /(.+?)\s+正在呼叫/i
                    ];
                    for (const re of patterns) {
                        const m = s.match(re);
                        if (m && m[1]) {
                            const name = m[1].trim();
                            if (name && !/^(来电|呼叫|通话|call|video|audio)$/i.test(name)) return name;
                        }
                    }
                    return '';
                };

                const extractCaller = (root) => {
                    const tryName = (v) => {
                        const n = String(v || '').trim();
                        if (!n || n.length > 40) return '';
                        if (/^(来电|正在呼叫|邀请你加入|语音通话|视频通话|某人)$/i.test(n)) return '';
                        return n;
                    };
                    const scopes = [];
                    if (root) scopes.push(root);
                    try {
                        document.querySelectorAll(
                            '[data-tid*="incoming"], [data-tid*="calling"], [class*="incoming"], [class*="Calling"]'
                        ).forEach(el => scopes.push(el));
                    } catch (e) {}
                    const sels = [
                        '[data-tid="calling-participant-name"]',
                        '[data-tid="participant-display-name"]',
                        '[data-tid*="caller"]',
                        '[data-tid*="participant-name"]',
                        '[data-tid="title"]',
                        '[class*="caller"]',
                        '[class*="display-name"]',
                        '[class*="participant"] [role="heading"]'
                    ];
                    for (const scope of scopes) {
                        for (const s of sels) {
                            try {
                                const el = scope.querySelector && scope.querySelector(s);
                                const v = tryName(el && (el.innerText || el.textContent || ''));
                                if (v) return v;
                            } catch (e) {}
                        }
                    }
                    try {
                        const btns = document.querySelectorAll(
                            ACCEPT_SELECTORS.concat(DECLINE_SELECTORS).join(',')
                        );
                        for (const btn of btns) {
                            const v = parseCallerFromLabel(btn.getAttribute('aria-label'));
                            if (v) return v;
                        }
                    } catch (e) {}
                    for (const scope of scopes) {
                        const t = (scope.innerText || scope.textContent || '').trim();
                        const lines = t.split(/[\r\n]+/).map(s => s.trim()).filter(Boolean);
                        for (const line of lines) {
                            const fromLabel = parseCallerFromLabel(line);
                            if (fromLabel) return fromLabel;
                            const cleaned = line
                                .replace(/(来电|正在呼叫|邀请你加入|视频通话|语音通话|incoming call|is calling|ringing)/ig, '')
                                .trim();
                            const v = tryName(cleaned);
                            if (v) return v;
                        }
                    }
                    // 全局 aria-label 扫描：弹层/按钮上常写“来自 X 的来电 / X is calling”
                    try {
                        const labelled = document.querySelectorAll('[aria-label]');
                        for (const el of labelled) {
                            const al = el.getAttribute('aria-label') || '';
                            if (!/来电|正在呼叫|呼叫|calling|incoming|call from/i.test(al)) continue;
                            const v = parseCallerFromLabel(al);
                            if (v) return v;
                        }
                    } catch (e) {}
                    // document.title 兜底：来电时常含呼叫者名字
                    try {
                        const tt = (document.title || '').trim();
                        const v = parseCallerFromLabel(tt);
                        if (v) return v;
                    } catch (e) {}
                    return '某人';
                };

                const scheduleCallEnd = () => {
                    if (window.__teams_call_end_timer) return;
                    window.__teams_call_end_timer = setTimeout(() => {
                        window.__teams_call_end_timer = null;
                        if (findCallRoot()) return;
                        if (!window.__teams_call_ui_active) return;
                        window.__teams_call_ui_active = false;
                        window.__teams_call_last_notify = 0;
                        window.__teams_call_notified_once = false;
                        window.__teams_call_caller_name = '';
                        const count = window.__teamsReadUnreadCount
                            ? window.__teamsReadUnreadCount() : 0;
                        if (window.__externalNotificationCallback) {
                            window.__externalNotificationCallback(
                                'call_end', '', '', count
                            );
                        }
                    }, __CALL_END_DEBOUNCE_MS__);
                };
                const cancelCallEnd = () => {
                    if (window.__teams_call_end_timer) {
                        clearTimeout(window.__teams_call_end_timer);
                        window.__teams_call_end_timer = null;
                    }
                };

                const tick = () => {
                    const root = findCallRoot();
                    if (!root) {
                        if (window.__teams_call_ui_active) {
                            scheduleCallEnd();
                        }
                        return;
                    }
                    cancelCallEnd();
                    if (window.__TEAMS_NOTIFICATIONS_OFF) {
                        return;
                    }
                    window.__teams_call_ui_active = true;
                    const now = Date.now();
                    const first = !window.__teams_call_notified_once;
                    const gapMs = first ? 0 : 4000;
                    if (
                        !first
                        && window.__teams_call_last_notify
                        && now - window.__teams_call_last_notify < gapMs
                    ) {
                        return;
                    }
                    window.__teams_call_last_notify = now;
                    window.__teams_call_notified_once = true;
                    const video = isVideoCall(root);
                    let caller = extractCaller(root);
                    if (caller && caller !== '某人') {
                        window.__teams_call_caller_name = caller;
                    } else if (window.__teams_call_caller_name) {
                        caller = window.__teams_call_caller_name;
                    }
                    const type = video ? 'incoming_video' : 'incoming_call';
                    const message = video ? '邀请你视频通话' : '邀请你语音通话';
                    const count = window.__teamsReadUnreadCount ? window.__teamsReadUnreadCount() : 0;
                    if (window.__externalNotificationCallback) {
                        window.__externalNotificationCallback(type, caller, message, count);
                    }
                };

                window.__teams_call_last_notify = 0;
                window.__teams_call_ui_active = false;
                window.__teams_call_notified_once = false;
                window.__teams_call_end_timer = null;
                const __callPollMs = (window.__teamsxRuntimeMode === 'warm_notify')
                    ? __WARM_CALL_DETECT_POLL_MS__ : __CALL_DETECT_POLL_MS__;
                // 轮询 + 观察双保险：来电 UI 一出现尽快触发
                window.__teams_call_poll = setInterval(tick, __callPollMs);
                try {
                    const obs = new MutationObserver(__teamsxThrottle(tick, 150));
                    obs.observe(document.body, { childList: true, subtree: true });
                    window.__teams_call_observer = obs;
                } catch (e) {}
                setTimeout(tick, 300);
            };
            window.__teamsEnableIncomingCallDetection = enableIncomingCallDetection;
            setTimeout(enableIncomingCallDetection, 200);
        })();
        """
        js_code = js_code.replace(
            "__CALL_DETECT_POLL_MS__", str(int(CALL_DETECT_POLL_MS))
        )
        js_code = js_code.replace(
            "__CALL_END_DEBOUNCE_MS__", str(int(CALL_END_DEBOUNCE_MS))
        )
        js_code = js_code.replace(
            "__NOTIFY_TITLE_SYNC_MIN_MS__", str(int(NOTIFY_TITLE_SYNC_MIN_MS))
        )
        js_code = js_code.replace(
            "__TITLE_BADGE_POLL_MS__", str(int(TITLE_BADGE_POLL_MS))
        )
        js_code = js_code.replace(
            "__REALTIME_SCAN_MS__", str(int(REALTIME_SCAN_MS))
        )
        js_code = js_code.replace(
            "__CHATLIST_SCAN_MS__", str(int(CHATLIST_SCAN_MS))
        )
        js_code = js_code.replace(
            "__TOAST_SCAN_MS__", str(int(TOAST_SCAN_MS))
        )
        js_code = js_code.replace(
            "__MUTE_ALL_POLL_MS__", str(int(MUTE_ALL_POLL_MS))
        )
        js_code = js_code.replace(
            "__WARM_TITLE_POLL_MS__", str(int(WARM_TITLE_POLL_MS))
        )
        js_code = js_code.replace(
            "__WARM_CALL_DETECT_POLL_MS__", str(int(WARM_CALL_DETECT_POLL_MS))
        )
        self._wv2_doc_scripts.append(js_code)
        self._wv2_doc_scripts.append(STARSAIL_NOTIFY_JS)
        return

# ==================== 主窗口类 ====================

def _query_system_free_memory_mb() -> int:
    """返回系统可用物理内存（MB），失败时 -1。"""
    if sys.platform != "win32":
        return -1
    try:
        import ctypes

        class MEMORYSTATUSEX(ctypes.Structure):
            _fields_ = [
                ("dwLength", ctypes.c_ulong),
                ("dwMemoryLoad", ctypes.c_ulong),
                ("ullTotalPhys", ctypes.c_ulonglong),
                ("ullAvailPhys", ctypes.c_ulonglong),
                ("ullTotalPageFile", ctypes.c_ulonglong),
                ("ullAvailPageFile", ctypes.c_ulonglong),
                ("ullTotalVirtual", ctypes.c_ulonglong),
                ("ullAvailVirtual", ctypes.c_ulonglong),
                ("ullAvailExtendedVirtual", ctypes.c_ulonglong),
            ]

        stat = MEMORYSTATUSEX()
        stat.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(stat)):
            return int(stat.ullAvailPhys // (1024 * 1024))
    except Exception:
        pass
    return -1


def _query_process_image_memory_mb(image_name: str) -> int:
    """按进程映像名汇总工作集内存（MB）。"""
    if sys.platform != "win32":
        return 0
    try:
        import subprocess

        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        proc = subprocess.run(
            ["tasklist", "/FI", f"IMAGENAME eq {image_name}", "/FO", "CSV", "/NH"],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=flags,
        )
        if proc.returncode != 0:
            return 0
        total_kb = 0
        needle = image_name.lower()
        for line in (proc.stdout or "").splitlines():
            line = line.strip()
            if not line or needle not in line.lower():
                continue
            parts = [p.strip('"') for p in line.split('","')]
            if len(parts) < 5:
                continue
            mem = parts[4].replace(",", "").replace(" K", "").replace("K", "").strip()
            try:
                total_kb += int(mem)
            except ValueError:
                pass
        return int(total_kb // 1024)
    except Exception:
        return 0


def _query_teamsx_used_memory_mb() -> int:
    """TeamsX 占用内存：主进程 + WebView2 子进程（MB）。"""
    return _query_process_image_memory_mb("StarsailX.exe") + _query_process_image_memory_mb(
        "msedgewebview2.exe"
    )


def _query_webview2_process_stats() -> Tuple[int, int]:
    """返回 (msedgewebview2 进程数, 估算总工作集 MB)。供内存压力日志使用。"""
    if sys.platform != "win32":
        return 0, 0
    try:
        import subprocess

        flags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        proc = subprocess.run(
            [
                "tasklist",
                "/FI",
                "IMAGENAME eq msedgewebview2.exe",
                "/FO",
                "CSV",
                "/NH",
            ],
            capture_output=True,
            text=True,
            timeout=10,
            creationflags=flags,
        )
        if proc.returncode != 0:
            return 0, 0
        count = 0
        total_kb = 0
        for line in (proc.stdout or "").splitlines():
            line = line.strip()
            if not line or "msedgewebview2.exe" not in line.lower():
                continue
            parts = [p.strip('"') for p in line.split('","')]
            if len(parts) < 5:
                continue
            count += 1
            mem = parts[4].replace(",", "").replace(" K", "").replace("K", "").strip()
            try:
                total_kb += int(mem)
            except ValueError:
                pass
        return count, int(total_kb // 1024)
    except Exception:
        return 0, 0


def _clamp_float(val: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, float(val)))


def _adaptive_idle_sec_for_online(online: int) -> float:
    """账号越多，闲置门槛越短（10 号≈8min，25 号≈5min，40 号≈2min）。"""
    online = max(1, int(online))
    return _clamp_float(
        ADAPTIVE_RECYCLE_IDLE_BASE_SEC
        - (online - 10) * ADAPTIVE_RECYCLE_IDLE_PER_ACCOUNT_SEC,
        ADAPTIVE_RECYCLE_IDLE_MIN_SEC,
        ADAPTIVE_RECYCLE_IDLE_BASE_SEC,
    )


def _adaptive_target_high_mb(online: int) -> int:
    online = max(1, int(online))
    return int(
        ADAPTIVE_RECYCLE_TARGET_BASE_MB
        + online * ADAPTIVE_RECYCLE_TARGET_PER_ACCOUNT_MB
    )


def _memory_ctrl_prune_samples(
    samples: deque, *, now: float, window_sec: float
) -> None:
    cutoff = float(now) - float(window_sec)
    while samples and float(samples[0][0]) < cutoff:
        samples.popleft()


def _memory_ctrl_compute_trends(
    samples: deque, *, now: float, window_sec: float
) -> Tuple[float, float]:
    """返回 (free_trend_mb_per_min, used_trend_mb_per_min)；样本不足时 0,0。"""
    cutoff = float(now) - float(window_sec)
    window: List[Tuple[float, int, int, int, int]] = [
        s for s in samples if float(s[0]) >= cutoff
    ]
    if len(window) < int(MEMORY_CTRL_TREND_MIN_SAMPLES):
        return 0.0, 0.0
    t0, free0, used0, _, _ = window[0]
    t1, free1, used1, _, _ = window[-1]
    dt_min = max(0.05, (float(t1) - float(t0)) / 60.0)
    free_trend = (float(free1) - float(free0)) / dt_min
    used_trend = (float(used1) - float(used0)) / dt_min
    return free_trend, used_trend


def _query_process_working_set_mb(pid: int) -> int:
    if sys.platform != "win32" or pid <= 0:
        return 0
    try:
        import ctypes

        PROCESS_QUERY_INFORMATION = 0x0400
        handle = ctypes.windll.kernel32.OpenProcess(
            PROCESS_QUERY_INFORMATION, False, int(pid)
        )
        if not handle:
            return 0
        try:
            class PROCESS_MEMORY_COUNTERS(ctypes.Structure):
                _fields_ = [
                    ("cb", ctypes.c_ulong),
                    ("PageFaultCount", ctypes.c_ulong),
                    ("PeakWorkingSetSize", ctypes.c_size_t),
                    ("WorkingSetSize", ctypes.c_size_t),
                    ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
                    ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
                    ("PagefileUsage", ctypes.c_size_t),
                    ("PeakPagefileUsage", ctypes.c_size_t),
                ]

            pmc = PROCESS_MEMORY_COUNTERS()
            pmc.cb = ctypes.sizeof(PROCESS_MEMORY_COUNTERS)
            if ctypes.windll.psapi.GetProcessMemoryInfo(
                handle, ctypes.byref(pmc), pmc.cb
            ):
                return int(pmc.WorkingSetSize // (1024 * 1024))
        finally:
            ctypes.windll.kernel32.CloseHandle(handle)
    except Exception:
        pass
    return 0


def _query_widget_process_id(widget) -> int:
    if widget is None or sys.platform != "win32":
        return 0
    try:
        import ctypes

        hwnd = int(widget.winId())
        if hwnd <= 0:
            return 0
        pid = ctypes.c_ulong(0)
        ctypes.windll.user32.GetWindowThreadProcessId(
            hwnd, ctypes.byref(pid)
        )
        return int(pid.value or 0)
    except Exception:
        return 0


class MainWindow(QMainWindow):
    """主窗口 - 优化版本"""
    _memoryStatsReady = pyqtSignal(int, int, int, int)

    def __init__(self):
        super().__init__()
        try:
            # 初始化组件
            self.db = Database()
            self.web_views: Dict[int, TeamsWebView] = {}
            self.suspended_webviews: Dict[int, TeamsWebView] = {}
            self._image_helper = ImageClipboardHelper(self)
            self.webview_pool = WebViewPool()
            self.badge_cache: SafeDict = SafeDict()
            self.current_account_id: Optional[int] = None
            self.check_timer: Optional[QTimer] = None
            self.memory_timer: Optional[QTimer] = None
            self._memory_guard_timer: Optional[QTimer] = None
            self._memory_light_timer: Optional[QTimer] = None
            self._memory_guard_debounce_timer: Optional[QTimer] = None
            self._notify_waker_timer: Optional[QTimer] = None
            self._waker_index: int = 0
            self._memory_pressure = False
            self._memory_emergency_active = False
            self._low_memory_since = 0.0
            self._last_emergency_trim_at = 0.0
            self._last_account_switch_at = 0.0
            self._adaptive_recycle_last_at = 0.0
            self._adaptive_recycle_next_interval_sec = float(
                ADAPTIVE_RECYCLE_DECISION_MIN_SEC
            )
            self._adaptive_recycle_last_free_mb = -1
            self._adaptive_recycle_pressure = "ok"
            self._adaptive_recycle_renderer_prev = -1
            self._adaptive_recycle_storm_until = 0.0
            self._adaptive_recycle_account_last: Dict[int, float] = {}
            self._adaptive_recycle_batch_pending = 0
            self._memory_ctrl_samples: deque = deque()
            self._memory_ctrl_state: Dict[str, object] = {}
            self._memory_ctrl_last_logged_level = "ok"
            self._memory_ctrl_last_recycle_effective = False
            self._memory_ctrl_last_recycle_ineffective = False
            self._memory_groom_active = False
            self._memory_groom_target_aid: Optional[int] = None
            self._memory_groom_restore_id: Optional[int] = None
            self._memory_groom_aggressive = False
            self._memory_groom_account_last: Dict[int, float] = {}
            self._memory_groom_rr_index = 0
            self._memory_groom_timer: Optional[QTimer] = None
            self._enforce_low_mem_last_at = 0.0
            self._oom_unload_since = 0.0
            self._memory_guard_last_free_mb = -1
            self._memory_guard_last_used_mb = 0
            self._memory_guard_running = False
            self._memory_guard_last_full_at = 0.0
            self._lifecycle_cur_id: Optional[int] = None
            self._memoryStatsReady.connect(self._on_memory_stats_ready)
            self.image_check_timer: Optional[QTimer] = None
            self.is_closing = False
            self._shutdown_started = False
            self._shutdown_finished = False
            self._round_mask_cache: Dict[Tuple[int, int, int], QBitmap] = {}
            self._corner_mask_cache: Dict[Tuple[int, int, int, int], QBitmap] = {}
            self._chrome_mask_timer: Optional[QTimer] = None
            self._cache_clean_running = False
            self._cache_clean_thread: Optional[QThread] = None
            self.check_queue = deque()
            self._current_group_id = 0
            self._all_accounts_cache: List[Tuple] = []
            self._window_drag_active = False
            self._sidebar_collapsed = False
            self._sidebar_last_width = SIDEBAR_DEFAULT_WIDTH
            self._resize_active = False
            self._fast_mask_key: Optional[Tuple[int, int, int, int]] = None
            self._resize_settle_timer: Optional[QTimer] = None
            self._sidebar_chrome_key: Optional[Tuple] = None
            self._live_layout_timer: Optional[QTimer] = None
            self._badge_pending: Dict[int, int] = {}
            self._badge_debounce_timers: Dict[int, QTimer] = {}
            self._badge_poll_index = 0
            self._notify_sound_global_last: float = 0.0
            self._notify_sound_suppress_until: float = 0.0
            self._notify_startup_arm_until: float = 0.0
            self._notify_baseline_locked: Set[int] = set()
            self._notify_last_unread: Dict[int, int] = {}
            self._notify_sound_fired_at_count: Dict[int, int] = {}
            self._msg_notify_dedup: Dict[Tuple[int, str], float] = {}
            self._api_notify_dedup: Dict[Tuple[int, str], float] = {}
            self._memory_tier_last_trim: Dict[int, float] = {}
            self._memory_guard_wv2_count: int = -1
            self._memory_guard_wv2_mb: int = 0
            self._msg_sound_last_at: float = 0.0
            self._msg_sound_last_by_account: Dict[int, float] = {}
            self._call_ring_loop_timer: Optional[QTimer] = None
            self._call_ring_active_aid: Optional[int] = None
            self._call_ring_started_at: float = 0.0
            self._call_ring_last: Dict[int, float] = {}
            self._call_end_pending: Dict[int, float] = {}
            self._call_sessions: Dict[int, dict] = {}
            self._call_dismiss_watcher: Optional[QFileSystemWatcher] = None
            self._notify_ring_timer: Optional[QTimer] = None
            self._notify_ring_pending = False
            self._notify_sound_ready = False
            self._notify_sound_play_pending = False
            self._notify_sound_dl_lock = threading.Lock()
            self._teams_notify_sound_path: Optional[str] = None
            self._teams_call_sound_path: Optional[str] = None
            self._notify_sound_player = None
            self._notify_sound_output = None
            self._call_sound_player = None
            self._call_sound_output = None
            self._call_sound_ready = False
            self._call_tray_icon: Optional[QSystemTrayIcon] = None
            self._app_tray_icon: Optional[QSystemTrayIcon] = None
            self._force_quit = False
            self._close_dialog_open = False
            self._close_dialog = None
            self._taskbar_badge = get_taskbar_badge_controller()
            self._lock_overlay: Optional[QWidget] = None
            self._lock_input: Optional[QLineEdit] = None
            self._lock_unload_queue: List[int] = []
            self._lock_teardown_active = False
            self._app_locked = False
            self._main_splitter: Optional[QSplitter] = None
            self._theme_light = True
            self._teams_recover_running = False
            self._teams_load_failures = 0
            self._last_teams_recover_at = 0.0

            self._switch_target_id: Optional[int] = None
            self._switch_debounce_timer: Optional[QTimer] = None
            self._trim_suspended_scheduled = False

            # 设置窗口
            self._native_frame = bool(USE_NATIVE_WINDOW_FRAME)
            if self._native_frame:
                # 原生窗口：保留系统样式以获得 DWM 动画/贴边/阴影，
                # 用 nativeEvent(WM_NCCALCSIZE) 隐藏可见边框，自绘标题栏。
                self.setWindowFlags(Qt.WindowType.Window)
            else:
                self.setWindowFlags(
                    Qt.WindowType.FramelessWindowHint
                    | Qt.WindowType.Window
                    | Qt.WindowType.WindowMinimizeButtonHint
                )
                self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
            QApplication.instance().installEventFilter(self)
            if self._native_frame:
                self.resize(1280, 800)
            else:
                outer_w = 1280 + 2 * WINDOW_SHADOW_MARGIN
                outer_h = 800 + 2 * WINDOW_SHADOW_MARGIN
                self.resize(outer_w, outer_h)
            self.setMinimumSize(900, 600)
            self._resize_cursor_active = False
            self._active_resize_edges = None
            self.setMouseTracking(True)

            # 设置 UI
            self.setup_ui()
            self.apply_theme(True)

            # 设置窗口标题
            self.setWindowTitle("StarsailX")
            base_icon = AppPaths.app_qicon()
            if not base_icon.isNull():
                self.setWindowIcon(base_icon)
                QApplication.instance().setWindowIcon(base_icon)

            # 初始化
            self.load_accounts()
    
            self._prepare_notify_sound_startup()
            QTimer.singleShot(
                int(NOTIFY_STARTUP_ARM_SEC * 1000), self._finish_notify_startup_arm
            )
            # 延后启动后台轮询，避免与首屏 WebView 初始化争抢主线程
            QTimer.singleShot(1200, self.start_notification_check)
            QTimer.singleShot(1800, self.start_memory_cleanup)
            QTimer.singleShot(2200, self.start_memory_guard)
            QTimer.singleShot(2400, self.start_daily_cache_cleanup)
            self._setup_call_dismiss_watcher()
            self._setup_app_tray()

            print(
                f"TeamsX 启动完成 · 数据: {AppPaths.data_root()} · "
                f"在线账号: 不限制 · "
                f"WebView2: {'共享Profile' if os.environ.get('TEAMSX_MULTI_PROFILE','1') not in ('0','false','no','off') else '独立进程'}"
            )
        except Exception as e:
            print(f"主窗口初始化失败: {e}")
            QMessageBox.critical(None, "初始化失败", f"程序初始化失败: {str(e)}")
            sys.exit(1)

    def apply_theme(self, light: bool):
        """切换深/浅主题（无提示）"""
        global CURRENT_THEME
        self._theme_light = light
        CURRENT_THEME = "light" if light else "dark"
        self.setStyleSheet(APP_LIGHT_STYLE if light else APP_DARK_STYLE)
        self._apply_window_shadow_theme(light)
        if hasattr(self, "account_list"):
            self.account_list.viewport().update()
        self._apply_sidebar_chrome_theme(light)
        self._sync_window_chrome()
        self._style_lock_overlay()

    def toggle_theme(self):
        self.apply_theme(not self._theme_light)

    def _apply_sidebar_chrome_theme(self, light: bool):
        if light:
            header = "font-size: 14px; font-weight: bold; color: #1a1a1a;"
            group_lbl = "font-size: 13px; font-weight: 600; color: #1a1a1a; padding-right: 2px;"
            status = "color: #0078d4; font-size: 11px; font-weight: bold; padding-left: 2px;"
            bottom = "background-color: #f0f0f0; border-top: 1px solid #e0e0e0;"
            sidebar_bg = "#f6f6f6"
        else:
            sidebar_bg = ""
            header = "font-size: 14px; font-weight: bold; color: #e0e0e0;"
            group_lbl = "font-size: 13px; font-weight: 600; color: #e0e0e0; padding-right: 2px;"
            status = "color: #00d4ff; font-size: 11px; font-weight: bold; padding-left: 2px;"
            bottom = "background-color: #252525; border-top: 1px solid #3c3c3c;"
        if hasattr(self, "_header_title_label"):
            self._header_title_label.setStyleSheet(header)
        if hasattr(self, "_group_label"):
            self._group_label.setStyleSheet(group_lbl)
        if hasattr(self, "status_label"):
            self.status_label.setStyleSheet(status)

        def _hard_exit() -> None:
            try:
                sys.stdout.flush()
                sys.stderr.flush()
            except Exception:
                pass
            os._exit(0)

        # 给 Qt 一点时间处理最后的关闭事件，再强制结束进程
        QTimer.singleShot(600, _hard_exit)

# ==================== 主程序入口 ====================

if __name__ == "__main__":
    from starsailx.__main__ import main

    main()

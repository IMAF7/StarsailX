# -*- coding: utf-8 -*-
"""启动前冒烟测试（不显示窗口）。"""
from __future__ import annotations

import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

from PyQt6.QtWidgets import QApplication

app = QApplication([])
from StarsailX import MainWindow  # noqa: E402

win = MainWindow()
assert hasattr(win, "update_status")
assert hasattr(win, "_sync_empty_page_theme")
assert win._theme_light is True
win._sync_empty_page_theme()
bg = win._empty_page.styleSheet()
assert "#f3f3f3" in bg, bg
win.apply_theme(False)
assert "#1e1e1e" in win._empty_page.styleSheet()
win.apply_theme(True)
assert "#f3f3f3" in win._empty_page.styleSheet()
win.go_home()
win.update_status("test")
print("smoke ok")

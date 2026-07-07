# -*- coding: utf-8 -*-
"""恢复精简时误删的 Database / UI / 桥接类。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "TeamsX.py"
if not SRC.is_file():
    SRC = Path(r"c:\Users\admin\Desktop\新建文件夹\DDDA\TeamsX.py")
DST = ROOT / "StarsailX.py"

SKIP_CLASSES = {
    "SidebarContentHost",
    "_GroupComboCenterDelegate",
    "GroupFilterComboBox",
    "AccountGroupPickerDialog",
    "GroupManagePanel",
}


def extract_block(lines: list[str]) -> str:
    """从 AccountListWidget 之后到 WebView 类之前提取，跳过分组相关类。"""
    start = None
    end = None
    for i, line in enumerate(lines):
        if line.startswith("class SidebarContentHost"):
            start = i
        if line.startswith("# ==================== WebView"):
            end = i
            break
    if start is None or end is None:
        raise SystemExit("markers not found in TeamsX.py")

    out: list[str] = []
    i = start
    while i < end:
        line = lines[i]
        if line.startswith("class "):
            name = line.split("(")[0].replace("class ", "").strip()
            if name in SKIP_CLASSES:
                i += 1
                while i < end and not lines[i].startswith("class "):
                    i += 1
                continue
        out.append(line)
        i += 1
    return "".join(out)


def main() -> None:
    src_lines = SRC.read_text(encoding="utf-8").splitlines(keepends=True)
    block = extract_block(src_lines)
    if "class Database:" not in block:
        raise SystemExit("Database not in extracted block")
    if "class JsNotifyBridge" not in block:
        raise SystemExit("JsNotifyBridge not in extracted block")

    dst = DST.read_text(encoding="utf-8")
    marker = "# ==================== WebView 类 ===================="
    if marker not in dst:
        raise SystemExit("webview marker missing in StarsailX.py")
    if "class Database:" in dst:
        print("Database already present")
        return

    dst = dst.replace(marker, block + "\n" + marker, 1)
    DST.write_text(dst, encoding="utf-8")
    print("restored core classes before WebView")


if __name__ == "__main__":
    main()

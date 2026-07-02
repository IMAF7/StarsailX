# -*- coding: utf-8 -*-
"""删除分组相关类（不要删 Database）。"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "StarsailX.py"

SKIP = {
    "SidebarContentHost",
    "_GroupComboCenterDelegate",
    "GroupFilterComboBox",
    "AccountGroupPickerDialog",
    "GroupManagePanel",
}


def drop_class(text: str, name: str) -> str:
    key = f"class {name}"
    if key not in text:
        return text
    start = text.find(f"class {name}")
    rest = text[start + 1 :]
    nxt = rest.find("\nclass ")
    if nxt < 0:
        return text[:start]
    return text[:start] + rest[nxt + 1 :]


def main() -> None:
    for name in SKIP:
        old = TARGET.read_text(encoding="utf-8")
        new = drop_class(old, name)
        if new != old:
            TARGET.write_text(new, encoding="utf-8")
            print("dropped", name)


if __name__ == "__main__":
    main()

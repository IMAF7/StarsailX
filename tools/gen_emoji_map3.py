import re
import json

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()


def extract_i_block(name: str) -> str:
    marker = f'{name}={{"[TUIEmoji_Smile]":'
    start = s.find(marker)
    if start < 0:
        return ""
    i = start + len(name) + 1
    depth = 0
    in_str = False
    quote = ""
    while i < len(s):
        ch = s[i]
        if in_str:
            if ch == quote and s[i - 1] != "\\":
                in_str = False
        else:
            if ch in ('"', "`"):
                in_str = True
                quote = ch
            elif ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    return s[start : i + 1]
        i += 1
    return ""


block = extract_i_block("i$8")
pairs = re.findall(r'"\[TUIEmoji_([A-Za-z0-9_]+)\]":`(\[[^\]]+\])`', block)
zh = {f"[TUIEmoji_{a}]": b for a, b in pairs}

out = r"c:\Users\admin\Desktop\StarsailX\tools\emoji_zh_cn_map.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(zh, f, ensure_ascii=False, indent=2)

lines = ["const STARSAIL_TUI_EMOJI_TO_MOBILE = {"]
for k in sorted(zh.keys()):
    lines.append(f"    {json.dumps(k, ensure_ascii=False)}: {json.dumps(zh[k], ensure_ascii=False)},")
lines.append("};")
with open(r"c:\Users\admin\Desktop\StarsailX\tools\emoji_map_js.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

print("saved", len(zh))

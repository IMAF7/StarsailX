import re
import json

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

start = s.find('i$10={"[TUIEmoji_Smile]":')
chunk = s[start : start + 10000]
pairs = re.findall(r'"\[TUIEmoji_([A-Za-z0-9_]+)\]":`(\[[^\]]+\])`', chunk)
zh = {f"[TUIEmoji_{a}]": b for a, b in pairs}

# verify Chinese chars
cn_count = sum(1 for v in zh.values() if re.search(r"[\u4e00-\u9fff]", v))
print("total", len(zh), "with han", cn_count)

out = r"c:\Users\admin\Desktop\StarsailX\tools\emoji_zh_cn_map.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(zh, f, ensure_ascii=False, indent=2)

# generate JS object literal for embedding
lines = ["const STARSAIL_TUI_EMOJI_TO_MOBILE = {"]
for k in sorted(zh.keys()):
    lines.append(f"    {json.dumps(k, ensure_ascii=False)}: {json.dumps(zh[k], ensure_ascii=False)},")
lines.append("};")
js = "\n".join(lines)
with open(r"c:\Users\admin\Desktop\StarsailX\tools\emoji_map_js.txt", "w", encoding="utf-8") as f:
    f.write(js)
print("wrote emoji_map_js.txt", len(js))

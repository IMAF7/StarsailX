import re
import json

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

needle = '"[TUIEmoji_Smile]":'
idx = s.find(needle)
print("idx", idx)
chunk = s[idx : idx + 12000]
pairs = re.findall(r'"\[TUIEmoji_([A-Za-z0-9_]+)\]":`(\[[^\]]+\])`', chunk)
print("pairs from backtick", len(pairs))
if not pairs:
    pairs = re.findall(r'"\[TUIEmoji_([A-Za-z0-9_]+)\]":"(\[[^\]]+\])"', chunk)

mapping = {f"[TUIEmoji_{a}]": b for a, b in pairs}
print("mapping size", len(mapping))
for k in sorted(mapping)[:15]:
    print(k, "->", mapping[k])

out = r"c:\Users\admin\Desktop\StarsailX\tools\emoji_map.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(mapping, f, ensure_ascii=False, indent=2)

# find zh variant - search for 微笑 near TUIEmoji
for term in ["微笑", "期待", "呲牙", "Smile", "Expect"]:
    i = s.find(term)
    print(term, "at", i)
    if i >= 0:
        print(s[max(0,i-100):i+150])

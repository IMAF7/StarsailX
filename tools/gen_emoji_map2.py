import re
import json

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

start = s.find('i$10={"[TUIEmoji_Smile]":')
end = s.find("};", start) + 2
block = s[start:end]
print("block len", len(block))
print("first 200 chars repr:", repr(block[:200]))

pairs = re.findall(r'"\[TUIEmoji_([A-Za-z0-9_]+)\]":`(\[[^\]]+\])`', block)
print("pairs in block only", len(pairs))
zh = {f"[TUIEmoji_{a}]": b for a, b in pairs}

# find which i$ index is Chinese
for name in ["i$8", "i$9", "i$10", "i$11", "i$12", "i$13"]:
    st = s.find(f'{name}={{"[TUIEmoji_Smile]":')
    if st < 0:
        continue
    frag = s[st : st + 120]
    print(name, repr(frag))

with open(r"c:\Users\admin\Desktop\StarsailX\tools\emoji_zh_cn_map.json", "w", encoding="utf-8") as f:
    json.dump(zh, f, ensure_ascii=False, indent=2)

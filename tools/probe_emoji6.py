import re
import json

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

idx = s.find('i$10={"[TUIEmoji_Smile]":')
print("i$10 idx", idx)
chunk = s[idx : idx + 12000]
pairs = re.findall(r'"\[TUIEmoji_([A-Za-z0-9_]+)\]":`(\[[^\]]+\])`', chunk)
zh = {f"[TUIEmoji_{a}]": b for a, b in pairs}
print("zh cn", len(zh))
out = r"c:\Users\admin\Desktop\StarsailX\tools\emoji_zh_cn_map.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(zh, f, ensure_ascii=False, indent=2)

# Also extract unicode emoji alternative - search TIM face classic
# OpenIM / Tencent might use /::) style - search in bundle
for pat in ["/::)", "/::~", "[微笑]"]:
    print(pat, "count", s.count(pat))

# How emoji picker inserts - search for TUIEmoji in click handler context
for term in ["onEmojiClick", "handleEmoji", "selectEmoji", "emojiKey", "TUIEmoji_"]:
    c = s.count(term)
    if c:
        print(term, c)

# find emoji picker component snippet
m = re.search(r'.{0,200}uikit-emoji.{0,400}', s)
if m:
    print("uikit-emoji ctx:", m.group(0)[:600])

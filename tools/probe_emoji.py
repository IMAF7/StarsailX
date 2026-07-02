import re
import json

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

# emojiUrlMap
m = re.search(r"emojiUrlMap\s*=\s*(\{[^;]+\})", s)
if m:
    block = m.group(1).replace("`", '"')
    print("emojiUrlMap block:", block[:500])

# Find zh Emoji translation - look for TUIEmoji_Expect near Chinese
for key in ["TUIEmoji_Expect", "TUIEmoji_Smile"]:
    pat = rf'"{key}[^"]*":"([^"]+)"'
    hits = re.findall(pat, s)
    print(key, "name hits:", hits[:5])

# reverse: Chinese bracket emojis
cn = re.findall(r"\[[\u4e00-\u9fff]{1,4}\]", s)
print("cn bracket count", len(set(cn)))
print("sample", sorted(set(cn))[:20])

# Emoji translation object pattern
for m in re.finditer(r'"(\[TUIEmoji_[^"]+\])":"([^"]+)"', s):
    if m.group(1) == "[TUIEmoji_Expect]":
        print("Expect maps to:", m.group(2))
        break

# collect all TUI -> display name from translation
pairs = {}
for m in re.finditer(r'"(\[TUIEmoji_[^"]+\])":"([^"]+)"', s):
    k, v = m.group(1), m.group(2)
    if k.startswith("[TUIEmoji_") and not v.endswith(".png"):
        pairs[k] = v

print("translation pairs", len(pairs))
for k in sorted(pairs)[:15]:
    print(k, "->", pairs[k])

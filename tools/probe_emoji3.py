import re
import json

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

# extract i$11 or similar emoji translation objects
for mobj in re.finditer(r'(\w+)\s*=\s*\{("\[TUIEmoji_[^"]+"\]:[^}]+\})', s):
    name = mobj.group(1)
    if "TUIEmoji_Smile" in mobj.group(0):
        block = mobj.group(0)
        print("BLOCK", name, "len", len(block))
        # parse pairs
        pairs = re.findall(r'"\[TUIEmoji_([^"]+)\]":`(\[[^\]]+\])`', block)
        if not pairs:
            pairs = re.findall(r'"\[TUIEmoji_([^"]+)\]":"(\[[^\]]+\])"', block)
        print("pairs", len(pairs))
        for a, b in pairs[:10]:
            print(f"[TUIEmoji_{a}] -> {b}")

# find all objects with TUIEmoji_Smile
starts = [m.start() for m in re.finditer(r'"\[TUIEmoji_Smile\]"', s)]
print("Smile occurrences", len(starts))
for st in starts[:5]:
    print(s[st:st+400])

import re
import json

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

# emojiUrlMap keys
m = re.search(r"emojiUrlMap\s*=\s*(\{[^;]+\})", s)
url_map = {}
if m:
    block = m.group(1).replace("`", '"')
    url_map = json.loads(block)

print("url_map keys", len(url_map))

# Find zh-CN translation block containing TUIEmoji
idx = s.find("[TUIEmoji_Expect]")
while idx >= 0:
    ctx = s[max(0, idx - 80) : idx + 120]
    if "Expect" in ctx and ("期待" in ctx or "Emoji" in ctx):
        print("CTX:", ctx)
        break
    idx = s.find("[TUIEmoji_Expect]", idx + 1)

# Search pattern: [TUIEmoji_XXX]:[中文]
# i18n often: "[TUIEmoji_Expect]":"[期待]"
pat = r'"(\[TUIEmoji_[A-Za-z0-9_]+\])":"(\[[^\]]+\])"'
pairs = re.findall(pat, s)
# dedupe
seen = {}
for k, v in pairs:
    if k not in seen:
        seen[k] = v

print("key->cn bracket pairs", len(seen))
out = r"c:\Users\admin\Desktop\StarsailX\tools\emoji_map.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(seen, f, ensure_ascii=False, indent=2)
print("wrote", out)
for k in sorted(seen)[:20]:
    print(k, "->", seen[k])

# also check if unicode emojis used
pat2 = r'"(\[TUIEmoji_[A-Za-z0-9_]+\])":"([^"]{1,8})"'
pairs2 = []
for m in re.finditer(pat2, s):
    k, v = m.group(1), m.group(2)
    if not v.endswith(".png") and "emoji_" not in v:
        pairs2.append((k, v))

uniq2 = {}
for k, v in pairs2:
    if k not in uniq2:
        uniq2[k] = v
print("all text mappings", len(uniq2))

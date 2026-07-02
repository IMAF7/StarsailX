import re
import json

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

# Chinese map i$10
idx = s.find('i$10={"[TUIEmoji_Smile]":')
chunk = s[idx : idx + 12000]
pairs = re.findall(r'"\[TUIEmoji_([A-Za-z0-9_]+)\]":`(\[[^\]]+\])`', chunk)
zh = {f"[TUIEmoji_{a}]": b for a, b in pairs}
print("zh", len(zh))

# search send hooks
for term in [
    "transformTextWithEmojiNameToKey",
    "transformTextWithEmojiKeyToName",
    "insertEmoji",
    "emojiUrlMap",
    "uikit-emoji",
    "EmojiPicker",
    "message-input",
    "sendTextMessage",
    "createTextMessage",
]:
    print(term, s.count(term))

# context around transformTextWithEmojiNameToKey usage in send
term = "transformTextWithEmojiNameToKey"
i = 0
n = 0
while n < 5:
    i = s.find(term, i)
    if i < 0:
        break
    print("---", n, s[i - 80 : i + 200])
    i += len(term)
    n += 1

out = r"c:\Users\admin\Desktop\StarsailX\tools\emoji_zh_map.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(zh, f, ensure_ascii=False, indent=2)
print("wrote", out)

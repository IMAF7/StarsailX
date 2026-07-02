p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

# How messages display emoji in chat
for term in [
    "emojiUrlMap",
    "TIMFaceElem",
    "faceMessage",
    "transformTextWithEmojiKeyToName",
    "messageForShow",
    "uikit-face-message",
    "FaceMessage",
]:
    print(term, s.count(term))

idx = s.find("uikit-face-message")
if idx >= 0:
    print(s[idx - 200 : idx + 500])

idx = s.find("function buildSdkMessage")
print("--- buildSdkMessage ---")
print(s[idx : idx + 800])

# message rendering text with emoji
for pat in ["messageForShow", "transformTextWithEmojiKeyToName("]:
    i = 0
    n = 0
    while n < 2:
        i = s.find(pat, i)
        if i < 0:
            break
        print("---", pat, s[i : i + 250])
        i += len(pat)
        n += 1

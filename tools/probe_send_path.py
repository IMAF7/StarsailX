p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

terms = [
    "sendInputMessage",
    "sendMessage({type:`textMessage`",
    "createTextMessage",
    "sendPacket",
    "openim.sendmsg",
    "MsgBody",
    "transformTextWithEmojiNameToKey",
]
for term in terms:
    print(term, s.count(term))

idx = s.find("sendInputMessage:async")
print("--- sendInputMessage ---")
print(s[idx : idx + 1500])

idx = s.find("async function sendStructuredContent")
if idx < 0:
    idx = s.find("async function sendStructuredContent".replace("async ", ""))
if idx < 0:
    idx = s.find("function sendStructuredContent")
print("--- sendStructuredContent ---")
print(s[idx : idx + 1200])

# find actual sendMessage on chat store wrapper
for pat in ["sendMessage(e,t)", "sendMessage:async", ".sendMessage=function"]:
    j = s.find(pat)
    print(pat, j)
    if j >= 0:
        print(s[j : j + 600])

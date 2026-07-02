p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

# find sendmsg / send message protocol
for term in ["openim.sendmsg", "sendmsg", "MsgRandom", "TUIEmoji_Expect"]:
    print(term, s.count(term))

idx = s.find("openim.sendmsg")
if idx >= 0:
    print(s[idx - 100 : idx + 600])

# createFaceMessage
idx = s.find("createFaceMessage")
print("createFaceMessage", idx)
if idx >= 0:
    print(s[idx : idx + 400])

# Does mobile use [微笑] in payload examples?
idx = s.find("[微笑]")
print("[微笑] idx", idx)
if idx >= 0:
    print(repr(s[idx - 50 : idx + 80]))

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

idx = s.find("currentMsgInputStore")
print("count", s.count("currentMsgInputStore"))
for n in range(5):
    idx = s.find("currentMsgInputStore", idx)
    if idx < 0:
        break
    print("---", n, s[idx : idx + 700])
    idx += 1

# MsgInputStore sendMessage
for term in ["MsgInputStore", "msgInputStore", "sendMessage(e,t){return pd"]:
    print(term, s.count(term))

idx = s.find("class MsgInputStore")
if idx < 0:
    idx = s.find("MsgInputStore=class")
print("MsgInputStore idx", idx)
if idx >= 0:
    print(s[idx : idx + 2000])

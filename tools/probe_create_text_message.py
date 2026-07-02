p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

idx = s.find("createTextMessage(e)")
if idx < 0:
    idx = s.find("createTextMessage(e){")
print("createTextMessage def", idx)
print(s[idx : idx + 1200])

# MsgBody text in send
for term in ["MsgBody", "ElemType", "TIMTextElem", "textElem"]:
    print(term, s.count(term))

idx = s.find("TIMTextElem")
if idx >= 0:
    print(s[idx - 100 : idx + 400])

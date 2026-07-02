p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

for term in ["LoginStore", "buildSdkMessage", "textMessage", "createTextMessage"]:
    print(term, s.count(term))

idx = s.find("function buildSdkMessage")
if idx < 0:
    idx = s.find("buildSdkMessage(")
print("buildSdkMessage idx", idx)
print(s[idx : idx + 2500])

p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

idx = s.find("LoginStore=")
print("LoginStore= idx", idx)
print(s[idx : idx + 1500])

idx = s.find("getChat(){")
print("getChat idx", s.find("getChat()"))
print(s[s.find("getChat()") : s.find("getChat()") + 400])

# createTextMessage payload text
idx = s.find("createTextMessage({")
for n in range(3):
    idx = s.find("createTextMessage({", idx)
    if idx < 0:
        break
    print("---", s[idx : idx + 300])
    idx += 1

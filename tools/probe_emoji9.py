p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

for term in ["sendInputMessage", "sendMessage({type:`textMessage`", "createTextMessage"]:
    idx = 0
    n = 0
    print("===", term)
    while n < 2:
        idx = s.find(term, idx)
        if idx < 0:
            break
        print(s[idx - 60 : idx + 280])
        idx += len(term)
        n += 1

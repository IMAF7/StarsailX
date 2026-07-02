p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

idx = s.find("MessageInputStore")
print("count", s.count("MessageInputStore"))
idx = s.find("MessageInputStore.create")
print(s[idx : idx + 3000])

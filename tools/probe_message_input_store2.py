p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

needle = "MessageInputStore"
start = 0
while True:
    idx = s.find(needle, start)
    if idx < 0:
        break
    ctx = s[idx : idx + 120]
    if "create" in ctx or "class" in ctx or "sendMessage" in s[idx : idx + 2500]:
        print("IDX", idx, ctx[:80])
        if "sendMessage" in s[idx : idx + 4000]:
            print(s[idx : idx + 4000])
            print("=====")
    start = idx + len(needle)

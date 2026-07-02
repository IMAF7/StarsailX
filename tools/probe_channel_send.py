p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

for term in ["getChannel(", "sendMessage:async", "sendMessage(e,", "sendMessage:("]:
    idx = 0
    n = 0
    print("===", term)
    while n < 3:
        idx = s.find(term, idx)
        if idx < 0:
            break
        print(s[idx : idx + 500])
        print("---")
        idx += len(term)
        n += 1

# find channel snapshot sendMessage
idx = s.find("sendMessage:async")
while idx >= 0:
    ctx = s[idx - 200 : idx + 400]
    if "getChannel" in ctx or "channel" in ctx.lower():
        print("CHANNEL CTX", ctx)
        break
    idx = s.find("sendMessage:async", idx + 1)

# search sendMessage in conv store / channel
for pat in ["getSnapshot(){", "sendMessage({type", "async sendMessage"]:
    print(pat, s.find(pat))

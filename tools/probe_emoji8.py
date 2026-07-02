p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

# find Chinese map - look for 微笑 specifically
idx = s.find('"[TUIEmoji_Smile]":`[微笑]`')
print("cn smile idx", idx)
if idx < 0:
    # try unicode escape
    idx = s.find("TUIEmoji_Smile")
    while idx >= 0:
        frag = s[idx : idx + 80]
        if "Smile" in frag and "`[" in frag:
            print("frag", repr(frag))
            if s[idx:idx+5] != "TUIEm":  # skip
                pass
        idx = s.find("TUIEmoji_Smile", idx + 1)

# extract by searching 微笑
idx = s.find("`[微笑]`")
print("微笑 idx", idx)
if idx > 0:
    start = s.rfind("i$", idx - 200, idx)
    print("block start", start)
    chunk = s[start : start + 10000]
    import re
    pairs = re.findall(r'"\[TUIEmoji_([A-Za-z0-9_]+)\]":`(\[[^\]]+\])`', chunk)
    print("pairs", len(pairs))
    for a, b in pairs[:5]:
        print(f"[TUIEmoji_{a}] -> {b}")

# chatUIStore on window?
for term in ["chatUIStore", "createStore", "sendMessage"]:
    print(term, s.count(term))

# find sendMessage definition on chat
idx = s.find("sendMessage(e,t)")
if idx < 0:
    idx = s.find("sendMessage({")
print("sendMessage idx", idx)
print(s[idx : idx + 800])

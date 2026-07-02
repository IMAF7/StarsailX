p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

for term in ["transformElementsToServerFormat", "MsgBody", "TIMTextElem", "TextElem"]:
    idx = s.find(term)
    print(term, idx)
    if idx >= 0:
        print(s[idx : idx + 500])
        print("---")

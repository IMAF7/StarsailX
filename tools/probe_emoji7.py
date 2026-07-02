p = r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js"
with open(p, "r", encoding="utf-8", errors="ignore") as f:
    s = f.read()

for term in ["MessageContentType.EMOJI", "textMessage", "insertInputContent", "trimInputContent"]:
    print(term, s.count(term))

idx = s.find("MessageContentType.EMOJI")
for i in range(5):
    if idx < 0:
        break
    print("---", i, s[idx - 120 : idx + 350])
    idx = s.find("MessageContentType.EMOJI", idx + 1)

# sendMessage emoji handling
idx = s.find("sendStructuredContent")
print("sendStructuredContent", s[idx : idx + 1200])

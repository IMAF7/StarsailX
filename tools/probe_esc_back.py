data = open(r"c:\Users\admin\Desktop\StarsailX\tools\starsail_bundle.js", "r", encoding="utf-8", errors="ignore").read()
patterns = [
    "setActiveConversation(``)",
    "setActiveConversation('')",
    'setActiveConversation("")',
    "setActiveConversation(null)",
    "setActiveConversation(void 0)",
    "setActiveConversation()",
]
for pat in patterns:
  i = data.find(pat)
  print(pat, i)
  if i >= 0:
    print(data[i - 150 : i + len(pat) + 150])
    print("---")

# search back button click with setActiveConversation nearby
idx = 0
for _ in range(10):
    i = data.find("setActiveConversation", idx)
    if i < 0:
        break
    chunk = data[i : i + 200]
    if "Escape" in chunk or "back" in chunk.lower() or "Back" in chunk:
        print("HIT", data[i - 200 : i + 300])
        print("---")
    idx = i + 1

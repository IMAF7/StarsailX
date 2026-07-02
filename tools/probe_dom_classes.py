import re
from pathlib import Path

s = Path(__file__).resolve().parents[1] / "tools" / "starsail_bundle.js"
text = s.read_text(encoding="utf-8")
classes = set(re.findall(r"uikit-[a-zA-Z0-9_-]+", text))
emoji = sorted(c for c in classes if "emoji" in c.lower())
msg = sorted(c for c in classes if "message-input" in c.lower() or "message_input" in c.lower())
attach = sorted(c for c in classes if "attachment" in c.lower() or "picker" in c.lower())
print("emoji:", emoji)
print("message-input:", msg[:40])
print("picker/attach:", [c for c in attach if "emoji" in c.lower() or "attach" in c.lower()][:40])

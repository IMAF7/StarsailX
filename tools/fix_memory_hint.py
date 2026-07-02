from pathlib import Path
p = Path(__file__).resolve().parents[1] / "StarsailX.py"
t = p.read_text(encoding="utf-8")
t = t.replace(
    "            self._mem_hint_color = \"\"\n            self._refresh_memory_hint()\n",
    "",
)
t = t.replace(
    "        self._refresh_memory_hint()\n        self._refresh_default_status()",
    "        self._refresh_default_status()",
)
p.write_text(t, encoding="utf-8")
print("memory hints left:", t.count("_refresh_memory_hint"))

import re
import urllib.request

html = urllib.request.urlopen("https://starsail.vip/", timeout=15).read().decode("utf-8", "replace")
scripts = re.findall(r'<script[^>]+src="([^"]+)"', html)
print("scripts", len(scripts))
for s in scripts:
    print(s)

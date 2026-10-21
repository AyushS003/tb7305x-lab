import urllib.request
import re

url = "https://support.lenovo.com/us/en/downloads/ds101291-rescue-and-smart-assistant-lmsa"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
try:
    with urllib.request.urlopen(req) as resp:
        html = resp.read().decode("utf-8", errors="replace")
        links = re.findall(r'https?://[^\s"\'<>]+', html)
        for l in set(links):
            if any(k in l.lower() for k in ["setup", ".exe", ".zip", "download.lenovo.com"]):
                print("Found:", l)
except Exception as e:
    print("Error:", e)

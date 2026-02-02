import json
import re
import urllib.request

UA = "job-alerts/detect"

def fetch(url: str, max_bytes: int = 800_000) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "text/html,*/*"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return resp.read(max_bytes).decode("utf-8", errors="ignore")

def main():
    with open("careers_urls.txt", "r", encoding="utf-8") as f:
        urls = [u.strip() for u in f.readlines() if u.strip()]

    found = []
    for u in urls:
        try:
            html = fetch(u).lower()
        except Exception as e:
            found.append({"url": u, "provider": "unknown", "error": str(e)})
            continue

        gh = re.search(r"https?://(?:boards|job-boards)\.greenhouse\.io/([a-z0-9\-_]+)", html)
        lv = re.search(r"https?://jobs\.lever\.co/([a-z0-9\-_]+)", html)
        ah = re.search(r"https?://jobs\.ashbyhq\.com/([a-z0-9\-_]+)", html)

        if gh:
            found.append({"url": u, "provider": "greenhouse", "board": gh.group(1)})
        elif lv:
            found.append({"url": u, "provider": "lever", "company": lv.group(1)})
        elif ah:
            found.append({"url": u, "provider": "ashby", "board": ah.group(1)})
        else:
            found.append({"url": u, "provider": "custom"})

    with open("detected.json", "w", encoding="utf-8") as f:
        json.dump(found, f, indent=2)

    print("Wrote detected.json")

if __name__ == "__main__":
    main()
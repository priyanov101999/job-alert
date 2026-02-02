import json
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

UA = "job-alerts/lever"

def _get_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _created_at_ms(p: Dict[str, Any]) -> Optional[datetime]:
    ms = p.get("createdAt")
    if ms is None:
        return None
    try:
        return datetime.fromtimestamp(ms / 1000, tz=timezone.utc)
    except Exception:
        return None

def fetch_jobs(company: str) -> List[Dict[str, Any]]:
    url = f"https://api.lever.co/v0/postings/{company}?mode=json"
    data = _get_json(url)  # list

    out: List[Dict[str, Any]] = []
    for p in data:
        cats = p.get("categories") or {}
        out.append(
            {
                "id": p.get("id") or p.get("hostedUrl") or p.get("applyUrl"),
                "title": p.get("text") or p.get("title") or "",
                "location": cats.get("location") or "",
                "team": cats.get("team") or "",
                "url": p.get("hostedUrl") or p.get("applyUrl") or "",
                "created_at": _created_at_ms(p),
                "raw": p,
                "source": "Lever",
            }
        )
    return out 
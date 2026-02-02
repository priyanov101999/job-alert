import json
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

UA = "job-alerts/ashby"

def _get_json(url: str) -> Any:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))

def _iso_dt(s: str) -> Optional[datetime]:
    if not s:
        return None
    try:
        return datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(timezone.utc)
    except Exception:
        return None

def fetch_jobs(board: str) -> List[Dict[str, Any]]:
    # Public posting API
    url = f"https://api.ashbyhq.com/posting-api/job-board/{board}"
    data = _get_json(url)

    postings = data.get("jobs", []) if isinstance(data, dict) else []
    out: List[Dict[str, Any]] = []

    for j in postings:
        created = _iso_dt(j.get("publishedAt", "")) or _iso_dt(j.get("createdAt", ""))

        out.append(
            {
                "id": j.get("id") or j.get("_id"),
                "title": j.get("title") or "",
                "location": (j.get("location") or {}).get("name") if isinstance(j.get("location"), dict) else (j.get("location") or ""),
                "url": j.get("jobUrl") or j.get("applyUrl") or "",
                "created_at": created,
                "raw": j,
                "source": "Ashby",
            }
        )

    return out
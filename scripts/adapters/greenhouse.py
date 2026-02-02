import json
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

UA = "job-alerts/greenhouse"

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
    url = f"https://boards-api.greenhouse.io/v1/boards/{board}/jobs?content=true"
    data = _get_json(url)
    jobs = data.get("jobs", []) if isinstance(data, dict) else []

    out: List[Dict[str, Any]] = []
    for j in jobs:
        loc = j.get("location")
        loc_name = ""
        if isinstance(loc, dict):
            loc_name = loc.get("name") or ""
        elif isinstance(loc, str):
            loc_name = loc

        created = _iso_dt(j.get("created_at", "")) or _iso_dt(j.get("createdAt", ""))

        out.append(
            {
                "id": j.get("id"),
                "title": j.get("title") or "",
                "location": loc_name,
                "url": j.get("absolute_url") or "",
                "created_at": created,
                "raw": j,
                "source": "Greenhouse",
            }
        )
    return out
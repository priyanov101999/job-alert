import json
import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from adapters import greenhouse, lever, ashby, custom_stub
from adapters import greenhouse, lever, ashby, custom_stub

STATE_FILE = "state.json"
ALERT_FILE = "alert.md"

def now_utc() -> datetime:
    return datetime.now(timezone.utc)

def parse_window(window: str) -> timedelta:
    w = window.strip().lower()
    if w.endswith("h"):
        return timedelta(hours=int(w[:-1]))
    if w.endswith("d"):
        return timedelta(days=int(w[:-1]))
    raise ValueError("window must be like '1h' or '7d'")

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path: str, obj: Any) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)

def text_blob(item: Dict[str, Any]) -> str:
    parts: List[str] = [
        str(item.get("title", "") or ""),
        str(item.get("location", "") or ""),
        str(item.get("team", "") or ""),
    ]
    raw = item.get("raw") or {}
    for k in ("description", "content", "descriptionPlain", "descriptionHtml", "text"):
        v = raw.get(k)
        if isinstance(v, str):
            parts.append(v)
    return " ".join(parts).lower()

def any_contains(blob: str, terms: List[str]) -> bool:
    if not terms:
        return True
    return any(t.lower() in blob for t in terms)

def none_contains(blob: str, terms: List[str]) -> bool:
    if not terms:
        return True
    return not any(t.lower() in blob for t in terms)

def in_window(dt: Optional[datetime], cutoff: datetime) -> bool:
    return dt is not None and dt >= cutoff

def job_key(source: str, company: str, job_id: Any, url: str) -> str:
    return f"{source}:{company}:{job_id}:{url}"

def format_md(items: List[Dict[str, Any]], window: str) -> str:
    lines: List[str] = []
    lines.append(f"## New jobs posted in last **{window}** (real created/published time)")
    lines.append("")
    if not items:
        lines.append("No new matching jobs found.")
        return "\n".join(lines)

    for it in items:
        created = it["created_at"].strftime("%Y-%m-%d %H:%M UTC") if it.get("created_at") else "unknown"
        lines.append(f"- **{it.get('title','').strip()}** — {it.get('company')} ({it.get('source')})  ")
        if it.get("location"):
            lines.append(f"  Location: {it.get('location')}  ")
        lines.append(f"  Posted: {created}  ")
        if it.get("url"):
            lines.append(f"  {it.get('url')}")
        lines.append("")
    return "\n".join(lines)

def main() -> None:
    targets = load_json("targets.json")
    state = load_json(STATE_FILE) if os.path.exists(STATE_FILE) else {"seen": {}}
    seen: Dict[str, str] = state.setdefault("seen", {})

    window = targets.get("window", "1h")
    cutoff = now_utc() - parse_window(window)

    role_any_of = targets.get("role_any_of", [])
    include_any_of = targets.get("include_any_of", [])
    exclude_any_of = targets.get("exclude_any_of", [])
    us_only = bool(targets.get("us_only", True))
    us_signals_any_of = targets.get("us_signals_any_of", [])

    new_items: List[Dict[str, Any]] = []

    # Greenhouse
    for t in targets.get("greenhouse", []):
        name = t["name"]
        board = t["board"]
        jobs = []
        try:
            jobs = greenhouse.fetch_jobs(board)
        except Exception as e:
            print(f"[WARN] Greenhouse failed {name} ({board}): {e}")
            continue

        for j in jobs:
            if not in_window(j.get("created_at"), cutoff):
                continue
            blob = text_blob(j)
            if role_any_of and not any_contains(blob, role_any_of):
                continue
            if include_any_of and not any_contains(blob, include_any_of):
                continue
            if exclude_any_of and not none_contains(blob, exclude_any_of):
                continue
            if us_only and us_signals_any_of and not any_contains(blob, us_signals_any_of):
                continue

            key = job_key("greenhouse", name, j.get("id"), j.get("url",""))
            if key in seen:
                continue
            seen[key] = now_utc().isoformat()
            j["company"] = name
            new_items.append(j)

    # Lever
    for t in targets.get("lever", []):
        name = t["name"]
        company = t["company"]
        jobs = []
        try:
            jobs = lever.fetch_jobs(company)
        except Exception as e:
            print(f"[WARN] Lever failed {name} ({company}): {e}")
            continue

        for j in jobs:
            if not in_window(j.get("created_at"), cutoff):
                continue
            blob = text_blob(j)
            if role_any_of and not any_contains(blob, role_any_of):
                continue
            if include_any_of and not any_contains(blob, include_any_of):
                continue
            if exclude_any_of and not none_contains(blob, exclude_any_of):
                continue
            if us_only and us_signals_any_of and not any_contains(blob, us_signals_any_of):
                continue

            key = job_key("lever", name, j.get("id"), j.get("url",""))
            if key in seen:
                continue
            seen[key] = now_utc().isoformat()
            j["company"] = name
            new_items.append(j)

    # Ashby
    for t in targets.get("ashby", []):
        name = t["name"]
        board = t["board"]
        jobs = []
        try:
            jobs = ashby.fetch_jobs(board)
        except Exception as e:
            print(f"[WARN] Ashby failed {name} ({board}): {e}")
            continue

        for j in jobs:
            if not in_window(j.get("created_at"), cutoff):
                continue
            blob = text_blob(j)
            if role_any_of and not any_contains(blob, role_any_of):
                continue
            if include_any_of and not any_contains(blob, include_any_of):
                continue
            if exclude_any_of and not none_contains(blob, exclude_any_of):
                continue
            if us_only and us_signals_any_of and not any_contains(blob, us_signals_any_of):
                continue

            key = job_key("ashby", name, j.get("id"), j.get("url",""))
            if key in seen:
                continue
            seen[key] = now_utc().isoformat()
            j["company"] = name
            new_items.append(j)

    # Custom portals (stub for now)
    for t in targets.get("custom_portals", []):
        _ = custom_stub.fetch_jobs(t["name"], t["url"])

    # Sort newest first
    new_items.sort(key=lambda x: x.get("created_at") or datetime(1970,1,1,tzinfo=timezone.utc), reverse=True)

    with open(ALERT_FILE, "w", encoding="utf-8") as f:
        f.write(format_md(new_items, window))

    save_json(STATE_FILE, state)
    print(f"Done. New items: {len(new_items)}")

if __name__ == "__main__":
    main()
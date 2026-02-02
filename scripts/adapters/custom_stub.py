from typing import Any, Dict, List

def fetch_jobs(name: str, url: str) -> List[Dict[str, Any]]:
    # Custom portals need a dedicated adapter per site.
    # We return empty list so your pipeline still runs.
    return []
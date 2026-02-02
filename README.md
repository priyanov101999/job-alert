# Job Alerts (Hourly) — ATS + Career Pages

This repo checks company job boards every hour and alerts when NEW jobs are posted (based on real `created_at` / `publishedAt`, not Google indexing time).

## What it tracks (reliable new-job timestamp)
✅ Greenhouse (`created_at`)  
✅ Lever (`createdAt`)  
✅ Ashby (`publishedAt`)

Custom portals (Apple/Amazon/Meta/Microsoft/etc.) are listed but not scraped yet unless adapters are added.

---

## Files
- `targets.json` → companies + filters (entry/junior + US)
- `scripts/run_alerts.py` → main runner
- `scripts/adapters/` → job board adapters (greenhouse, lever, ashby)
- `state.json` → dedupe state (prevents repeat alerts)
- `alert.md` → latest results

---

## How it runs every hour
GitHub Actions workflow:
`.github/workflows/job_alerts.yml`

Cron:
```yaml
- cron: "0 * * * *"

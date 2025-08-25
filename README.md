# Chicago SMB Market Radar

Ship a lightweight, free-to-run market radar for Chicago using open data (Business Licenses, Building Permits, CTA boardings).
Ingest via Socrata SODA/SoQL, transform in pandas, push tidy tables to Google Sheets, connect to Looker Studio, and auto-generate a weekly brief (Markdown → PDF if Pandoc is installed).

## Sources (official)
- Business Licenses — r5kz-chrr (includes community area/name since 2025-02-20). Portal page + change notice:
  - https://data.cityofchicago.org/Community-Economic-Development/Business-Licenses/r5kz-chrr
  - https://data.cityofchicago.org/stories/s/Change-Notice-Business-Licenses-2-20-2025/yu97-as3j/
- Building Permits — ydr8-5enu (API Foundry docs):
  - https://dev.socrata.com/foundry/data.cityofchicago.org/ydr8-5enu
- CTA Ridership — Daily Boarding Totals — 6iiy-9s97:
  - https://data.cityofchicago.org/Transportation/CTA-Ridership-Daily-Boarding-Totals/6iiy-9s97
- SoQL/SODA docs:
  - Queries guide: https://dev.socrata.com/docs/queries/
  - date_trunc_ymd: https://dev.socrata.com/docs/functions/date_trunc_ymd
  - SELECT clause: https://dev.socrata.com/docs/queries/select

## Data model (Sheets tabs)
- licenses_weekly: week_start, community_area, community_area_name, bucket, new_licenses, wow, avg_13w, std_13w, momentum_index
- permits_weekly (optional): week_start, community_area, permits
- cta_weekly (optional): week_start, boardings
- summary_latest: pre-computed tiles for dashboard + brief

## Quickstart (Mac + Cursor)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
Create a Google service account (JSON), share your target Sheet with the service account email, copy `.env.example` to `.env`, and set GOOGLE_APPLICATION_CREDENTIALS + SHEET_ID. Then run:
```bash
python -m src.main
```

## GitHub Actions (6:00 AM CT Mondays)
Uses `GOOGLE_CREDENTIALS_B64` (base64 of your JSON) + `SHEET_ID` secrets. See `.github/workflows/refresh.yml` for details.

## Limits & future upgrades
Included: Socrata client, weekly rollups, 13w baselines, momentum index, Sheets writer, Markdown brief, GH Actions cron.
Not included: corridor geoshapes, advanced NLP bucketing, Slack/email alerts, backfills beyond the lookback, DB sink, Looker template.

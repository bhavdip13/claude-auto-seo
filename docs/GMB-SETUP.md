# Google My Business (GMB) Setup Guide

Claude Auto SEO can automatically post to your Google My Business profile using the Google My Business API.

---

## What It Does

- Posts updates, tips, and offers to your GMB profile automatically
- Uses random timing within your configured windows (natural appearance)
- Posts every 3 days, twice daily, or on your custom schedule
- Generates a banner image for each GMB post
- Reads topics from `config/keywords.md` — GMB section

---

## Step 1: Enable the My Business API

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Create a new project or select existing
3. Go to **APIs & Services → Library**
4. Search for **"My Business Account Management API"** → Enable
5. Search for **"My Business Business Information API"** → Enable
6. Search for **"My Business Notifications API"** → Enable

---

## Step 2: Create OAuth 2.0 Credentials

1. Go to **APIs & Services → Credentials**
2. Click **"Create Credentials" → "OAuth 2.0 Client IDs"**
3. Application type: **Desktop Application**
4. Name: "Claude Auto SEO"
5. Download the JSON file
6. Save as `config/google-oauth-client.json`

---

## Step 3: Get Your GMB Location ID

```bash
python3 scripts/gmb_setup.py --list-locations
```

This will:
1. Open a browser for you to log in to Google
2. List all your GMB locations
3. Show the Location ID for each

Copy your Location ID and add to `.env`:
```
GMB_LOCATION_ID=accounts/123456789/locations/987654321
```

---

## Step 4: Get Access Token

```bash
python3 scripts/gmb_setup.py --auth
```

This opens a browser OAuth flow and saves your tokens to `config/gmb-tokens.json`

Then add to `.env`:
```
GOOGLE_GMB_ACCESS_TOKEN=[token from gmb-tokens.json]
GOOGLE_APPLICATION_CREDENTIALS=config/google-service-account.json
```

---

## Step 5: Configure Schedule

In `config/schedule.json`:
```json
"gmb": {
  "enabled": true,
  "frequency": "every_3_days",
  "posts_per_session": 1,
  "random_timing": true,
  "posting_windows": [
    {"from": 9, "to": 11},
    {"from": 14, "to": 16}
  ]
}
```

**Frequency options:**
- `"twice_daily"` — 2 posts per day at random times
- `"daily"` — 1 post per day
- `"every_3_days"` — 1 post every 3 days (recommended)
- `"weekly"` — once per week

---

## Step 6: Add GMB Topics to Keywords Config

In `config/keywords.md`, find the GMB section:
```markdown
## Google My Business Keywords

| GMB Post Topic | Keyword Focus | Post Type |
|---|---|---|
| New blog post about SEO tips | seo tips | update |
| Special offer this week | discount offer | offer |
| Expert tip about keyword research | keyword research | standard |
```

---

## Step 7: Test

```bash
python3 scripts/dm_scheduler.py --preview  # Preview without posting
python3 scripts/dm_scheduler.py --run      # Run now
```

---

## GMB Post Types

| Type | Use Case |
|---|---|
| `STANDARD` | Tips, insights, news, blog post announcements |
| `OFFER` | Promotions, discounts, special deals |
| `EVENT` | Webinars, events, launches |
| `ALERT` | Important updates (use sparingly) |

---

## Token Refresh

GMB access tokens expire. To refresh:
```bash
python3 scripts/gmb_setup.py --refresh-token
```

Or set up the refresh token flow — it auto-refreshes if you have the client credentials configured.

---

## Troubleshooting

**"403 Forbidden"** — Your account needs GMB API access. Apply at: https://developers.google.com/my-business/content/prereqs

**"Location not found"** — Run `python3 scripts/gmb_setup.py --list-locations` to get the correct ID format.

**"Token expired"** — Run `python3 scripts/gmb_setup.py --refresh-token`

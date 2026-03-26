# Complete Setup & Testing Guide

> This guide answers all your questions and walks through the exact steps
> to get Claude Auto SEO fully running — from domain to full automation.

---

## STEP 0: Your 3-Minute Prerequisites

Install these before anything else:

```bash
# 1. Install Claude Code
# Go to: https://claude.ai/claude-code
# Download and install for your OS

# 2. Install Python 3.10+
# Go to: https://python.org/downloads

# 3. Install the project
git clone https://github.com/YOUR_USERNAME/claude-auto-seo.git
cd claude-auto-seo
./install.sh
pip install -r requirements.txt
```

---

## STEP 1: Auto-Configure from Your Domain (2 minutes)

**This answers your question: "How does it know about my website?"**

Just give it your domain name and it reads everything automatically:

```bash
# Basic (scans your site publicly)
python3 scripts/auto_configure.py --domain yoursite.com

# Better (also reads your WordPress posts and pages)
python3 scripts/auto_configure.py --domain yoursite.com \
  --wp-user your_wp_username \
  --wp-pass "your app password"
```

**What it auto-detects:**
- Your site's niche and business type
- Your brand colors (for banner images)
- All your existing WordPress posts (mapped as internal links)
- All your WordPress pages
- Generates keyword clusters for your niche
- Creates 30 topics in the writing queue
- Pre-fills your `.env` with site URL and colors

**After running, you'll have these files auto-created:**
- `config/site.json` — your site settings
- `config/keywords.md` — keyword clusters
- `context/brand-voice.md` — brand voice template (you fill in details)
- `context/internal-links-map.md` — your existing pages
- `topics/queue.txt` — 30 topics ready to write
- `.env` — credentials template

---

## STEP 2: Add Your Logo (1 minute)

**This answers: "How does it get the logo?"**

It does NOT auto-download your logo (copyright reasons). You add it manually:

1. Save your logo as `assets/logo.png`
2. Recommended: PNG with transparent background, at least 300×100px
3. It will appear in the top-left corner of every banner image

If you skip this, the system uses your site name as text instead.

---

## STEP 3: Add the Anthropic API Key

**This is required for Claude to write content automatically.**

1. Go to: https://console.anthropic.com/api-keys
2. Create a new key
3. Add to `.env`:
```
ANTHROPIC_API_KEY=sk-ant-api03-...
```

The scheduler uses this to call Claude Code when generating articles.

---

## STEP 4: Add WordPress App Password

**For: Auto-publishing, SEO scanning, auto-fixing**

```
WP_URL=https://yoursite.com
WP_USERNAME=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

**How to get the App Password:**
1. Log in to WordPress Admin
2. Go to: Users → Your Profile
3. Scroll down to "Application Passwords"
4. Enter name: `Claude Auto SEO`
5. Click "Add New Application Password"
6. Copy the generated password (shown once only)
7. Paste into `.env` as `WP_APP_PASSWORD`

**Test it:**
```bash
python3 scripts/wp_seo_fixer.py --scan
```
If you see a list of your posts, it's working.

---

## STEP 5: Social Media Credentials

**All social media credentials go in ONE place: `.env`**

### Facebook + Instagram (Same credentials)

1. Go to: https://developers.facebook.com
2. Create App → Business type
3. Add products: Facebook Login + Instagram Graph API
4. Go to Graph API Explorer → Generate Access Token for your Page
5. Grant permissions: `pages_manage_posts`, `instagram_content_publish`

```
META_ACCESS_TOKEN=your_page_access_token_here
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_USER_ID=your_instagram_business_id
```

**Test Facebook:**
```bash
python3 scripts/social_publisher.py --topic "Test" --platforms facebook
```

**Test Instagram:**
```bash
python3 scripts/social_publisher.py --topic "Test" --platforms instagram --image output/images/test.jpg
```

---

### Twitter / X

1. Go to: https://developer.twitter.com
2. Apply for developer account → Create App
3. Set permissions to "Read and Write"
4. Copy all 5 credentials:

```
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_SECRET=xxx
TWITTER_BEARER_TOKEN=xxx
```

**Test:**
```bash
python3 scripts/social_publisher.py --topic "Test tweet" --platforms twitter
```

---

### LinkedIn

1. Go to: https://linkedin.com/developers → Create App
2. Request permissions: `w_member_social`, `r_basicprofile`
3. Run OAuth flow:
```bash
python3 scripts/linkedin_auth.py
```

```
LINKEDIN_ACCESS_TOKEN=your_token
```

**Test:**
```bash
python3 scripts/social_publisher.py --topic "Test post" --platforms linkedin
```

---

### Pinterest

1. Go to: https://developers.pinterest.com → Create App
2. Get your Board ID from any board URL
3. Run auth: `python3 scripts/pinterest_auth.py`

```
PINTEREST_ACCESS_TOKEN=your_token
PINTEREST_BOARD_ID=your_board_id
```

---

### Google My Business

This is more involved. See `docs/GMB-SETUP.md` for step-by-step.

Quick version:
```bash
python3 scripts/gmb_setup.py --auth           # Opens browser OAuth
python3 scripts/gmb_setup.py --list-locations  # Shows your location ID
```

Then add to `.env`:
```
GOOGLE_GMB_ACCESS_TOKEN=from_auth_step
GMB_LOCATION_ID=accounts/xxx/locations/yyy
```

**Test:**
```bash
python3 scripts/dm_scheduler.py --preview
```

---

## STEP 6: Find Your Top 100 Priority Keywords

```bash
python3 scripts/keyword_finder.py --domain yoursite.com --update-config
```

This:
1. Pulls your existing rankings from Google Search Console
2. Finds keywords on pages 2-6 (easiest to push to page 1)
3. Adds new keyword opportunities
4. Saves a full report to `reports/top-100-keywords-[date].md`
5. Updates `config/keywords.md` with these prioritized keywords

---

## STEP 7: Scan and Fix Your WordPress Site

```bash
# In Claude Code:
claude
/wp-seo-fix scan https://yoursite.com
```

Review the report, then:
```
/wp-seo-fix apply
```

Or via Python:
```bash
python3 scripts/wp_seo_fixer.py --scan
python3 scripts/wp_seo_fixer.py --apply --dry-run  # Preview first
python3 scripts/wp_seo_fixer.py --apply            # Apply all fixes
```

---

## STEP 8: Test Content Generation

```bash
claude
/research "your main keyword from keywords.md"
/write "your main keyword"
```

Check:
- `research/brief-*.md` — research brief created
- `drafts/*.md` — article created
- `drafts/reports-*.md` — agent analysis reports

---

## STEP 9: Test Banner Image Generation

```bash
python3 scripts/image_generator.py --title "Test Post Title" --keyword "seo" --type all
ls output/images/
```

You should see JPEG/SVG files for all platform sizes.

---

## STEP 10: Test Social Media Posts

```bash
# Preview without posting (safe test)
python3 scripts/dm_scheduler.py --preview

# Test one platform
python3 scripts/social_publisher.py --topic "Test post" --keyword "seo" --platforms facebook

# Test festival poster
python3 scripts/festival_poster.py --preview
python3 scripts/festival_poster.py --check-upcoming 30
```

---

## STEP 11: Set Up Full Automation (Cron Jobs)

```bash
# Daily blog post at 9 AM
python3 scripts/scheduler.py --install-cron

# Social media posts (3x daily at random times)
python3 scripts/dm_scheduler.py --install-cron

# Festival posts at 1 AM
python3 scripts/festival_poster.py --install-cron

# Daily email report at 8 PM
# Add manually to crontab:
crontab -e
# Add: 0 20 * * * cd /path/to/claude-auto-seo && python3 scripts/daily_report.py --send-email
```

Verify cron is installed:
```bash
crontab -l
```

---

## STEP 12: Set Up Daily Email Report

In `.env`:
```
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_gmail_app_password
NOTIFICATION_EMAIL=you@yoursite.com
```

**Gmail App Password** (not your regular password):
1. Google Account → Security → 2-Step Verification (must be on)
2. App Passwords → Create one called "Claude Auto SEO"
3. Use that 16-char password as `SMTP_PASS`

**Test email:**
```bash
python3 scripts/daily_report.py --send-email
```

---

## QUICK TEST CHECKLIST

Run through these to confirm everything works:

```bash
# ✅ 1. WordPress connection
python3 scripts/wp_seo_fixer.py --scan

# ✅ 2. Banner images
python3 scripts/image_generator.py --title "Test" --keyword "seo" --type blog

# ✅ 3. Article writing (requires ANTHROPIC_API_KEY)
claude
/write "test keyword"
# Exit claude with Ctrl+C

# ✅ 4. Social media preview
python3 scripts/dm_scheduler.py --preview

# ✅ 5. Festival check
python3 scripts/festival_poster.py --check-upcoming 30

# ✅ 6. Daily report
python3 scripts/daily_report.py --print-only

# ✅ 7. Keyword finder
python3 scripts/keyword_finder.py --domain yoursite.com

# ✅ 8. Directory checklist
python3 scripts/directory_manager.py --generate-checklist
```

---

## WHERE EVERYTHING IS STORED

| Data | Location |
|---|---|
| API credentials | `.env` |
| Keywords | `config/keywords.md` |
| Schedule settings | `config/schedule.json` |
| Your logo | `assets/logo.png` |
| Topic queue | `topics/queue.txt` |
| Drafts awaiting review | `review-required/` |
| Published articles | `published/` |
| Generated banners | `output/images/` |
| Daily reports | `reports/daily-report-*.md` |
| Audit results | `audits/` |
| Social post log | `data/social-publish-log.json` |
| Festival post log | `data/festival-log.json` |
| WP fix backup | `data/wp-fix-backup-*.json` |
| Rankings history | `data/rankings-history.json` |

---

## DAILY REVIEW WORKFLOW

Every morning, check your daily report:
```bash
cat reports/daily-report-$(date +%Y-%m-%d).md
```
Or it will be emailed to you automatically.

The report shows:
- Every blog post written (with file path)
- Every social media post (with post IDs/URLs)
- Every festival post
- Every WordPress SEO fix applied
- Current keyword rankings
- Any errors that need attention
- Action items requiring your review

---

## SUPPORT

- Installation issues: `docs/TROUBLESHOOTING.md`
- Social credentials: `docs/SOCIAL-CREDENTIALS.md`
- GMB setup: `docs/GMB-SETUP.md`
- All commands: `docs/COMMANDS.md`
- Architecture: `docs/ARCHITECTURE.md`

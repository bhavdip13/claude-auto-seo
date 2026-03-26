# Quick Start Guide — Claude Auto SEO + Digital Marketing

Get up and running in 15 minutes.

---

## Step 1: Install (2 minutes)

```bash
git clone https://github.com/YOUR_USERNAME/claude-auto-seo.git
cd claude-auto-seo
./install.sh
pip install -r requirements.txt
```

---

## Step 2: Configure Your Site (5 minutes)

### 2a. Edit `config/site.json`
```json
{
  "site": {
    "url": "https://yoursite.com",
    "name": "Your Brand Name",
    "type": "blog"
  }
}
```

### 2b. Add your WordPress credentials to `.env`
```bash
cp .env.example .env
# Edit .env:
WP_URL=https://yoursite.com
WP_USERNAME=your_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

**Get App Password:** WordPress Admin → Users → Profile → Application Passwords → Create one called "Claude Auto SEO"

### 2c. Add your logo
Copy your logo PNG to `assets/logo.png` (used on banner images)

---

## Step 3: Add Your Keywords (3 minutes)

Edit `config/keywords.md` — this is the most important file:

```markdown
## Cluster 1: [Your Topic]

| Keyword | Volume | Difficulty | Intent | Status |
|---|---|---|---|---|
| your main keyword | 1200 | low | informational | queue |
| related keyword 2 | 800 | low | informational | queue |
| related keyword 3 | 500 | medium | commercial | queue |
```

Set `status` to `queue` for keywords you want written automatically.

---

## Step 4: Try It Now (5 minutes)

```bash
# Start Claude Code
claude

# Run a full SEO audit of your site
/seo audit https://yoursite.com

# Scan your WordPress site for SEO issues
/wp-seo-fix scan https://yoursite.com

# Write your first blog post
/research "your first keyword from keywords.md"
/write "your first keyword"

# Generate social media banners
/dm banner "Your Post Title" --keyword "your keyword"
```

---

## Step 5: Auto-Fix WordPress SEO Issues

```bash
# In Claude Code:
/wp-seo-fix scan https://yoursite.com
# Review the report
/wp-seo-fix apply
# All fixable issues are patched automatically!
```

---

## Step 6: Set Up Auto-Scheduling (Optional)

### Content (daily blog posts):
```bash
python3 scripts/scheduler.py --install-cron
```

### Social Media (daily auto-posting):
1. Add your social media credentials to `.env` (see `docs/SOCIAL-CREDENTIALS.md`)
2. Enable platforms in `config/schedule.json` (set `"enabled": true`)
3. Install cron jobs:
```bash
python3 scripts/dm_scheduler.py --install-cron
```

### Google My Business:
1. Follow `docs/GMB-SETUP.md`
2. Enable in `config/schedule.json`: `"gmb": { "enabled": true }`

---

## What Happens Automatically

Once set up, every day:
- ✍️ **9 AM** — New blog post written from your keyword queue → saved to `review-required/`
- 📱 **9:30 AM** — Social media posts generated + banner images created
- 📸 **10 AM** — Instagram posted (if enabled)
- 📘 **10:15 AM** — Facebook posted
- 💼 **8:30 AM** — LinkedIn posted
- 🐦 **3x/day** — Twitter/X posted
- 📍 **Every 3 days** — Google My Business post (random time)

---

## Key Commands Reference

```bash
# SEO
/seo audit <url>          # Full site audit
/wp-seo-fix scan <url>    # Scan WordPress issues
/wp-seo-fix apply         # Auto-fix all issues
/seo weekly-digest <url>  # Weekly summary

# Content
/research <topic>         # Research before writing
/write <topic>            # Write + optimize article
/content calendar         # 30-day content plan

# Publishing
/publish-draft <file>     # → WordPress
/publish-external <file> medium  # → Medium
/publish-external <file> all     # → All platforms

# Social Media & Digital Marketing
/dm post <topic>          # Post to all social platforms
/dm schedule run-now      # Run today's scheduled posts
/dm banner <title>        # Generate banner images only

# Reports
/seo report <url>         # Full PDF report
/seo rank-track <url>     # Keyword rankings
/dm report                # Social media report
```

---

## File You'll Edit Most Often

| File | What it does |
|---|---|
| `config/keywords.md` | Your target keywords — add more here |
| `topics/queue.txt` | Topics in the writing queue |
| `config/schedule.json` | Enable/disable platforms, set frequency |
| `context/brand-voice.md` | Your brand voice (for better articles) |
| `.env` | All API credentials |
| `assets/logo.png` | Your logo (for banner images) |

---

## Need Help?

- Full docs: `docs/` directory
- Installation issues: `docs/TROUBLESHOOTING.md`
- Social credentials: `docs/SOCIAL-CREDENTIALS.md`
- GMB setup: `docs/GMB-SETUP.md`
- All commands: `docs/COMMANDS.md`

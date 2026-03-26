# Cloud Hosting Guide — Run Without Your Laptop 24/7

> **Short answer:** No, you do NOT need your laptop running 24/7.
> You can host this completely free on cloud servers.

---

## Free Hosting Options (Best to Worst)

### 🥇 Option 1: Google Cloud Run (BEST — Free Tier)
**Cost:** Free for light usage
**Always on:** Yes
**Setup time:** 20 minutes

```bash
# 1. Install Google Cloud CLI
# Download from: https://cloud.google.com/sdk/docs/install

# 2. Login
gcloud auth login
gcloud config set project YOUR_PROJECT_ID

# 3. Deploy Claude Auto SEO as a Cloud Run job
gcloud run jobs create claude-auto-seo \
  --image python:3.11 \
  --region us-central1 \
  --memory 512Mi \
  --max-retries 3 \
  --set-env-vars="$(cat .env | tr '\n' ',')"

# 4. Schedule it with Cloud Scheduler (replaces cron)
# Blog post - 9 AM daily
gcloud scheduler jobs create http seo-blog-daily \
  --schedule="0 9 * * *" \
  --uri="https://YOUR_CLOUD_RUN_URL/run?script=scheduler" \
  --time-zone="America/New_York"

# Social media - 9:30 AM
gcloud scheduler jobs create http seo-social-morning \
  --schedule="30 9 * * *" \
  --uri="https://YOUR_CLOUD_RUN_URL/run?script=dm_scheduler"

# Festival posts - 1 AM
gcloud scheduler jobs create http seo-festivals \
  --schedule="0 1 * * *" \
  --uri="https://YOUR_CLOUD_RUN_URL/run?script=festival_poster"

# Daily report - 8 PM
gcloud scheduler jobs create http seo-report \
  --schedule="0 20 * * *" \
  --uri="https://YOUR_CLOUD_RUN_URL/run?script=daily_report"
```

**Free tier includes:** 2M requests/month, 360,000 vCPU-seconds — more than enough.

---

### 🥈 Option 2: GitHub Actions (COMPLETELY FREE)
**Cost:** Free forever (2,000 minutes/month on free plan)
**Always on:** Yes (runs on GitHub's servers)
**Setup time:** 10 minutes

This is the EASIEST option. Create `.github/workflows/automation.yml`:

```yaml
# .github/workflows/automation.yml

name: Claude Auto SEO Automation

on:
  schedule:
    # Blog post - 9 AM UTC daily (adjust for your timezone)
    - cron: '0 9 * * *'
    # Social media morning - 9:30 AM UTC
    - cron: '30 9 * * *'
    # Social media afternoon - 1 PM UTC
    - cron: '0 13 * * *'
    # Social media evening - 7 PM UTC
    - cron: '0 19 * * *'
    # Festival posts - 1 AM UTC
    - cron: '0 1 * * *'
    # Daily report - 8 PM UTC
    - cron: '0 20 * * *'
  workflow_dispatch:  # Allow manual trigger

jobs:
  run-automation:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v4
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: pip install -r requirements.txt
    
    - name: Run Blog Scheduler
      if: github.event.schedule == '0 9 * * *'
      env:
        ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
        WP_URL: ${{ secrets.WP_URL }}
        WP_USERNAME: ${{ secrets.WP_USERNAME }}
        WP_APP_PASSWORD: ${{ secrets.WP_APP_PASSWORD }}
      run: python3 scripts/scheduler.py --run-now
    
    - name: Run Social Media
      if: github.event.schedule == '30 9 * * *' || github.event.schedule == '0 13 * * *' || github.event.schedule == '0 19 * * *'
      env:
        META_ACCESS_TOKEN: ${{ secrets.META_ACCESS_TOKEN }}
        FACEBOOK_PAGE_ID: ${{ secrets.FACEBOOK_PAGE_ID }}
        INSTAGRAM_USER_ID: ${{ secrets.INSTAGRAM_USER_ID }}
        TWITTER_API_KEY: ${{ secrets.TWITTER_API_KEY }}
        TWITTER_API_SECRET: ${{ secrets.TWITTER_API_SECRET }}
        TWITTER_ACCESS_TOKEN: ${{ secrets.TWITTER_ACCESS_TOKEN }}
        TWITTER_ACCESS_SECRET: ${{ secrets.TWITTER_ACCESS_SECRET }}
        LINKEDIN_ACCESS_TOKEN: ${{ secrets.LINKEDIN_ACCESS_TOKEN }}
        WP_URL: ${{ secrets.WP_URL }}
        SITE_NAME: ${{ secrets.SITE_NAME }}
      run: python3 scripts/dm_scheduler.py --run
    
    - name: Festival Posts (1 AM)
      if: github.event.schedule == '0 1 * * *'
      env:
        META_ACCESS_TOKEN: ${{ secrets.META_ACCESS_TOKEN }}
        FACEBOOK_PAGE_ID: ${{ secrets.FACEBOOK_PAGE_ID }}
        INSTAGRAM_USER_ID: ${{ secrets.INSTAGRAM_USER_ID }}
        WP_URL: ${{ secrets.WP_URL }}
        SITE_NAME: ${{ secrets.SITE_NAME }}
      run: python3 scripts/festival_poster.py --post-now
    
    - name: Daily Report (8 PM)
      if: github.event.schedule == '0 20 * * *'
      env:
        SMTP_USER: ${{ secrets.SMTP_USER }}
        SMTP_PASS: ${{ secrets.SMTP_PASS }}
        NOTIFICATION_EMAIL: ${{ secrets.NOTIFICATION_EMAIL }}
        WP_URL: ${{ secrets.WP_URL }}
        SITE_NAME: ${{ secrets.SITE_NAME }}
      run: python3 scripts/daily_report.py --send-email
```

**How to set up GitHub Secrets:**
1. Push your project to GitHub (without `.env`)
2. Go to: Repository → Settings → Secrets and variables → Actions
3. Add each credential as a secret (same names as in your `.env`)
4. The workflow runs on GitHub's servers — your laptop can be off!

---

### 🥉 Option 3: Railway.app (Free Tier — $5/month after)
**Cost:** $5/month (very cheap)
**Always on:** Yes
**Setup time:** 15 minutes

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login and deploy
railway login
railway init
railway up

# 3. Add environment variables
railway variables set ANTHROPIC_API_KEY=sk-ant-...
railway variables set WP_URL=https://yoursite.com
# (add all your .env variables)

# 4. Add cron jobs via Railway dashboard
# Settings → Cron Jobs → Add your schedules
```

---

### 🥉 Option 4: Render.com (Free Tier)
**Cost:** Free for cron jobs
**Setup time:** 10 minutes

1. Create account at render.com
2. New → Cron Job
3. Connect your GitHub repo
4. Set command: `python3 scripts/scheduler.py --run-now`
5. Set schedule: `0 9 * * *`
6. Add environment variables in dashboard
7. Repeat for each script

---

### 🥉 Option 5: PythonAnywhere (Free Tier)
**Cost:** Free (1 task/day) or $5/month (unlimited)
**Setup time:** 10 minutes

1. Sign up at pythonanywhere.com
2. Upload your project files
3. Go to: Tasks → Add Scheduled Task
4. Command: `cd /home/username/claude-auto-seo && python3 scripts/scheduler.py --run-now`
5. Set time and frequency

---

## RECOMMENDED SETUP (Best for Beginners)

### Use GitHub Actions — It's Free, Always On, No Server Needed

```bash
# Step 1: Push to GitHub
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/YOUR_USERNAME/claude-auto-seo.git
git push -u origin main

# Step 2: Add all your .env values as GitHub Secrets
# Go to: GitHub → Your Repo → Settings → Secrets → New Repository Secret
# Add each key-value pair from your .env file

# Step 3: Create the workflow file
mkdir -p .github/workflows
cp scripts/github-actions-template.yml .github/workflows/automation.yml

# Step 4: Push the workflow
git add .github/
git commit -m "Add automation workflow"
git push

# Step 5: Verify it's running
# GitHub → Your Repo → Actions tab → Check workflow runs
```

**After this, your laptop can be completely OFF.**
GitHub runs all automation on their servers for FREE.

---

## Important: What to NEVER push to GitHub

Your `.env` file contains API keys. NEVER push it.

It's already in `.gitignore` — but double-check:
```bash
cat .gitignore | grep .env
# Should show: .env
```

Instead, use GitHub Secrets for all credentials.

---

## Hosting Comparison

| Option | Cost | Always On | Difficulty | Best For |
|---|---|---|---|---|
| GitHub Actions | **Free** | ✅ Yes | Easy | Everyone |
| Google Cloud Run | **Free tier** | ✅ Yes | Medium | Scaling up |
| Railway.app | $5/month | ✅ Yes | Easy | Simple hosting |
| Render.com | Free | ✅ Yes | Easy | Cron jobs |
| PythonAnywhere | Free/5$/mo | ✅ Yes | Easy | Python projects |
| Your laptop | Free | ❌ Must stay on | Easy | Not recommended |

---

## Quick Answer to Your Question

**Q: Do I need to keep my laptop on 24/7?**

**A: NO.** Use GitHub Actions (free):
1. Push your project to GitHub
2. Add credentials as GitHub Secrets  
3. The `.github/workflows/automation.yml` file runs all your cron jobs on GitHub's servers
4. Your laptop can be completely off
5. Check results in the GitHub Actions tab and via your daily email report

**Total cost: $0/month** (within GitHub free tier limits)

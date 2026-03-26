# /seo schedule — Automated Daily/Weekly Content Scheduler

You are the Content Scheduler for Claude Auto SEO. This command sets up and manages automated content publishing schedules.

## What This Does
Automatically generates, optimizes, and publishes blog posts to WordPress on a schedule you define — daily, weekly, or custom intervals.

## Setup

### Step 1: Configure Schedule
Edit `config/schedule.json`:
```json
{
  "wordpress_internal": {
    "enabled": true,
    "frequency": "daily",
    "time": "09:00",
    "timezone": "America/New_York",
    "posts_per_run": 1,
    "topic_source": "auto",
    "auto_publish": false,
    "review_required": true
  },
  "external_platforms": {
    "medium": { "enabled": false, "frequency": "weekly" },
    "reddit": { "enabled": false, "frequency": "weekly" }
  }
}
```

### Step 2: Populate Topic Queue
Add topics to `topics/queue.txt` (one per line):
```
best practices for wordpress seo
how to improve page speed
internal linking strategies
schema markup guide
```

Or let the system auto-generate topics from:
- `context/target-keywords.md` keyword clusters
- Competitor gap analysis
- Trending topics in your niche

### Step 3: Run the Scheduler

**Manual run (generate today's content):**
```bash
python3 scripts/scheduler.py --run-now
```

**Set up daily cron job (Linux/Mac):**
```bash
python3 scripts/scheduler.py --install-cron
# Installs: 0 9 * * * cd /path/to/project && python3 scripts/scheduler.py --run-now
```

**Windows Task Scheduler:**
```bash
python3 scripts/scheduler.py --install-windows-task
```

## Scheduler Pipeline (Per Run)

### Phase 1: Topic Selection
1. Check `topics/queue.txt` for next topic
2. If queue empty: auto-generate from keyword clusters + trending topics
3. Verify topic not already published (check `published/` + WordPress posts)
4. Log selected topic to `data/scheduler-log.json`

### Phase 2: Content Generation
1. Run `/research [topic]` → save brief
2. Run `/write [topic]` → create article
3. Run all optimization agents automatically
4. Run `/scrub` → remove AI patterns
5. SEO score check: if < 75, apply auto-fixes

### Phase 3: Quality Gate
Before publishing, verify:
- [ ] Word count ≥ 2,000
- [ ] SEO score ≥ 75/100
- [ ] Primary keyword density 1-2%
- [ ] 3+ internal links
- [ ] Meta title 50-60 chars
- [ ] Meta description 150-160 chars

If `review_required: true` → save to `review-required/` and STOP
If `review_required: false` → proceed to publish

### Phase 4: Publish (if auto_publish enabled)
- POST to WordPress as DRAFT (if review_required) or PUBLISHED
- Set all Yoast SEO metadata
- Update internal links map
- Log publish to `data/publish-log.json`

### Phase 5: Reporting
- Add to weekly digest
- Update `data/rankings-history.json` with new post
- Send notification if configured (Slack/email)

## Commands

```bash
/seo schedule setup          # Interactive setup wizard
/seo schedule status         # Show current schedule and queue
/seo schedule run-now        # Generate and publish one post now
/seo schedule pause          # Pause the scheduler
/seo schedule resume         # Resume the scheduler
/seo schedule queue          # Show and manage topic queue
/seo schedule log            # View recent scheduler activity
```

## Notifications (Optional)
Configure in `.env`:
```
SLACK_WEBHOOK_URL=https://hooks.slack.com/...
NOTIFICATION_EMAIL=you@yoursite.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@gmail.com
SMTP_PASS=your_app_password
```

When a post is generated and queued for review, you'll receive:
- Post title and SEO score
- Link to the draft in WordPress
- Any quality issues detected

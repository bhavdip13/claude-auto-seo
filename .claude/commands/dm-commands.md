# /dm post — Auto-Generate and Post to All Social Media Platforms

You are the Digital Marketing Agent for Claude Auto SEO. When invoked with `/dm post [topic] [platforms]`, generate content and banner images and publish to all configured social media platforms.

## Usage
```bash
/dm post "seo tips for beginners"              # Post to all enabled platforms
/dm post "seo tips" --platforms instagram,facebook  # Specific platforms
/dm post --from-article drafts/my-article.md   # Convert article to social posts
/dm post --keyword "wordpress seo"             # Use keyword from config/keywords.md
```

## Pipeline

### Step 1: Content Generation
For each platform, generate tailored content:

**Instagram** (2200 chars max, 25 hashtags):
- Hook emoji + topic headline
- 3 key insights as ✅ bullet points
- "Link in bio ☝️" CTA
- 25 relevant hashtags from config/keywords.md

**Facebook** (no limit, 5 hashtags):
- Engaging opener question or statement
- 4 bullet point insights
- Comment question at end ("What's your experience with [topic]?")
- Direct article link

**LinkedIn** (3000 chars, 5 hashtags):
- Professional insight hook
- Numbered takeaways (1. 2. 3. 4.)
- Thought leadership angle
- Engagement question

**Twitter/X** (280 chars, 2 hashtags):
- Key insight in 240 chars
- 2 hashtags + link

**Pinterest** (500 chars, 5 hashtags):
- Keyword-rich description
- "Save for later" prompt
- What you'll learn bullets

**Google My Business** (1500 chars, no hashtags):
- Local/professional tone
- Helpful tip or update
- CTA to website

### Step 2: Banner Image Generation
Run `scripts/image_generator.py` for each platform size:
- Blog: 1200×628px
- Instagram: 1080×1080px
- Instagram Story: 1080×1920px
- Facebook: 1200×630px
- LinkedIn: 1200×627px
- Twitter: 1200×675px
- GMB: 1200×900px
- Pinterest: 1000×1500px

Each banner includes:
- Background photo (from Unsplash based on keyword)
- Your logo (top-left corner from `assets/logo.png`)
- Post title text overlay (centered, readable)
- Brand color bar at bottom with site name
- Keyword hashtag tag

### Step 3: Publish
Run `scripts/social_publisher.py` with generated content and images.

### Step 4: Log
All posts logged to `data/social-publish-log.json`

## Output
```
✅ Instagram: Posted (ID: xxx)
✅ Facebook: Posted (ID: xxx)
✅ LinkedIn: Posted (ID: xxx)
✅ Twitter: Tweeted (ID: xxx)
✅ Pinterest: Pinned (ID: xxx)
✅ GMB: Posted
📊 Published: 6/6 platforms
🖼️  Banners saved to: output/images/
📝 Log: data/social-publish-log.json
```

---

# /dm schedule — Set Up Automated Daily Social Media Posting

You are the Digital Marketing Scheduler. When invoked with `/dm schedule`, set up and manage the automated daily posting schedule.

## Setup Commands
```bash
/dm schedule setup           # Interactive setup wizard
/dm schedule status          # Show what's scheduled
/dm schedule run-now         # Trigger all today's posts immediately
/dm schedule install-cron    # Install cron jobs for auto-posting
/dm schedule preview         # Show what would post today without posting
/dm schedule pause           # Pause all scheduled posting
/dm schedule resume          # Resume scheduled posting
```

## How It Works

The scheduler reads keywords from `config/keywords.md` and:
1. Picks a random keyword from the queue
2. Generates platform-specific content for each social platform
3. Creates banner images with your logo and brand colors
4. Posts at random times within configured windows (natural-looking)
5. GMB posts every 3 days (or twice daily) at random times
6. Logs every post to `data/dm-scheduler-log.json`

## To Enable
Edit `config/schedule.json`:
```json
"social_media": {
  "instagram": { "enabled": true, ... },
  "facebook":  { "enabled": true, ... },
  "gmb":       { "enabled": true, "frequency": "every_3_days" }
}
```

## Run Python Directly
```bash
python3 scripts/dm_scheduler.py --run       # Run today's posts
python3 scripts/dm_scheduler.py --install-cron  # Install 3x daily cron
python3 scripts/dm_scheduler.py --preview   # Preview without posting
python3 scripts/dm_scheduler.py --status    # Show status
```

---

# /dm report — Digital Marketing Performance Report

Generate a report of all digital marketing activity:
- Posts published by platform (last 7/30 days)
- Engagement rates (if platform APIs support it)
- Most used topics/keywords
- Top performing content
- Recommendations for next week

Save to: `reports/dm-report-[date].md`

---

# /dm banner — Generate Banner Images Only

Generate banner images without posting:

```bash
/dm banner "Your Post Title" --keyword "seo tips" --type all
/dm banner "Your Title" --type instagram
/dm banner "Your Title" --type blog
```

Runs: `python3 scripts/image_generator.py --title "..." --keyword "..." --type all`

Images saved to: `output/images/`

Supports: blog, instagram, instagram_story, facebook, linkedin, twitter, gmb, pinterest, youtube

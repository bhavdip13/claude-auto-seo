# /publish-external — Publish to Medium, Reddit, LinkedIn & More

You are the External Publisher for Claude Auto SEO. When invoked with `/publish-external [file] [platform]`, adapt and publish content to external platforms for backlinks and brand visibility.

## Supported Platforms

| Platform | Type | SEO Benefit | Auth Method |
|---|---|---|---|
| Medium | Blog | Dofollow canonical backlink | API Token |
| Reddit | Discussion | Traffic + brand awareness | OAuth2 |
| LinkedIn | Article | Professional authority | API Token |
| Dev.to | Dev blog | Tech audience + dofollow | API Key |
| Hashnode | Dev blog | Strong DA + dofollow | API Key |

---

## Platform Strategies

### Medium
- Republish full article with canonical link back to original WordPress post
- Canonical prevents duplicate content penalty
- Add "Originally published at [your site]" at bottom
- Use Medium tags to maximize discovery
- Import directly via Medium API

**Required in .env:**
```
MEDIUM_INTEGRATION_TOKEN=your_token
```

**Auto-action:** Set canonical URL to original WordPress post URL

---

### Reddit
- Do NOT just post your article link (will be removed as spam)
- Instead: write a genuine value-add comment or post
- Extract 3-5 key insights from article
- Post as discussion/question with insights + link as resource
- Target relevant subreddits from `config/schedule.json`
- Timing: post when subreddit is most active

**Reddit Post Format:**
```
Title: [Question or insight about the topic — no clickbait]

Body:
[2-3 paragraph genuine value add]
[Key insight 1]
[Key insight 2]
[Key insight 3]

I wrote a more detailed guide here if useful: [link]
What's your experience with [topic]?
```

**Required in .env:**
```
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

---

### LinkedIn Article
- Repurpose as professional insight piece
- Shorter (1,200-1,500 words)
- More business-focused angle
- End with question to drive comments
- Add "Full guide at: [link]"

**Required in .env:**
```
LINKEDIN_ACCESS_TOKEN=your_token
```

---

### Dev.to / Hashnode (for tech sites)
- Full article republish with canonical
- Add relevant tags
- Both have very active communities

**Required in .env:**
```
DEVTO_API_KEY=your_key
HASHNODE_API_KEY=your_key
HASHNODE_PUBLICATION_ID=your_pub_id
```

---

## Command Usage

```bash
# Publish to specific platform
/publish-external drafts/my-article.md medium
/publish-external drafts/my-article.md reddit --subreddit r/SEO
/publish-external drafts/my-article.md linkedin

# Publish to all configured platforms
/publish-external drafts/my-article.md all

# Generate platform-adapted version without publishing (review first)
/publish-external drafts/my-article.md medium --dry-run
```

## Adaptation Process

For each platform, Claude will:
1. Load the original article
2. Adapt title for platform conventions
3. Adjust tone if needed (Reddit = casual, LinkedIn = professional)
4. Strip or adapt internal WordPress links
5. Add platform-appropriate tags/hashtags
6. Set canonical URL back to WordPress post
7. Publish via API
8. Log to `data/external-publish-log.json`

## Output After Publishing

```
✅ Published to Medium
   URL: https://medium.com/@you/your-article-slug
   Canonical: https://yoursite.com/your-post/
   
✅ Posted to Reddit r/SEO
   URL: https://reddit.com/r/SEO/comments/xxx
   
⚠️  LinkedIn: Token expired — run /publish-external --reauth linkedin

📊 External Publishing Summary:
   Platforms published: 2/3
   New backlinks created: 2
   Estimated reach: 5,000-15,000 readers
```

Log: `data/external-publish-log.json`

## Scheduled External Publishing

Add to `config/schedule.json`:
```json
"external_platforms": {
  "medium": {
    "enabled": true,
    "frequency": "weekly",
    "day": "wednesday",
    "time": "10:00",
    "canonical_to_wordpress": true
  },
  "reddit": {
    "enabled": true,
    "frequency": "weekly", 
    "day": "thursday",
    "subreddits": ["r/SEO", "r/Entrepreneur", "r/YoursNiche"],
    "time": "14:00"
  }
}
```

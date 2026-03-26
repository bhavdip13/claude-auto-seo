# Agent: Landing Page Optimizer

**Auto-triggers after:** `/landing-write`, `/landing-audit`
**Purpose:** Comprehensive landing page optimization combining SEO + CRO

## Combined Score (SEO + CRO = 100)

### SEO Component (50 pts)
- Title tag and meta description: 10 pts
- H1 with primary keyword: 10 pts
- Content depth (800+ words): 10 pts
- Schema markup (WebPage + FAQPage): 10 pts
- Page speed signals: 10 pts

### CRO Component (50 pts)
- Above-fold effectiveness: 10 pts
- CTA quality: 10 pts
- Trust signals: 10 pts
- Friction level: 10 pts
- Social proof: 10 pts

## Output

```markdown
## Landing Page Optimizer Report

### Combined Score: [X]/100
SEO: [X]/50 | CRO: [X]/50

### 🚀 Priority Action Plan

**Do Today (Highest Impact):**
1. [Action] — Impact: +[n] pts

**Do This Week:**
2. [Action]

**Ongoing Optimization:**
3. [Action]

### A/B Test Priority Queue
1. [Test idea with highest expected impact]
```

---

# Agent: Social Media Content Creator

**Auto-triggers after:** `/dm post`, `/write` (when social sharing enabled)
**Purpose:** Generate platform-specific social media content from articles/topics

## Platform Content Specs

| Platform | Max Chars | Hashtags | Tone | Best Format |
|---|---|---|---|---|
| Instagram | 2,200 | 25 | Visual, inspiring | Hook + bullets + CTA |
| Facebook | 63,206 | 5 | Conversational | Story + question |
| LinkedIn | 3,000 | 5 | Professional | Insight + takeaways |
| Twitter/X | 280 | 2 | Punchy, direct | Key insight + link |
| Pinterest | 500 | 5 | Keyword-rich | Save-worthy description |
| GMB | 1,500 | 0 | Local, helpful | Tip + CTA to site |
| TikTok | 150 (caption) | 5 | Trendy, casual | Hook + value |

## Content Generation Rules

1. **Never copy-paste** between platforms — each needs platform-native voice
2. **Instagram:** Start with emoji + hook. End with "link in bio ☝️" + 20+ hashtags
3. **LinkedIn:** Start with bold insight. Use numbered list. End with question for comments
4. **Twitter:** Lead with the most interesting fact or tip. 240 chars + 2 tags + link
5. **Facebook:** More conversational. Tell a mini story. Ask a question to drive comments
6. **GMB:** No hashtags. Professional, helpful. Direct CTA to website

## Hashtag Strategy
- Load hashtags from `config/keywords.md` hashtag section
- Mix: 5 high-volume + 10 medium + 10 niche-specific
- Include: brand hashtag, keyword hashtag, niche hashtags
- Never use: banned hashtags, irrelevant trending tags

## Output Per Platform

```
### [Platform] Content
[Content body]

Hashtags: [list]
Image: [size recommendation]
Best time to post: [day + time window]
```

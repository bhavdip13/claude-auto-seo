# /content research — Keyword & Competitor Research Brief

You are the Research Agent for Claude Auto SEO. When invoked with `/content research <topic>`, produce a comprehensive research brief before writing.

## Research Steps

### 1. Keyword Analysis
- Primary keyword: exact match, search volume estimate
- Secondary keywords: 5-10 related terms
- LSI keywords: semantically related terms
- Long-tail variations: 5-8 question-based keywords
- Search intent: informational / commercial / transactional / navigational
- Keyword difficulty: low / medium / high

### 2. SERP Analysis (Top 10)
For each of the top 10 ranking pages:
- URL and title
- Estimated word count
- Content type (guide, listicle, comparison, etc.)
- Key H2 headings used
- SERP features present (Featured Snippet, PAA, etc.)
- Unique angle or differentiator

### 3. Content Gap Analysis
- Topics covered by all top 10 (must-cover)
- Topics covered by 50%+ (should-cover)
- Topics NOT covered by any (opportunity)
- Questions from "People Also Ask"
- Related searches at bottom of SERP

### 4. Recommended Article Blueprint
```
Title: [Primary keyword — compelling hook]
Word Count Target: [n] words (based on top 10 average + 10%)
Search Intent: [intent type]
Content Type: [type]

Outline:
H1: [Full title]
  H2: Introduction — [hook approach]
  H2: [Section 1]
    H3: [Subsection]
  H2: [Section 2]
  ...
  H2: FAQ
  H2: Conclusion + CTA

Internal Links: [3-5 pages from context/internal-links-map.md]
External Links: [2-3 authority sources to cite]
Meta Title: [50-60 chars]
Meta Description: [150-160 chars]
```

## Output
Save to: `research/brief-[slug]-[YYYY-MM-DD].md`
After saving, ask: "Ready to write this article? Run `/content write [topic]`"

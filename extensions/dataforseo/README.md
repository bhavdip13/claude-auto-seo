# DataForSEO Extension

Integrates Claude Auto SEO with DataForSEO API for live SERP data, keyword research, backlinks, and AI visibility tracking.

## Features

- Live SERP results for any keyword
- Keyword search volume and difficulty
- Backlink analysis
- On-page SEO data
- AI mention tracking (brand in ChatGPT, Perplexity responses)
- Competitor keyword gaps

## Setup

### 1. Get DataForSEO Credentials
Sign up at https://dataforseo.com — free trial available.

### 2. Add Credentials to .env
```env
DATAFORSEO_LOGIN=your_email@example.com
DATAFORSEO_PASSWORD=your_api_password
```

### 3. Install Extension
```bash
./extensions/dataforseo/install.sh
```

## Commands Available After Install

```bash
/seo dataforseo serp <keyword>          # Live SERP results
/seo dataforseo keywords <topic>        # Keyword research
/seo dataforseo backlinks <domain>      # Backlink analysis
/seo dataforseo on-page <url>          # On-page SEO data
/seo dataforseo ai-mentions <brand>    # Track brand in AI answers
/seo dataforseo competitor <domain>    # Competitor keyword data
/seo dataforseo rank-check <keyword>   # Current ranking for keyword
```

## API Cost Notes

DataForSEO charges per API call. Approximate costs:
- SERP results: ~$0.003 per request
- Keyword data: ~$0.002 per keyword
- Backlinks: ~$0.005 per domain

Claude Auto SEO caches results for 24 hours to minimize API calls.
Cache stored in: `data/dataforseo-cache/`

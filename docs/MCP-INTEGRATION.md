# MCP Integration Guide

Claude Auto SEO integrates with several MCP (Model Context Protocol) servers to provide live data.

---

## Available MCP Integrations

| MCP Server | Purpose | Required? |
|---|---|---|
| DataForSEO | SERP data, keywords, backlinks | Recommended |
| Google Search Console | Rankings, impressions, CTR | Recommended |
| Google Analytics 4 | Traffic, conversions | Recommended |
| Ahrefs | Backlinks, keyword data | Optional |
| Semrush | Full SEO suite | Optional |

---

## DataForSEO MCP

### Setup
1. Sign up at https://dataforseo.com
2. Add to `.env`:
   ```
   DATAFORSEO_LOGIN=email@example.com
   DATAFORSEO_PASSWORD=your_password
   ```
3. Install extension:
   ```bash
   ./extensions/dataforseo/install.sh
   ```

### Commands Unlocked
```
/seo dataforseo serp <keyword>
/seo dataforseo keywords <topic>
/seo dataforseo backlinks <domain>
/seo dataforseo on-page <url>
/seo dataforseo ai-mentions <brand>
```

---

## Google Search Console

### Setup
1. Create Google Cloud service account
2. Download JSON key → save as `config/google-service-account.json`
3. Add service account email to GSC property (as Owner)
4. Add to `.env`:
   ```
   GSC_SITE_URL=https://yoursite.com
   GOOGLE_APPLICATION_CREDENTIALS=config/google-service-account.json
   ```

### Data Available
- Keyword positions by URL
- Click and impression data
- CTR by query
- Crawl errors

---

## Google Analytics 4

### Setup
1. Use same service account as GSC
2. Add to `.env`:
   ```
   GA4_PROPERTY_ID=123456789
   GOOGLE_APPLICATION_CREDENTIALS=config/google-service-account.json
   ```

### Data Available
- Organic traffic by page
- Conversion rates
- User behavior metrics
- Traffic source breakdown

---

## Ahrefs MCP

### Setup
1. Get API key from https://ahrefs.com/api
2. Add MCP server in Claude Code settings:
   ```json
   {
     "mcpServers": {
       "ahrefs": {
         "command": "npx",
         "args": ["-y", "@ahrefs/mcp"],
         "env": { "AHREFS_API_KEY": "your_key" }
       }
     }
   }
   ```

---

## Claude Code MCP Config

Add to your Claude Code MCP configuration (`~/.claude/mcp.json`):

```json
{
  "mcpServers": {
    "dataforseo": {
      "command": "python3",
      "args": ["extensions/dataforseo/mcp_server.py"],
      "env": {
        "DATAFORSEO_LOGIN": "${DATAFORSEO_LOGIN}",
        "DATAFORSEO_PASSWORD": "${DATAFORSEO_PASSWORD}"
      }
    }
  }
}
```

---

## Without MCP (Fallback Mode)

Claude Auto SEO works without any MCP integrations. In fallback mode:
- Audits use web search for SERP data
- Keyword volumes are estimated
- Backlink data is unavailable
- Rankings are checked via web search

For best results, connect at least DataForSEO and Google Search Console.

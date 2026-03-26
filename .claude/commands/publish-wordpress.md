# /publish wordpress — Auto-Publish to WordPress with Yoast SEO

You are the WordPress Publisher Agent for Claude Auto SEO. When invoked with `/publish wordpress <file>`, publish the article to WordPress via REST API with full Yoast SEO metadata.

## Pre-Publish Checklist

Before publishing, verify:
- [ ] Article has a primary keyword
- [ ] Meta title is 50-60 characters
- [ ] Meta description is 150-160 characters
- [ ] Article has at least 3 internal links
- [ ] At least one image included
- [ ] SEO score ≥ 70/100

If any check fails, warn the user and ask to proceed anyway.

## Publishing Process

### 1. Parse the Markdown File
Extract:
- Title (H1)
- Content (full body)
- Meta title (from agent report or generate)
- Meta description (from agent report or generate)
- Focus keyword (from front matter or filename)
- Categories and tags (from content analysis)
- Featured image URL (if specified)

### 2. Convert Markdown to HTML
- Convert headings, bold, italic, lists, links
- Preserve code blocks
- Convert internal links to proper WordPress slugs

### 3. Call WordPress REST API
```
POST /wp-json/wp/v2/posts
Authorization: Basic [base64 of user:app_password]

{
  "title": "[title]",
  "content": "[html content]",
  "status": "draft", // Default to draft — user changes to publish
  "categories": [...],
  "tags": [...],
  "yoast_meta": {
    "yoast_wpseo_title": "[meta title]",
    "yoast_wpseo_metadesc": "[meta description]",
    "yoast_wpseo_focuskw": "[focus keyword]"
  }
}
```

### 4. Confirm Success
```
✅ Published to WordPress (Draft)
URL: https://yoursite.com/wp-admin/post.php?post=[id]&action=edit
Title: [title]
Status: Draft (review before publishing live)
Yoast SEO: ✅ Title, Description, Focus Keyword set
```

## Configuration Required
In `.env`:
```
WP_URL=https://yoursite.com
WP_USERNAME=your_username
WP_APP_PASSWORD=your_app_password
```

If not configured, provide setup instructions and offer to save credentials.

## After Publishing
- Move article file from `drafts/` to `published/`
- Log in `data/publish-log.json`
- Update `context/internal-links-map.md` with new URL

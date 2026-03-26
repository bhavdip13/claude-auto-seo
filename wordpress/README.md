# WordPress Integration Guide

Claude Auto SEO can auto-publish articles directly to WordPress with full Yoast SEO metadata.

---

## Files Included

| File | Purpose |
|---|---|
| `claude-auto-seo-yoast-rest.php` | MU-plugin: exposes Yoast fields via REST API |
| `../data_sources/modules/wordpress_publisher.py` | Python: handles publishing logic |

---

## Installation Steps

### Step 1: Install the MU Plugin

Copy `claude-auto-seo-yoast-rest.php` to your WordPress:
```
wp-content/mu-plugins/claude-auto-seo-yoast-rest.php
```

MU-plugins (Must-Use plugins) load automatically — no activation needed.

**Verify it's working:**
Visit: `https://yoursite.com/wp-json/wp/v2/posts?per_page=1`
You should see `yoast_wpseo_title` and `yoast_wpseo_metadesc` in the response.

### Step 2: Create Application Password

1. Log in to WordPress Admin
2. Go to **Users → Your Profile**
3. Scroll to **"Application Passwords"** section
4. Name: `Claude Auto SEO`
5. Click **"Add New Application Password"**
6. **Copy the generated password immediately** (shown only once)

### Step 3: Add Credentials to .env

```env
WP_URL=https://yoursite.com
WP_USERNAME=your_wordpress_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

---

## Usage

### Via Claude Code Command
```
/publish wordpress drafts/my-article-2026-03-16.md
```

### Via Python Script Directly
```bash
python3 data_sources/modules/wordpress_publisher.py drafts/my-article.md
```

---

## Article Front Matter

Add YAML front matter to your markdown files for full control:

```markdown
---
title: My Article Title
seo_title: SEO Title — 55 chars max | Brand
meta_description: Your 150-160 char meta description with CTA.
focus_keyword: primary keyword here
categories: SEO, Content Marketing
tags: seo tips, content strategy
status: draft
featured_image: https://yoursite.com/image.jpg
canonical: https://yoursite.com/canonical-url/
---

# My Article Title

Article content here...
```

### Status Options
- `draft` — Saved but not published (recommended for review)
- `publish` — Goes live immediately
- `private` — Only visible to admins

---

## Troubleshooting

### 401 Unauthorized
- Make sure you're using the **Application Password**, not your login password
- Application passwords have spaces in them — include them as-is

### 404 Not Found
- Verify `WP_URL` is correct and doesn't have a trailing slash issue
- Test: `curl -u username:app_password https://yoursite.com/wp-json/wp/v2/posts`

### Yoast fields not saving
- Verify the MU plugin is installed at `wp-content/mu-plugins/`
- Check PHP error log for plugin conflicts

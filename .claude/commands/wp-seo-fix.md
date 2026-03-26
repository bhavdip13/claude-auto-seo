# /wp-seo-fix — WordPress SEO Auto-Scanner & Auto-Fixer

You are the WordPress SEO Doctor for Claude Auto SEO. This is the most powerful command — it connects to your live WordPress site via the REST API, scans every page, identifies ALL SEO issues, shows you a full report, and then fixes everything automatically.

## What This Does

1. **Scans your entire WordPress site** via REST API
2. **Identifies every SEO issue** across all posts/pages
3. **Shows you a complete report** with issue severity
4. **Asks for your confirmation** to fix
5. **Automatically applies all fixes** via REST API
6. **Verifies fixes were applied** correctly

---

## Phase 1: Full Site Scan

```bash
/wp-seo-fix scan https://yoursite.com
```

### What It Scans

#### All Posts & Pages
For every published post and page:
- Missing meta title → flag + generate
- Missing meta description → flag + generate
- Meta title > 60 chars → flag + trim
- Meta description > 160 chars → flag + trim
- Missing focus keyword (Yoast) → flag + suggest
- Missing H1 → flag
- Multiple H1s → flag
- H1 doesn't contain focus keyword → flag + suggest fix
- Missing alt text on images → flag + generate alt text
- Thin content (< 300 words for posts) → flag
- No internal links → flag + suggest links
- Broken internal links → flag
- Duplicate meta titles → flag all instances

#### Site-Wide Technical
- Sitemap exists and is valid → check
- Robots.txt exists and not blocking important pages → check
- HTTPS on all pages → check
- Schema markup on homepage → check + generate if missing
- Organization/WebSite schema → check + generate
- Blog page has BlogPosting schema → check

#### Yoast SEO Settings (if installed)
- Title separator set → check
- Site tagline SEO-optimized → check
- Social meta (OG/Twitter) enabled → check
- XML sitemaps enabled → check

### Scan Output
```markdown
# WordPress SEO Scan Report
Site: https://yoursite.com
Scanned: [n] posts | [n] pages | [n] other
Date: [date]

## 🔴 Critical Issues ([n] found)
| URL | Issue | Severity | Auto-Fixable |
|---|---|---|---|
| /blog/post-1 | Missing meta description | Critical | ✅ Yes |
| /about | Meta title too long (72 chars) | High | ✅ Yes |

## 🟡 High Priority Issues ([n] found)
...

## 🟢 Optimization Opportunities ([n] found)
...

## ✅ Passing ([n] checks)
...

## Summary
- Total issues: [n]
- Auto-fixable: [n] ([%])
- Manual review needed: [n]
- Estimated fix time if done manually: [n] hours
- Auto-fix time: ~[n] minutes

Ready to auto-fix all [n] fixable issues? 
Run: /wp-seo-fix apply
```

---

## Phase 2: Auto-Fix All Issues

After reviewing the scan report:

```bash
/wp-seo-fix apply
```

Or fix specific types only:
```bash
/wp-seo-fix apply --meta-only        # Only fix title/description
/wp-seo-fix apply --images-only      # Only fix image alt text
/wp-seo-fix apply --post-id 123      # Fix one specific post
```

### What It Fixes Automatically

#### Meta Titles (Missing/Wrong Length)
- Generate SEO-optimized title (50-60 chars)
- Include focus keyword near start
- Include brand name if space allows
- Update via Yoast REST API field `yoast_wpseo_title`

#### Meta Descriptions (Missing/Wrong Length)
- Generate compelling 150-160 char description
- Include focus keyword naturally
- Include a benefit/CTA
- Update via `yoast_wpseo_metadesc`

#### Image Alt Text (Missing)
- Read image filename and surrounding content
- Generate descriptive, keyword-relevant alt text
- Update via WordPress Media REST API

#### Schema Markup (Missing/Broken)
- Add `Organization` + `WebSite` schema to homepage
- Add `Article`/`BlogPosting` schema to blog posts
- Add `BreadcrumbList` to all pages
- Inject as JSON-LD via WordPress REST API

#### Internal Links (Zero Internal Links)
- Find 2-3 relevant pages from `context/internal-links-map.md`
- Suggest specific sentences to add links in
- With `--auto-insert` flag: automatically insert into content

#### Focus Keywords (Missing Yoast Focus Keyword)
- Detect primary keyword from title and content
- Set `yoast_wpseo_focuskw` via REST API

### Fix Progress Output
```
Applying fixes to [n] issues...

✅ Fixed meta description: /blog/post-1
✅ Fixed meta description: /blog/post-2
✅ Fixed image alt text: 14 images across 8 posts
✅ Added schema to homepage
✅ Set focus keywords: 23 posts
⚠️  Skipped /blog/post-3 — needs manual review (ambiguous keyword)
⚠️  Skipped /contact — page too short for automated fix

Results:
- Fixed: [n] issues
- Skipped: [n] (manual review needed)
- Failed: [n] (see errors below)
- Time taken: [n] seconds

Run /wp-seo-fix scan again to verify all fixes applied.
```

---

## Phase 3: Verify Fixes

```bash
/wp-seo-fix verify
```

Re-runs the scan and compares to the previous report to confirm all fixes are in place.

```
Verification Report:
- Issues before: [n]
- Issues after: [n]  
- Issues resolved: [n] ✅
- New issues detected: [n] (investigate)
- Overall SEO improvement: +[n] pts
```

---

## Credentials Required

In `.env`:
```
WP_URL=https://yoursite.com
WP_USERNAME=your_wordpress_username
WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
```

WordPress Application Password provides:
- Read access to all posts, pages, media
- Write access to update post meta (Yoast fields)
- Write access to update media alt text
- NO access to: admin panel, user management, core settings

The App Password is safe — it cannot delete your site or change admin settings.

---

## Run the Python Script Directly

```bash
# Full scan
python3 scripts/wp_seo_fixer.py --scan

# Apply all fixes
python3 scripts/wp_seo_fixer.py --apply

# Verify fixes
python3 scripts/wp_seo_fixer.py --verify

# Fix one post
python3 scripts/wp_seo_fixer.py --fix-post 123
```

---

## Safety Guarantees
- Never deletes any content
- Never changes post status (draft stays draft, published stays published)
- Creates backup log before any changes: `data/wp-fix-backup-[date].json`
- All changes are reversible via the backup log
- Run `python3 scripts/wp_seo_fixer.py --rollback` to undo all changes

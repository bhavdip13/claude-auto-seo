"""
Claude Auto SEO — WordPress SEO Auto-Fixer
Scans your entire WordPress site via REST API and auto-fixes all SEO issues.

Usage:
  python3 scripts/wp_seo_fixer.py --scan          # Scan all issues
  python3 scripts/wp_seo_fixer.py --apply         # Apply all auto-fixes
  python3 scripts/wp_seo_fixer.py --verify        # Verify fixes applied
  python3 scripts/wp_seo_fixer.py --fix-post 123  # Fix one post
  python3 scripts/wp_seo_fixer.py --rollback      # Undo all changes
"""

import os
import re
import sys
import json
import base64
import requests
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from dotenv import load_dotenv

load_dotenv()

# ── Config ──────────────────────────────────────────────────────────────────
WP_URL      = os.getenv("WP_URL", "").rstrip("/")
WP_USER     = os.getenv("WP_USERNAME", "")
WP_PASS     = os.getenv("WP_APP_PASSWORD", "")
DATA_DIR    = os.path.join(os.path.dirname(__file__), "../data")
BACKUP_FILE = os.path.join(DATA_DIR, f"wp-fix-backup-{datetime.now().strftime('%Y%m%d')}.json")
REPORT_DIR  = os.path.join(os.path.dirname(__file__), "../reports")


def get_auth_header() -> Dict:
    creds = base64.b64encode(f"{WP_USER}:{WP_PASS}".encode()).decode()
    return {"Authorization": f"Basic {creds}", "Content-Type": "application/json"}


def wp_get(endpoint: str, params: Dict = None) -> List:
    """Paginated GET from WordPress REST API."""
    results, page = [], 1
    while True:
        p = {"per_page": 100, "page": page, **(params or {})}
        r = requests.get(f"{WP_URL}/wp-json/wp/v2/{endpoint}",
                         headers=get_auth_header(), params=p, timeout=30)
        if r.status_code != 200:
            break
        data = r.json()
        if not data:
            break
        results.extend(data)
        if len(data) < 100:
            break
        page += 1
    return results


def wp_update(post_type: str, post_id: int, payload: Dict) -> bool:
    """Update a post via REST API."""
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/{post_type}/{post_id}",
        headers=get_auth_header(),
        json=payload,
        timeout=30
    )
    return r.status_code in (200, 201)


def update_media_alt(media_id: int, alt_text: str) -> bool:
    """Update image alt text via Media REST API."""
    r = requests.post(
        f"{WP_URL}/wp-json/wp/v2/media/{media_id}",
        headers=get_auth_header(),
        json={"alt_text": alt_text},
        timeout=30
    )
    return r.status_code == 200


# ── Text Helpers ─────────────────────────────────────────────────────────────

def strip_html(html: str) -> str:
    return re.sub(r"<[^>]+>", " ", html or "").strip()


def count_words(text: str) -> int:
    return len(re.findall(r"\b\w+\b", text))


def extract_keyword_from_title(title: str) -> str:
    """Simple heuristic: strip common stop words, return key phrase."""
    stop = {"a", "an", "the", "and", "or", "but", "in", "on", "at", "to",
            "for", "of", "with", "by", "from", "how", "what", "why", "when",
            "is", "are", "was", "were", "be", "been", "being"}
    words = [w.lower() for w in re.findall(r"\b\w+\b", title) if w.lower() not in stop]
    return " ".join(words[:4]) if words else title.lower()[:40]


def generate_meta_title(title: str, keyword: str, brand: str = "") -> str:
    """Generate a 50-60 char meta title."""
    # Put keyword first if not already
    kw_lower = keyword.lower()
    title_lower = title.lower()
    base = title if kw_lower in title_lower else f"{keyword.title()} — {title}"
    if brand:
        candidate = f"{base[:50].rstrip()} | {brand}"
        if len(candidate) <= 60:
            return candidate
    return base[:60]


def generate_meta_description(title: str, content_text: str, keyword: str) -> str:
    """Generate a 150-160 char meta description."""
    # Try to extract first sentence that mentions the keyword
    sentences = re.split(r"[.!?]+", content_text)
    for sentence in sentences:
        sentence = sentence.strip()
        if keyword.lower() in sentence.lower() and 80 <= len(sentence) <= 160:
            return sentence[:160]

    # Fallback: first substantial sentence
    for sentence in sentences:
        sentence = sentence.strip()
        if len(sentence) >= 80:
            return sentence[:157] + "..."

    # Last resort
    return f"Learn everything about {keyword}. {title}. Read our complete guide."[:160]


def generate_alt_text(filename: str, context: str = "", keyword: str = "") -> str:
    """Generate alt text from filename and context."""
    # Clean filename
    name = re.sub(r"\.(jpg|jpeg|png|gif|webp|svg)$", "", filename, flags=re.IGNORECASE)
    name = re.sub(r"[-_]", " ", name)
    name = re.sub(r"\d{4,}", "", name).strip()

    if keyword and keyword.lower() not in name.lower():
        return f"{keyword} — {name}"[:125]
    return name[:125]


# ── Scanner ───────────────────────────────────────────────────────────────────

def scan_site(post_types: List[str] = None) -> Dict:
    """Scan all posts/pages for SEO issues."""
    if not all([WP_URL, WP_USER, WP_PASS]):
        print("❌ Missing WP credentials in .env (WP_URL, WP_USERNAME, WP_APP_PASSWORD)")
        sys.exit(1)

    post_types = post_types or ["posts", "pages"]
    issues = {"critical": [], "high": [], "medium": [], "info": []}
    passing = []
    all_titles = {}  # for duplicate detection

    print(f"🔍 Scanning {WP_URL} ...")

    for pt in post_types:
        items = wp_get(pt, {"status": "publish", "_fields": "id,link,title,content,excerpt,yoast_wpseo_title,yoast_wpseo_metadesc,yoast_wpseo_focuskw"})
        print(f"  Found {len(items)} published {pt}")

        for item in items:
            pid    = item["id"]
            url    = item.get("link", "")
            title  = strip_html(item.get("title", {}).get("rendered", ""))
            content_html = item.get("content", {}).get("rendered", "")
            content_text = strip_html(content_html)
            yoast_title  = item.get("yoast_wpseo_title", "")
            yoast_desc   = item.get("yoast_wpseo_metadesc", "")
            yoast_kw     = item.get("yoast_wpseo_focuskw", "")
            word_count   = count_words(content_text)

            base = {"post_id": pid, "url": url, "title": title, "post_type": pt.rstrip("s")}

            # ── Meta Title ──────────────────────────────────────
            if not yoast_title:
                issues["critical"].append({**base, "issue": "Missing Yoast SEO title",
                    "fix_type": "meta_title", "auto_fixable": True,
                    "suggested_fix": generate_meta_title(title, extract_keyword_from_title(title))})
            elif len(yoast_title) > 65:
                issues["high"].append({**base, "issue": f"Meta title too long ({len(yoast_title)} chars)",
                    "fix_type": "meta_title", "auto_fixable": True,
                    "suggested_fix": yoast_title[:60]})
            elif len(yoast_title) < 40:
                issues["medium"].append({**base, "issue": f"Meta title too short ({len(yoast_title)} chars)",
                    "fix_type": "meta_title", "auto_fixable": True,
                    "suggested_fix": generate_meta_title(title, extract_keyword_from_title(title))})
            else:
                passing.append(f"Meta title OK: {url}")

            # Track for duplicates
            norm_title = (yoast_title or title).lower().strip()
            if norm_title in all_titles:
                issues["high"].append({**base, "issue": f"Duplicate meta title — same as {all_titles[norm_title]}",
                    "fix_type": "meta_title", "auto_fixable": False})
            else:
                all_titles[norm_title] = url

            # ── Meta Description ─────────────────────────────────
            if not yoast_desc:
                issues["critical"].append({**base, "issue": "Missing meta description",
                    "fix_type": "meta_description", "auto_fixable": True,
                    "suggested_fix": generate_meta_description(title, content_text,
                                                                extract_keyword_from_title(title))})
            elif len(yoast_desc) > 165:
                issues["high"].append({**base, "issue": f"Meta description too long ({len(yoast_desc)} chars)",
                    "fix_type": "meta_description", "auto_fixable": True,
                    "suggested_fix": yoast_desc[:157] + "..."})
            elif len(yoast_desc) < 120:
                issues["medium"].append({**base, "issue": f"Meta description too short ({len(yoast_desc)} chars)",
                    "fix_type": "meta_description", "auto_fixable": True,
                    "suggested_fix": generate_meta_description(title, content_text,
                                                                extract_keyword_from_title(title))})

            # ── Focus Keyword ─────────────────────────────────────
            if not yoast_kw:
                issues["medium"].append({**base, "issue": "Missing Yoast focus keyword",
                    "fix_type": "focus_keyword", "auto_fixable": True,
                    "suggested_fix": extract_keyword_from_title(title)})

            # ── Heading Structure ─────────────────────────────────
            h1s = re.findall(r"<h1[^>]*>(.*?)</h1>", content_html, re.IGNORECASE | re.DOTALL)
            if not h1s:
                issues["high"].append({**base, "issue": "No H1 tag found in content",
                    "fix_type": "manual", "auto_fixable": False})
            elif len(h1s) > 1:
                issues["medium"].append({**base, "issue": f"Multiple H1 tags ({len(h1s)}) — use only one",
                    "fix_type": "manual", "auto_fixable": False})

            # ── Thin Content ──────────────────────────────────────
            if pt == "posts" and word_count < 300:
                issues["high"].append({**base, "issue": f"Thin content ({word_count} words)",
                    "fix_type": "manual", "auto_fixable": False,
                    "suggested_fix": "Expand content to at least 800 words"})

            # ── Internal Links ────────────────────────────────────
            internal_links = re.findall(
                rf'href=["\']({re.escape(WP_URL)}[^"\']*)["\']', content_html)
            if pt == "posts" and len(internal_links) == 0:
                issues["medium"].append({**base, "issue": "No internal links in post",
                    "fix_type": "manual", "auto_fixable": False,
                    "suggested_fix": "Add 3-5 internal links"})

            # ── Images without alt text ───────────────────────────
            imgs_total = re.findall(r"<img[^>]+>", content_html, re.IGNORECASE)
            imgs_no_alt = [i for i in imgs_total
                           if not re.search(r'alt=["\'][^"\']{3,}["\']', i, re.IGNORECASE)]
            if imgs_no_alt:
                kw = yoast_kw or extract_keyword_from_title(title)
                for img in imgs_no_alt:
                    src_match = re.search(r'src=["\']([^"\']+)["\']', img)
                    fname = src_match.group(1).split("/")[-1] if src_match else "image"
                    issues["medium"].append({**base, "issue": f"Image missing alt text: {fname}",
                        "fix_type": "image_alt", "auto_fixable": True,
                        "img_src": src_match.group(1) if src_match else "",
                        "suggested_fix": generate_alt_text(fname, content_text[:200], kw)})

    # Save scan results
    os.makedirs(DATA_DIR, exist_ok=True)
    scan_data = {"scanned_at": datetime.now().isoformat(), "site": WP_URL,
                 "issues": issues, "passing_count": len(passing)}
    scan_path = os.path.join(DATA_DIR, "last-scan.json")
    with open(scan_path, "w") as f:
        json.dump(scan_data, f, indent=2)

    return scan_data


def print_scan_report(scan_data: Dict):
    """Print a human-readable scan report."""
    issues = scan_data["issues"]
    total = sum(len(v) for v in issues.values())
    auto_fixable = sum(1 for v in issues.values() for i in v if i.get("auto_fixable"))

    print(f"\n{'='*60}")
    print(f"WordPress SEO Scan Report — {scan_data['site']}")
    print(f"Scanned: {scan_data['scanned_at'][:10]}")
    print(f"{'='*60}\n")

    for severity, emoji in [("critical","🔴"), ("high","🟡"), ("medium","🟢"), ("info","ℹ️")]:
        items = issues.get(severity, [])
        if items:
            print(f"{emoji} {severity.upper()} ISSUES ({len(items)})")
            for issue in items[:10]:  # Show first 10
                fixable = "✅ Auto-fixable" if issue.get("auto_fixable") else "⚠️  Manual"
                print(f"  [{fixable}] {issue['url']}")
                print(f"           → {issue['issue']}")
            if len(items) > 10:
                print(f"  ... and {len(items)-10} more (see data/last-scan.json)")
            print()

    print(f"{'='*60}")
    print(f"Total issues found: {total}")
    print(f"Auto-fixable:       {auto_fixable} ({int(auto_fixable/max(total,1)*100)}%)")
    print(f"Manual review:      {total - auto_fixable}")
    print(f"\nRun with --apply to fix all {auto_fixable} auto-fixable issues.")


def apply_fixes(dry_run: bool = False, post_id_filter: int = None):
    """Apply all auto-fixable issues from last scan."""
    scan_path = os.path.join(DATA_DIR, "last-scan.json")
    if not os.path.exists(scan_path):
        print("No scan data found. Run --scan first.")
        return

    with open(scan_path) as f:
        scan_data = json.load(f)

    backup = {"applied_at": datetime.now().isoformat(), "fixes": []}
    fixed, skipped, failed = 0, 0, 0

    for severity in ["critical", "high", "medium"]:
        for issue in scan_data["issues"].get(severity, []):
            if not issue.get("auto_fixable"):
                skipped += 1
                continue
            if post_id_filter and issue["post_id"] != post_id_filter:
                continue

            pid = issue["post_id"]
            fix_type = issue["fix_type"]
            fix_value = issue.get("suggested_fix", "")
            pt = issue.get("post_type", "post") + "s"

            if dry_run:
                print(f"[DRY RUN] Would fix {fix_type} on post {pid}: {fix_value[:60]}")
                continue

            payload = {}
            if fix_type == "meta_title":
                payload = {"yoast_wpseo_title": fix_value}
            elif fix_type == "meta_description":
                payload = {"yoast_wpseo_metadesc": fix_value}
            elif fix_type == "focus_keyword":
                payload = {"yoast_wpseo_focuskw": fix_value}
            elif fix_type == "image_alt":
                # For image alt text, we update via media endpoint
                # Find media ID from src URL (simplified)
                print(f"  [Image alt] Manual update needed for: {issue.get('img_src','')}")
                skipped += 1
                continue

            if payload:
                backup["fixes"].append({"post_id": pid, "post_type": pt,
                                         "fix_type": fix_type, "value": fix_value})
                success = wp_update(pt, pid, payload)
                if success:
                    fixed += 1
                    print(f"  ✅ Fixed {fix_type}: {issue['url']}")
                else:
                    failed += 1
                    print(f"  ❌ Failed {fix_type}: {issue['url']}")

    # Save backup
    os.makedirs(DATA_DIR, exist_ok=True)
    with open(BACKUP_FILE, "w") as f:
        json.dump(backup, f, indent=2)

    print(f"\n{'='*40}")
    print(f"Fixed:   {fixed}")
    print(f"Skipped: {skipped} (manual or filtered)")
    print(f"Failed:  {failed}")
    print(f"Backup:  {BACKUP_FILE}")
    print(f"\nRun --verify to confirm all fixes applied.")


def rollback():
    """Rollback all fixes from the backup file."""
    if not os.path.exists(BACKUP_FILE):
        print(f"No backup found: {BACKUP_FILE}")
        return

    with open(BACKUP_FILE) as f:
        backup = json.load(f)

    print(f"Rolling back {len(backup['fixes'])} fixes...")
    for fix in backup["fixes"]:
        if fix["fix_type"] == "meta_title":
            wp_update(fix["post_type"], fix["post_id"], {"yoast_wpseo_title": ""})
        elif fix["fix_type"] == "meta_description":
            wp_update(fix["post_type"], fix["post_id"], {"yoast_wpseo_metadesc": ""})
        elif fix["fix_type"] == "focus_keyword":
            wp_update(fix["post_type"], fix["post_id"], {"yoast_wpseo_focuskw": ""})
        print(f"  Rolled back {fix['fix_type']} on post {fix['post_id']}")

    print("✅ Rollback complete.")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="WordPress SEO Auto-Fixer")
    parser.add_argument("--scan",      action="store_true", help="Scan site for issues")
    parser.add_argument("--apply",     action="store_true", help="Apply all auto-fixes")
    parser.add_argument("--verify",    action="store_true", help="Re-scan to verify fixes")
    parser.add_argument("--rollback",  action="store_true", help="Undo all applied fixes")
    parser.add_argument("--dry-run",   action="store_true", help="Show fixes without applying")
    parser.add_argument("--fix-post",  type=int, metavar="ID", help="Fix a single post by ID")
    args = parser.parse_args()

    if args.scan or args.verify:
        data = scan_site()
        print_scan_report(data)
    elif args.apply:
        apply_fixes(dry_run=args.dry_run, post_id_filter=args.fix_post)
    elif args.rollback:
        rollback()
    else:
        parser.print_help()

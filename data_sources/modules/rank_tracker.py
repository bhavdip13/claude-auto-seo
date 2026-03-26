"""
Claude Auto SEO — Rank Tracker Module
Tracks keyword rankings over time and detects significant changes.
"""

import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "../../data")
HISTORY_FILE = os.path.join(DATA_DIR, "rankings-history.json")


def load_history() -> Dict:
    """Load rankings history from disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return {"domain": "", "tracked_keywords": [], "last_updated": None}


def save_history(data: Dict):
    """Save rankings history to disk."""
    os.makedirs(DATA_DIR, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)


def add_ranking(keyword: str, position: int, url: str = "",
                domain: str = "", serp_features: List[str] = None):
    """Record a keyword ranking check."""
    history = load_history()

    if domain and not history.get("domain"):
        history["domain"] = domain

    today = date.today().isoformat()
    entry = {
        "date": today,
        "position": position,
        "url": url,
        "serp_features": serp_features or [],
    }

    # Find or create keyword record
    kw_record = None
    for kw in history["tracked_keywords"]:
        if kw["keyword"].lower() == keyword.lower():
            kw_record = kw
            break

    if kw_record is None:
        kw_record = {
            "keyword": keyword,
            "target_url": url,
            "history": [],
            "best_position": position,
            "first_tracked": today,
        }
        history["tracked_keywords"].append(kw_record)

    # Don't duplicate today's entry
    if kw_record["history"] and kw_record["history"][-1]["date"] == today:
        kw_record["history"][-1] = entry
    else:
        kw_record["history"].append(entry)

    # Update best position
    if position < kw_record.get("best_position", 999):
        kw_record["best_position"] = position

    save_history(history)
    return entry


def get_changes(keyword: str, days_back: int = 7) -> Dict:
    """Get position changes for a keyword over the last N days."""
    history = load_history()

    for kw in history["tracked_keywords"]:
        if kw["keyword"].lower() != keyword.lower():
            continue

        hist = kw["history"]
        if len(hist) < 2:
            return {"keyword": keyword, "change": None, "message": "Not enough data yet."}

        latest = hist[-1]
        # Find entry from ~days_back ago
        compare_entry = hist[0]
        for entry in hist:
            entry_date = datetime.fromisoformat(entry["date"]).date()
            cutoff = (datetime.now() - __import__('timedelta', fromlist=['timedelta'])
                      if False else datetime.now()).date()
            compare_entry = entry

        if len(hist) >= 2:
            compare_entry = hist[-2]

        change = compare_entry["position"] - latest["position"]  # Positive = improved

        return {
            "keyword": keyword,
            "current_position": latest["position"],
            "previous_position": compare_entry["position"],
            "change": change,
            "change_direction": "up" if change > 0 else "down" if change < 0 else "stable",
            "change_label": _change_label(latest["position"], change),
            "best_position": kw.get("best_position"),
            "serp_features": latest.get("serp_features", []),
        }

    return {"keyword": keyword, "error": "Keyword not tracked."}


def _change_label(position: int, change: int) -> str:
    """Generate emoji label for position change."""
    if position <= 3 and change >= 0:
        return "🏆 Top 3"
    if position <= 10 and change > 0:
        return "⭐ Entered Top 10"
    if change >= 10:
        return f"📈 Up {change} positions"
    if change >= 3:
        return f"↑ Up {change}"
    if change <= -10:
        return f"🔴 Down {abs(change)} positions"
    if change <= -3:
        return f"↓ Down {abs(change)}"
    if change == 0:
        return "→ No change"
    return f"↑ Up {change}" if change > 0 else f"↓ Down {abs(change)}"


def get_quick_wins(min_volume: int = 100) -> List[Dict]:
    """Return keywords in positions 11-20 (quick win candidates)."""
    history = load_history()
    quick_wins = []

    for kw in history["tracked_keywords"]:
        if not kw["history"]:
            continue
        latest = kw["history"][-1]
        if 11 <= latest["position"] <= 20:
            quick_wins.append({
                "keyword": kw["keyword"],
                "position": latest["position"],
                "url": latest.get("url", kw.get("target_url", "")),
                "action": "Add internal links, expand content, improve meta title CTR",
            })

    return sorted(quick_wins, key=lambda x: x["position"])


def generate_rankings_report(domain: str = "") -> str:
    """Generate a markdown rankings report."""
    history = load_history()
    today = date.today().strftime("%B %d, %Y")

    lines = [
        f"# Keyword Rankings Report",
        f"**Site:** {domain or history.get('domain', 'your site')}",
        f"**Date:** {today}",
        f"**Keywords Tracked:** {len(history['tracked_keywords'])}",
        "",
        "## 📊 All Tracked Keywords",
        "",
        "| Keyword | Position | Change | Best Ever | SERP Features |",
        "|---|---|---|---|---|",
    ]

    for kw in sorted(history["tracked_keywords"],
                     key=lambda x: x["history"][-1]["position"] if x["history"] else 999):
        if not kw["history"]:
            continue
        latest = kw["history"][-1]
        change_data = get_changes(kw["keyword"])
        change_str = _change_label(latest["position"], change_data.get("change", 0))
        features = ", ".join(latest.get("serp_features", [])) or "—"
        lines.append(
            f"| {kw['keyword']} | #{latest['position']} | {change_str} "
            f"| #{kw.get('best_position', '—')} | {features} |"
        )

    # Quick wins section
    quick_wins = get_quick_wins()
    if quick_wins:
        lines += [
            "",
            "## ⭐ Quick Wins (Positions 11–20)",
            "",
            "| Keyword | Position | Action |",
            "|---|---|---|",
        ]
        for qw in quick_wins:
            lines.append(f"| {qw['keyword']} | #{qw['position']} | {qw['action']} |")

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo: add some rankings and generate report
    add_ranking("seo audit tool", 14, "https://example.com/seo-audit", "example.com")
    add_ranking("technical seo checklist", 8, "https://example.com/checklist", "example.com")
    add_ranking("best seo software", 23, "https://example.com/seo-software", "example.com")

    print(generate_rankings_report("example.com"))
    print("\nQuick Wins:")
    for qw in get_quick_wins():
        print(f"  #{qw['position']}: {qw['keyword']}")

"""
Claude Auto SEO — Banner Image Generator
Creates professional blog/social media banner images with:
  - Background image (fetched from Unsplash or generated)
  - Website logo overlay (top-left corner)
  - Blog title text overlay
  - Brand color overlay
  - Multiple size presets (blog, Instagram, Facebook, LinkedIn, Twitter/X, GMB)

Usage:
  python3 scripts/image_generator.py --title "My Blog Post Title" --type blog
  python3 scripts/image_generator.py --title "Post Title" --type instagram
  python3 scripts/image_generator.py --title "Post Title" --type all
"""

import os
import sys
import re
import json
import textwrap
import requests
from datetime import datetime
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

# ── Config ────────────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR  = os.path.join(BASE_DIR, "output", "images")
LOGO_PATH   = os.environ.get("LOGO_PATH", os.path.join(BASE_DIR, "assets", "logo.png"))

# Brand colors (override in .env)
BRAND_PRIMARY   = os.environ.get("BRAND_COLOR_PRIMARY",   "#0f3460")
BRAND_SECONDARY = os.environ.get("BRAND_COLOR_SECONDARY",  "#e74c3c")
BRAND_TEXT      = os.environ.get("BRAND_COLOR_TEXT",       "#ffffff")
SITE_NAME       = os.environ.get("SITE_NAME",              "Your Site")

# Image size presets
SIZES = {
    "blog":         (1200, 628),    # Blog featured image (Open Graph)
    "instagram":    (1080, 1080),   # Instagram square
    "instagram_story": (1080, 1920), # Instagram/Facebook Story
    "facebook":     (1200, 630),    # Facebook post
    "linkedin":     (1200, 627),    # LinkedIn post
    "twitter":      (1200, 675),    # Twitter/X post
    "gmb":          (1200, 900),    # Google My Business post
    "pinterest":    (1000, 1500),   # Pinterest pin
    "youtube":      (1280, 720),    # YouTube thumbnail
}


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))


def fetch_background(keyword: str, width: int, height: int) -> Optional[bytes]:
    """Fetch a relevant background image from Unsplash (free, no auth needed for basic)."""
    unsplash_key = os.environ.get("UNSPLASH_ACCESS_KEY")
    if unsplash_key:
        try:
            r = requests.get(
                "https://api.unsplash.com/photos/random",
                params={"query": keyword, "orientation": "landscape" if width > height else "portrait",
                        "w": width, "h": height},
                headers={"Authorization": f"Client-ID {unsplash_key}"},
                timeout=10
            )
            if r.status_code == 200:
                img_url = r.json()["urls"]["regular"]
                img_r = requests.get(img_url, timeout=15)
                if img_r.status_code == 200:
                    return img_r.content
        except Exception:
            pass

    # Fallback: use Picsum for a generic photo background
    try:
        r = requests.get(f"https://picsum.photos/{width}/{height}", timeout=10)
        if r.status_code == 200:
            return r.content
    except Exception:
        pass

    return None


def create_banner_pillow(title: str, keyword: str, output_path: str,
                          width: int, height: int, site_name: str = None) -> bool:
    """Create banner using Pillow (if installed)."""
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        import io
    except ImportError:
        return False

    site_name = site_name or SITE_NAME

    # Create base image
    img = Image.new("RGB", (width, height), hex_to_rgb(BRAND_PRIMARY))

    # Try to load background photo
    bg_bytes = fetch_background(keyword, width, height)
    if bg_bytes:
        try:
            bg = Image.open(io.BytesIO(bg_bytes)).convert("RGB")
            bg = bg.resize((width, height), Image.LANCZOS)
            # Darken background for text readability
            overlay = Image.new("RGB", (width, height), hex_to_rgb(BRAND_PRIMARY))
            img = Image.blend(bg, overlay, alpha=0.6)
        except Exception:
            pass

    draw = ImageDraw.Draw(img)

    # Load fonts (fallback to default if custom not available)
    def get_font(size: int):
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",
            "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
        ]
        for fp in font_paths:
            if os.path.exists(fp):
                try:
                    return ImageFont.truetype(fp, size)
                except Exception:
                    pass
        return ImageFont.load_default()

    title_font_size = max(40, min(80, int(width / len(title) * 2.5))) if len(title) < 30 else \
                      max(32, min(60, int(width / len(title) * 2.2)))
    title_font  = get_font(title_font_size)
    site_font   = get_font(max(20, width // 40))
    small_font  = get_font(max(16, width // 50))

    # ── Brand color bar at bottom ─────────────────────────────────────────
    bar_h = height // 8
    draw.rectangle([(0, height - bar_h), (width, height)],
                   fill=hex_to_rgb(BRAND_SECONDARY))

    # ── Site name in bar ──────────────────────────────────────────────────
    draw.text((20, height - bar_h + bar_h // 3), site_name,
              font=site_font, fill=hex_to_rgb(BRAND_TEXT))

    # ── Keyword tag ───────────────────────────────────────────────────────
    if keyword:
        tag_text = f"#{keyword.replace(' ', '')}"
        draw.text((width - 20, height - bar_h + bar_h // 3), tag_text,
                  font=small_font, fill=hex_to_rgb(BRAND_TEXT), anchor="ra")

    # ── Title text (centered, word-wrapped) ───────────────────────────────
    max_chars = max(20, width // (title_font_size // 2))
    wrapped = textwrap.fill(title, width=max_chars)
    lines = wrapped.split("\n")
    line_h = title_font_size + 10
    total_h = line_h * len(lines)
    start_y = (height - bar_h) // 2 - total_h // 2

    # Shadow for readability
    for i, line in enumerate(lines):
        y = start_y + i * line_h
        # Draw shadow
        draw.text((width // 2 + 2, y + 2), line, font=title_font,
                  fill=(0, 0, 0, 180), anchor="mm")
        # Draw text
        draw.text((width // 2, y), line, font=title_font,
                  fill=hex_to_rgb(BRAND_TEXT), anchor="mm")

    # ── Logo overlay (top-left) ───────────────────────────────────────────
    if os.path.exists(LOGO_PATH):
        try:
            logo = Image.open(LOGO_PATH).convert("RGBA")
            logo_max = min(width // 6, 150)
            logo.thumbnail((logo_max, logo_max), Image.LANCZOS)
            padding = 20
            img.paste(logo, (padding, padding), logo if logo.mode == "RGBA" else None)
        except Exception:
            # Fallback: text logo
            draw.text((20, 20), f"[ {site_name} ]", font=site_font,
                      fill=hex_to_rgb(BRAND_TEXT))
    else:
        # Text logo if no image logo
        draw.text((20, 20), f"[ {site_name} ]", font=site_font,
                  fill=hex_to_rgb(BRAND_TEXT))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path, "JPEG", quality=92, optimize=True)
    return True


def create_banner_svg(title: str, keyword: str, output_path: str,
                       width: int, height: int, site_name: str = None) -> bool:
    """Create banner as SVG (fallback when Pillow not available)."""
    site_name = site_name or SITE_NAME
    primary_rgb = BRAND_PRIMARY
    secondary_rgb = BRAND_SECONDARY

    # Word wrap for SVG
    words = title.split()
    lines, line = [], []
    for word in words:
        line.append(word)
        if len(" ".join(line)) > (width // 18):
            lines.append(" ".join(line[:-1]))
            line = [word]
    lines.append(" ".join(line))
    lines = [l for l in lines if l]

    title_y_start = height // 2 - (len(lines) * 60) // 2
    title_lines_svg = ""
    for i, l in enumerate(lines):
        title_lines_svg += f'<text x="{width//2}" y="{title_y_start + i*65}" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="{min(72, max(36, width//20))}" font-weight="bold" filter="url(#shadow)">{l}</text>\n'

    bar_y = height - height // 8
    tag = f"#{keyword.replace(' ', '')}" if keyword else ""

    svg = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
  <defs>
    <linearGradient id="bg" x1="0%" y1="0%" x2="100%" y2="100%">
      <stop offset="0%" style="stop-color:{primary_rgb};stop-opacity:1" />
      <stop offset="100%" style="stop-color:{secondary_rgb};stop-opacity:0.7" />
    </linearGradient>
    <filter id="shadow">
      <feDropShadow dx="2" dy="2" stdDeviation="3" flood-color="black" flood-opacity="0.5"/>
    </filter>
  </defs>
  <!-- Background -->
  <rect width="{width}" height="{height}" fill="url(#bg)"/>
  <!-- Grid pattern overlay -->
  <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
    <path d="M 40 0 L 0 0 0 40" fill="none" stroke="white" stroke-width="0.3" opacity="0.1"/>
  </pattern>
  <rect width="{width}" height="{height}" fill="url(#grid)"/>
  <!-- Bottom brand bar -->
  <rect x="0" y="{bar_y}" width="{width}" height="{height - bar_y}" fill="{secondary_rgb}"/>
  <!-- Site name -->
  <text x="24" y="{bar_y + (height-bar_y)//2 + 8}" fill="white" font-family="Arial, sans-serif" font-size="{max(20, width//50)}" font-weight="bold">{site_name}</text>
  <!-- Keyword tag -->
  <text x="{width - 24}" y="{bar_y + (height-bar_y)//2 + 8}" fill="white" font-family="Arial, sans-serif" font-size="{max(16, width//60)}" text-anchor="end" opacity="0.85">{tag}</text>
  <!-- Decorative accent line -->
  <rect x="0" y="{bar_y}" width="{width}" height="4" fill="white" opacity="0.3"/>
  <!-- Title -->
  {title_lines_svg}
  <!-- Corner logo placeholder -->
  <rect x="20" y="20" width="120" height="40" rx="6" fill="white" opacity="0.15"/>
  <text x="80" y="47" text-anchor="middle" fill="white" font-family="Arial, sans-serif" font-size="18" font-weight="bold">{site_name[:10]}</text>
</svg>"""

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(svg)
    return True


def generate_banner(title: str, keyword: str = "", image_type: str = "blog",
                     site_name: str = None, output_dir: str = None) -> dict:
    """Generate a banner image for the given title and type."""
    output_dir = output_dir or OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)

    slug = re.sub(r"[^a-z0-9]+", "-", title.lower())[:40].strip("-")
    date_str = datetime.now().strftime("%Y%m%d")

    if image_type == "all":
        results = {}
        for t in SIZES:
            r = generate_banner(title, keyword, t, site_name, output_dir)
            results[t] = r
        return results

    width, height = SIZES.get(image_type, SIZES["blog"])

    # Try Pillow first, fall back to SVG
    out_jpg = os.path.join(output_dir, f"{slug}-{image_type}-{date_str}.jpg")
    out_svg = os.path.join(output_dir, f"{slug}-{image_type}-{date_str}.svg")

    success = create_banner_pillow(title, keyword, out_jpg, width, height, site_name)
    if success:
        output_path = out_jpg
        fmt = "JPEG"
    else:
        create_banner_svg(title, keyword, out_svg, width, height, site_name)
        output_path = out_svg
        fmt = "SVG"

    print(f"✅ {image_type.upper()} banner ({width}x{height}): {os.path.relpath(output_path, BASE_DIR)}")
    return {
        "path": output_path,
        "format": fmt,
        "width": width,
        "height": height,
        "type": image_type,
        "title": title,
    }


def generate_all_social_banners(title: str, keyword: str = "",
                                  site_name: str = None) -> dict:
    """Generate all banner sizes at once for a post."""
    results = {}
    social_types = ["blog", "instagram", "facebook", "linkedin", "twitter", "gmb", "instagram_story"]

    print(f"\n🎨 Generating banners for: '{title[:50]}'")
    for t in social_types:
        r = generate_banner(title, keyword, t, site_name)
        results[t] = r

    print(f"\n✅ Generated {len(results)} banner images")
    return results


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — Banner Generator")
    parser.add_argument("--title",    required=True, help="Blog/post title")
    parser.add_argument("--keyword",  default="",    help="Primary keyword (for tag)")
    parser.add_argument("--type",     default="blog", help=f"Image type: {list(SIZES.keys())} or 'all'")
    parser.add_argument("--site",     default="",    help="Site name override")
    args = parser.parse_args()

    if args.type == "social":
        generate_all_social_banners(args.title, args.keyword, args.site or None)
    else:
        generate_banner(args.title, args.keyword, args.type, args.site or None)

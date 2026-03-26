"""
Claude Auto SEO — WordPress Publisher Module
Publishes articles to WordPress via REST API with Yoast SEO metadata.
"""

import os
import re
import json
import base64
import requests
from datetime import datetime
from typing import Dict, Optional
from dotenv import load_dotenv

load_dotenv()


class WordPressPublisher:
    def __init__(self):
        self.wp_url = os.getenv('WP_URL', '').rstrip('/')
        self.username = os.getenv('WP_USERNAME', '')
        self.app_password = os.getenv('WP_APP_PASSWORD', '')
        self.api_base = f"{self.wp_url}/wp-json/wp/v2"

        if not all([self.wp_url, self.username, self.app_password]):
            raise ValueError(
                "Missing WordPress credentials. Set WP_URL, WP_USERNAME, "
                "WP_APP_PASSWORD in your .env file."
            )

        # Build auth header
        credentials = f"{self.username}:{self.app_password}"
        self.auth_header = base64.b64encode(credentials.encode()).decode()
        self.headers = {
            'Authorization': f'Basic {self.auth_header}',
            'Content-Type': 'application/json',
        }

    def test_connection(self) -> bool:
        """Test WordPress API connection."""
        try:
            resp = requests.get(f"{self.api_base}/posts", headers=self.headers, timeout=10)
            return resp.status_code == 200
        except Exception:
            return False

    def parse_markdown(self, md_path: str) -> Dict:
        """Parse markdown file and extract article data."""
        with open(md_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract front matter if present (YAML-style between ---)
        front_matter = {}
        fm_match = re.match(r'^---\n(.*?)\n---\n', content, re.DOTALL)
        if fm_match:
            fm_text = fm_match.group(1)
            for line in fm_text.split('\n'):
                if ':' in line:
                    key, val = line.split(':', 1)
                    front_matter[key.strip()] = val.strip()
            content = content[fm_match.end():]

        # Extract H1 as title
        h1_match = re.search(r'^# (.+)$', content, re.MULTILINE)
        title = front_matter.get('title', h1_match.group(1) if h1_match else 'Untitled')

        # Convert markdown to HTML (basic)
        html_content = self._markdown_to_html(content)

        return {
            'title': title,
            'content': html_content,
            'seo_title': front_matter.get('seo_title', title),
            'seo_description': front_matter.get('meta_description', ''),
            'focus_keyword': front_matter.get('focus_keyword', ''),
            'categories': front_matter.get('categories', '').split(',') if front_matter.get('categories') else [],
            'tags': front_matter.get('tags', '').split(',') if front_matter.get('tags') else [],
            'status': front_matter.get('status', 'draft'),
            'featured_image_url': front_matter.get('featured_image', ''),
            'canonical': front_matter.get('canonical', ''),
        }

    def _markdown_to_html(self, md: str) -> str:
        """Convert markdown to HTML."""
        html = md
        # Headers
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        # Bold/italic
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)', r'<a href="\2">\1</a>', html)
        # Lists
        html = re.sub(r'(?m)^- (.+)$', r'<li>\1</li>', html)
        html = re.sub(r'(<li>.*?</li>\n?)+', r'<ul>\g<0></ul>', html, flags=re.DOTALL)
        # Paragraphs
        lines = html.split('\n\n')
        result = []
        for block in lines:
            block = block.strip()
            if block and not block.startswith('<'):
                block = f'<p>{block}</p>'
            result.append(block)
        return '\n\n'.join(result)

    def get_or_create_category(self, name: str) -> Optional[int]:
        """Get category ID by name, or create it."""
        name = name.strip()
        if not name:
            return None

        # Search for existing
        resp = requests.get(
            f"{self.api_base}/categories",
            headers=self.headers,
            params={'search': name}
        )
        categories = resp.json()
        for cat in categories:
            if cat['name'].lower() == name.lower():
                return cat['id']

        # Create new
        resp = requests.post(
            f"{self.api_base}/categories",
            headers=self.headers,
            json={'name': name}
        )
        if resp.status_code == 201:
            return resp.json()['id']
        return None

    def get_or_create_tag(self, name: str) -> Optional[int]:
        """Get tag ID by name, or create it."""
        name = name.strip()
        if not name:
            return None

        resp = requests.get(
            f"{self.api_base}/tags",
            headers=self.headers,
            params={'search': name}
        )
        tags = resp.json()
        for tag in tags:
            if tag['name'].lower() == name.lower():
                return tag['id']

        resp = requests.post(
            f"{self.api_base}/tags",
            headers=self.headers,
            json={'name': name}
        )
        if resp.status_code == 201:
            return resp.json()['id']
        return None

    def publish(self, md_path: str) -> Dict:
        """Publish a markdown article to WordPress."""
        print(f"📤 Publishing: {md_path}")

        if not self.test_connection():
            return {'success': False, 'error': 'Cannot connect to WordPress. Check credentials in .env'}

        article = self.parse_markdown(md_path)

        # Resolve categories and tags
        category_ids = [self.get_or_create_category(c) for c in article['categories'] if c]
        category_ids = [c for c in category_ids if c]

        tag_ids = [self.get_or_create_tag(t) for t in article['tags'] if t]
        tag_ids = [t for t in tag_ids if t]

        # Build post payload
        payload = {
            'title': article['title'],
            'content': article['content'],
            'status': article['status'],
            'categories': category_ids,
            'tags': tag_ids,
            # Yoast fields (registered via MU plugin)
            'yoast_wpseo_title': article['seo_title'],
            'yoast_wpseo_metadesc': article['seo_description'],
            'yoast_wpseo_focuskw': article['focus_keyword'],
        }

        if article.get('canonical'):
            payload['yoast_wpseo_canonical'] = article['canonical']

        if article.get('featured_image_url'):
            payload['featured_image_url'] = article['featured_image_url']

        # Create the post
        resp = requests.post(
            f"{self.api_base}/posts",
            headers=self.headers,
            json=payload
        )

        if resp.status_code == 201:
            post_data = resp.json()
            edit_url = f"{self.wp_url}/wp-admin/post.php?post={post_data['id']}&action=edit"
            print(f"✅ Published successfully (ID: {post_data['id']})")
            print(f"   Edit URL: {edit_url}")
            print(f"   Status: {article['status']}")
            return {
                'success': True,
                'post_id': post_data['id'],
                'post_url': post_data.get('link', ''),
                'edit_url': edit_url,
                'status': article['status'],
                'title': article['title'],
            }
        else:
            error = resp.json()
            print(f"❌ Failed to publish: {error.get('message', 'Unknown error')}")
            return {
                'success': False,
                'error': error.get('message', 'Unknown error'),
                'status_code': resp.status_code,
            }


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python3 wordpress_publisher.py drafts/my-article.md")
        sys.exit(1)

    publisher = WordPressPublisher()
    result = publisher.publish(sys.argv[1])
    print(json.dumps(result, indent=2))

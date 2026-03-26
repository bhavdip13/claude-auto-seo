"""
Claude Auto SEO — DataForSEO Client Module
Interfaces with DataForSEO API for live SEO data.
"""

import os
import json
import hashlib
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import requests
from dotenv import load_dotenv

load_dotenv()

CACHE_DIR = os.path.join(os.path.dirname(__file__), '../../data/dataforseo-cache')
CACHE_TTL_HOURS = 24


def _cache_key(endpoint: str, params: dict) -> str:
    content = f"{endpoint}:{json.dumps(params, sort_keys=True)}"
    return hashlib.md5(content.encode()).hexdigest()


def _load_cache(key: str) -> Optional[dict]:
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    if os.path.exists(path):
        with open(path) as f:
            cached = json.load(f)
        if datetime.fromisoformat(cached['expires']) > datetime.now():
            return cached['data']
    return None


def _save_cache(key: str, data: dict):
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = os.path.join(CACHE_DIR, f"{key}.json")
    with open(path, 'w') as f:
        json.dump({
            'data': data,
            'expires': (datetime.now() + timedelta(hours=CACHE_TTL_HOURS)).isoformat()
        }, f)


class DataForSEOClient:
    BASE_URL = "https://api.dataforseo.com/v3"

    def __init__(self):
        self.login = os.getenv('DATAFORSEO_LOGIN')
        self.password = os.getenv('DATAFORSEO_PASSWORD')
        if not self.login or not self.password:
            raise ValueError("Set DATAFORSEO_LOGIN and DATAFORSEO_PASSWORD in .env")
        self.auth = (self.login, self.password)

    def _post(self, endpoint: str, payload: list, use_cache: bool = True) -> dict:
        cache_key = _cache_key(endpoint, payload)
        if use_cache:
            cached = _load_cache(cache_key)
            if cached:
                return cached

        resp = requests.post(
            f"{self.BASE_URL}/{endpoint}",
            auth=self.auth,
            json=payload,
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()

        if use_cache:
            _save_cache(cache_key, data)

        return data

    def serp(self, keyword: str, location: str = "United States",
             language: str = "English", device: str = "desktop") -> Dict:
        """Get live SERP results for a keyword."""
        payload = [{
            "keyword": keyword,
            "location_name": location,
            "language_name": language,
            "device": device,
            "depth": 10,
        }]
        data = self._post("serp/google/organic/live/regular", payload)
        return self._parse_serp(data, keyword)

    def _parse_serp(self, raw: dict, keyword: str) -> Dict:
        results = []
        try:
            items = raw['tasks'][0]['result'][0]['items']
            for item in items:
                if item.get('type') == 'organic':
                    results.append({
                        'position': item.get('rank_absolute'),
                        'title': item.get('title'),
                        'url': item.get('url'),
                        'description': item.get('description'),
                        'domain': item.get('domain'),
                    })
        except (KeyError, IndexError, TypeError):
            pass

        return {
            'keyword': keyword,
            'results': results,
            'total_results': len(results),
            'fetched_at': datetime.now().isoformat()
        }

    def keyword_data(self, keywords: List[str], location: str = "United States") -> List[Dict]:
        """Get search volume and difficulty for keywords."""
        payload = [{
            "keywords": keywords,
            "location_name": location,
            "language_name": "English",
        }]
        data = self._post("keywords_data/google_ads/search_volume/live", payload)
        results = []
        try:
            for item in data['tasks'][0]['result']:
                results.append({
                    'keyword': item.get('keyword'),
                    'search_volume': item.get('search_volume', 0),
                    'competition': item.get('competition'),
                    'cpc': item.get('cpc'),
                    'monthly_searches': item.get('monthly_searches', []),
                })
        except (KeyError, IndexError, TypeError):
            pass
        return results

    def backlinks(self, domain: str, limit: int = 100) -> Dict:
        """Get backlink data for a domain."""
        payload = [{
            "target": domain,
            "limit": limit,
            "order_by": ["domain_from_rank,desc"],
        }]
        data = self._post("backlinks/backlinks/live", payload)
        results = []
        try:
            items = data['tasks'][0]['result'][0]['items']
            for item in items:
                results.append({
                    'domain_from': item.get('domain_from'),
                    'url_from': item.get('url_from'),
                    'url_to': item.get('url_to'),
                    'anchor': item.get('anchor'),
                    'domain_from_rank': item.get('domain_from_rank'),
                    'is_dofollow': item.get('dofollow'),
                })
        except (KeyError, IndexError, TypeError):
            pass

        summary = {}
        try:
            summary = {
                'total_backlinks': data['tasks'][0]['result'][0].get('total_count', 0),
                'referring_domains': data['tasks'][0]['result'][0].get('referring_domains', 0),
            }
        except (KeyError, IndexError, TypeError):
            pass

        return {'domain': domain, 'summary': summary, 'backlinks': results}

    def on_page_audit(self, url: str) -> Dict:
        """Run on-page SEO audit via DataForSEO."""
        payload = [{
            "url": url,
            "enable_javascript": True,
            "load_resources": True,
        }]
        data = self._post("on_page/instant_pages", payload)
        try:
            page_data = data['tasks'][0]['result'][0]['items'][0]
            return {
                'url': url,
                'title': page_data.get('meta', {}).get('title'),
                'description': page_data.get('meta', {}).get('description'),
                'h1': page_data.get('meta', {}).get('htags', {}).get('h1', []),
                'word_count': page_data.get('meta', {}).get('content', {}).get('plain_text_word_count'),
                'page_timing': page_data.get('page_timing'),
                'checks': page_data.get('checks', {}),
                'duplicate_title': page_data.get('duplicate_title'),
                'duplicate_description': page_data.get('duplicate_description'),
            }
        except (KeyError, IndexError, TypeError):
            return {'url': url, 'error': 'Could not parse response'}


if __name__ == "__main__":
    client = DataForSEOClient()
    results = client.serp("seo tools for small business")
    print(f"Top results for '{results['keyword']}':")
    for r in results['results'][:5]:
        print(f"  #{r['position']}: {r['title']} — {r['domain']}")

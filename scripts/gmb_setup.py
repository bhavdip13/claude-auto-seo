"""
Claude Auto SEO — GMB Setup & Auth Helper
Handles Google My Business OAuth flow and location discovery.

Usage:
  python3 scripts/gmb_setup.py --auth              # Run OAuth flow
  python3 scripts/gmb_setup.py --list-locations    # List your GMB locations
  python3 scripts/gmb_setup.py --refresh-token     # Refresh access token
  python3 scripts/gmb_setup.py --test-post         # Send a test GMB post
"""

import os
import sys
import json
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

BASE_DIR      = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOKEN_FILE    = os.path.join(BASE_DIR, "config", "gmb-tokens.json")
CLIENT_FILE   = os.path.join(BASE_DIR, "config", "google-oauth-client.json")
REDIRECT_URI  = "http://localhost:8080/oauth2callback"
SCOPES = [
    "https://www.googleapis.com/auth/business.manage",
]


def load_tokens() -> dict:
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE) as f:
            return json.load(f)
    return {}


def save_tokens(tokens: dict):
    os.makedirs(os.path.dirname(TOKEN_FILE), exist_ok=True)
    with open(TOKEN_FILE, "w") as f:
        json.dump(tokens, f, indent=2)
    print(f"✅ Tokens saved to {TOKEN_FILE}")


def run_oauth_flow() -> str:
    """Run OAuth 2.0 flow to get access token."""
    if not os.path.exists(CLIENT_FILE):
        print(f"❌ OAuth client file not found: {CLIENT_FILE}")
        print("   Download from Google Cloud Console → APIs & Services → Credentials")
        print("   Save as: config/google-oauth-client.json")
        sys.exit(1)

    try:
        from google_auth_oauthlib.flow import Flow
    except ImportError:
        print("Install: pip install google-auth-oauthlib")
        sys.exit(1)

    flow = Flow.from_client_secrets_file(
        CLIENT_FILE,
        scopes=SCOPES,
        redirect_uri=REDIRECT_URI
    )

    auth_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent"
    )

    print(f"\n🌐 Opening browser for Google OAuth...")
    print(f"   If browser doesn't open, visit:\n   {auth_url}\n")
    webbrowser.open(auth_url)

    # Local server to capture callback
    auth_code = [None]

    class CallbackHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            params = parse_qs(urlparse(self.path).query)
            if "code" in params:
                auth_code[0] = params["code"][0]
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"<h1>Authentication successful! You can close this window.</h1>")
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"<h1>Authentication failed.</h1>")

        def log_message(self, *args):
            pass  # Suppress request logs

    print("Waiting for OAuth callback on http://localhost:8080 ...")
    server = HTTPServer(("localhost", 8080), CallbackHandler)
    server.handle_request()

    if not auth_code[0]:
        print("❌ No auth code received")
        sys.exit(1)

    flow.fetch_token(code=auth_code[0])
    credentials = flow.credentials

    tokens = {
        "access_token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
    }
    save_tokens(tokens)

    print(f"\n✅ Authentication successful!")
    print(f"   Add to .env:\n   GOOGLE_GMB_ACCESS_TOKEN={tokens['access_token']}")
    return tokens["access_token"]


def refresh_token() -> str:
    """Refresh the GMB access token using the stored refresh token."""
    tokens = load_tokens()
    if not tokens.get("refresh_token"):
        print("No refresh token found. Run --auth first.")
        return ""

    import requests
    r = requests.post(
        "https://oauth2.googleapis.com/token",
        data={
            "client_id": tokens["client_id"],
            "client_secret": tokens["client_secret"],
            "refresh_token": tokens["refresh_token"],
            "grant_type": "refresh_token",
        }
    )

    if r.status_code == 200:
        new_access = r.json()["access_token"]
        tokens["access_token"] = new_access
        save_tokens(tokens)
        print(f"✅ Token refreshed!")
        print(f"   Update .env:\n   GOOGLE_GMB_ACCESS_TOKEN={new_access}")
        return new_access
    else:
        print(f"❌ Token refresh failed: {r.text}")
        return ""


def list_locations(access_token: str = None) -> list:
    """List all GMB locations for the authenticated account."""
    import requests

    token = access_token or load_tokens().get("access_token") or \
            os.environ.get("GOOGLE_GMB_ACCESS_TOKEN")

    if not token:
        print("No access token. Run --auth first.")
        return []

    headers = {"Authorization": f"Bearer {token}"}

    # Get accounts
    acc_r = requests.get(
        "https://mybusinessaccountmanagement.googleapis.com/v1/accounts",
        headers=headers
    )

    if acc_r.status_code != 200:
        print(f"❌ Failed to get accounts: {acc_r.text[:200]}")
        print("   Note: GMB API requires approval. Apply at:")
        print("   https://developers.google.com/my-business/content/prereqs")
        return []

    accounts = acc_r.json().get("accounts", [])
    all_locations = []

    for account in accounts:
        acc_name = account["name"]
        loc_r = requests.get(
            f"https://mybusinessbusinessinformation.googleapis.com/v1/{acc_name}/locations",
            headers=headers,
            params={"readMask": "name,title,storefrontAddress,websiteUri"}
        )

        if loc_r.status_code == 200:
            for loc in loc_r.json().get("locations", []):
                location_id = loc["name"].split("/")[-1]
                all_locations.append({
                    "name": loc.get("title", "Unknown"),
                    "location_id": loc["name"],
                    "address": loc.get("storefrontAddress", {}).get("addressLines", [""])[0],
                    "website": loc.get("websiteUri", ""),
                })

    if all_locations:
        print("\n✅ Your GMB Locations:")
        print("="*60)
        for loc in all_locations:
            print(f"\n📍 {loc['name']}")
            print(f"   Address: {loc['address']}")
            print(f"   Location ID: {loc['location_id']}")
            print(f"   ➤ Add to .env: GMB_LOCATION_ID={loc['location_id']}")
    else:
        print("No locations found.")

    return all_locations


def test_post(access_token: str = None):
    """Send a test post to GMB."""
    import requests

    token = access_token or load_tokens().get("access_token") or \
            os.environ.get("GOOGLE_GMB_ACCESS_TOKEN")
    location_id = os.environ.get("GMB_LOCATION_ID")

    if not token or not location_id:
        print("Set GOOGLE_GMB_ACCESS_TOKEN and GMB_LOCATION_ID in .env first")
        return

    payload = {
        "languageCode": "en",
        "summary": "🎉 Test post from Claude Auto SEO! Our automated SEO and digital marketing system is working correctly.",
        "callToAction": {
            "actionType": "LEARN_MORE",
            "url": os.environ.get("WP_URL", "https://yoursite.com")
        },
        "topicType": "STANDARD"
    }

    r = requests.post(
        f"https://mybusiness.googleapis.com/v4/accounts/-/locations/{location_id}/localPosts",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json=payload
    )

    if r.status_code == 200:
        print(f"✅ Test post created successfully!")
        print(f"   Post name: {r.json().get('name')}")
    else:
        print(f"❌ Test post failed: {r.text[:300]}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Claude Auto SEO — GMB Setup")
    parser.add_argument("--auth",             action="store_true", help="Run OAuth flow")
    parser.add_argument("--list-locations",   action="store_true", help="List GMB locations")
    parser.add_argument("--refresh-token",    action="store_true", help="Refresh access token")
    parser.add_argument("--test-post",        action="store_true", help="Send a test GMB post")
    args = parser.parse_args()

    if args.auth:
        run_oauth_flow()
    elif args.list_locations:
        list_locations()
    elif args.refresh_token:
        refresh_token()
    elif args.test_post:
        test_post()
    else:
        parser.print_help()

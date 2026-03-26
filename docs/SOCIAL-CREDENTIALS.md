# Social Media Credentials Setup

Step-by-step guide to get API credentials for every platform.

---

## Facebook + Instagram (Meta)

**One set of credentials covers both platforms.**

### Step 1: Create Meta Developer App
1. Go to [developers.facebook.com](https://developers.facebook.com)
2. Click "My Apps" → "Create App"
3. Choose "Business" type
4. Name: "Claude Auto SEO"

### Step 2: Add Products
In your app dashboard, add:
- **Facebook Login** (for OAuth)
- **Instagram Graph API** (for Instagram posting)

### Step 3: Get Page Access Token
1. Go to [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
2. Select your app
3. Click "Generate Access Token"
4. Select your Facebook Page
5. Grant permissions: `pages_manage_posts`, `pages_read_engagement`, `instagram_basic`, `instagram_content_publish`
6. Copy the **Page Access Token**

### Step 4: Get Instagram User ID
```bash
curl "https://graph.facebook.com/v19.0/me/accounts?access_token=YOUR_PAGE_TOKEN"
# Find instagram_business_account.id in the response
```

### Add to .env:
```
META_ACCESS_TOKEN=your_page_access_token
FACEBOOK_PAGE_ID=your_page_id
INSTAGRAM_USER_ID=your_instagram_business_id
```

---

## Twitter / X

### Step 1: Apply for Developer Access
1. Go to [developer.twitter.com](https://developer.twitter.com)
2. Apply for a developer account (usually approved instantly)
3. Create a new Project and App

### Step 2: Configure App Permissions
- Set to "Read and Write" permissions
- Enable OAuth 1.0a

### Step 3: Get Your Keys
From your app dashboard:
- API Key and Secret
- Generate Access Token and Secret (for your account)
- Bearer Token

### Add to .env:
```
TWITTER_API_KEY=xxx
TWITTER_API_SECRET=xxx
TWITTER_ACCESS_TOKEN=xxx
TWITTER_ACCESS_SECRET=xxx
TWITTER_BEARER_TOKEN=xxx
```

### Install tweepy:
```bash
pip install tweepy
```

---

## LinkedIn

### Step 1: Create LinkedIn App
1. Go to [linkedin.com/developers](https://www.linkedin.com/developers/)
2. Create a new app — select your LinkedIn Company Page
3. Request access to: `w_member_social`, `r_basicprofile`

### Step 2: Get Access Token
LinkedIn uses OAuth 2.0. Use the OAuth flow or:
```bash
python3 scripts/linkedin_auth.py  # Runs OAuth flow and saves token
```

### Add to .env:
```
LINKEDIN_ACCESS_TOKEN=your_token
LINKEDIN_CLIENT_ID=your_client_id
LINKEDIN_CLIENT_SECRET=your_client_secret
```

**Note:** LinkedIn access tokens expire after 60 days. Run `python3 scripts/linkedin_auth.py --refresh` to renew.

---

## Pinterest

### Step 1: Create Pinterest App
1. Go to [developers.pinterest.com](https://developers.pinterest.com)
2. Create a new app
3. Get approved for the "Ads" or "Organic" product

### Step 2: Get Board ID
1. Go to your Pinterest board
2. The Board ID is the number in the URL: `pinterest.com/username/board-name/**123456789**/`

### Step 3: OAuth
```bash
python3 scripts/pinterest_auth.py
```

### Add to .env:
```
PINTEREST_ACCESS_TOKEN=your_token
PINTEREST_BOARD_ID=your_board_id
```

---

## TikTok

### Step 1: Apply for Content Posting API
1. Go to [developers.tiktok.com](https://developers.tiktok.com)
2. Create a developer account
3. Apply for the **Content Posting API** product
4. Note: TikTok primarily supports video. Text posts require Creator Portal access.

### Add to .env:
```
TIKTOK_ACCESS_TOKEN=your_token
```

---

## Unsplash (for banner background images)

Free account, no cost for the API.

1. Go to [unsplash.com/developers](https://unsplash.com/developers)
2. Create an app
3. Copy the **Access Key**

### Add to .env:
```
UNSPLASH_ACCESS_KEY=your_access_key
```

Without this key, banner images use random photos from Picsum (still works, but not keyword-relevant).

---

## Medium (External Blog)

1. Go to [medium.com/me/settings](https://medium.com/me/settings)
2. Scroll to "Integration tokens"
3. Generate a new token

### Add to .env:
```
MEDIUM_INTEGRATION_TOKEN=your_token
```

---

## Reddit (External Blog)

1. Go to [reddit.com/prefs/apps](https://reddit.com/prefs/apps)
2. Click "Create another app..."
3. Type: "script"
4. Name: "Claude Auto SEO"
5. Redirect URI: `http://localhost:8080`

### Add to .env:
```
REDDIT_CLIENT_ID=your_app_client_id
REDDIT_CLIENT_SECRET=your_app_secret
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password
```

---

## Quick Verification

After setting credentials, verify each platform:
```bash
python3 scripts/social_publisher.py --topic "Test post" --keyword "test" --platforms facebook --dry-run
```

Or in Claude Code:
```
/dm post "test post" --platforms facebook --dry-run
```

# Installation Guide

## Requirements

| Requirement | Version | Required? |
|---|---|---|
| Claude Code CLI | Latest | ✅ Required |
| Python | 3.8+ | ✅ Required |
| pip | Latest | ✅ Required |
| Node.js | 18+ | Optional (some scripts) |
| WordPress | 5.9+ | Optional (for publishing) |
| Yoast SEO Plugin | Any | Optional (for Yoast metadata) |

---

## Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/claude-auto-seo.git
cd claude-auto-seo
```

---

## Step 2: Run the Installer

### macOS / Linux
```bash
chmod +x install.sh
./install.sh
```

### Windows (PowerShell)
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\install.ps1
```

The installer will:
- Verify Claude Code and Python are installed
- Copy skills to `~/.claude/skills/`
- Copy agents to `~/.claude/agents/`
- Copy commands to `~/.claude/commands/`
- Install Python dependencies

---

## Step 3: Install Python Dependencies

```bash
pip install -r requirements.txt
```

For NLP features, also download NLTK data:
```bash
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

---

## Step 4: Configure Your Site

### 4a. Edit config/site.json
```json
{
  "site": {
    "url": "https://yoursite.com",
    "name": "Your Site Name",
    "type": "blog"
  }
}
```

### 4b. Fill in context/ files
These files tell Claude about your brand. The more detail, the better the output:

- `context/brand-voice.md` — Your tone and writing style
- `context/seo-guidelines.md` — Already filled with best practices (customize as needed)
- `context/target-keywords.md` — Your keyword research
- `context/internal-links-map.md` — Your key pages for internal linking
- `context/competitor-analysis.md` — Your competitors

### 4c. Set up .env (for integrations)
```bash
cp .env.example .env
# Edit .env with your credentials
```

---

## Step 5: WordPress Setup (Optional)

If you want auto-publishing to WordPress:

1. Install the MU plugin:
   ```
   Copy wordpress/claude-auto-seo-yoast-rest.php
   to: wp-content/mu-plugins/
   ```

2. Create a WordPress Application Password:
   - Go to WordPress Admin → Users → Your Profile
   - Scroll to "Application Passwords"
   - Enter name "Claude Auto SEO" → Click "Add New Application Password"
   - Copy the generated password

3. Add to `.env`:
   ```
   WP_URL=https://yoursite.com
   WP_USERNAME=your_username
   WP_APP_PASSWORD=xxxx xxxx xxxx xxxx xxxx xxxx
   ```

---

## Step 6: Verify Installation

```bash
claude
```

Then in Claude Code:
```
/seo audit https://example.com
```

If you see an audit running, you're set up correctly! ✅

---

## Troubleshooting

### "Command not found: claude"
Install Claude Code from: https://claude.ai/claude-code

### "No module named X"
```bash
pip install -r requirements.txt --upgrade
```

### "WordPress publishing fails"
- Verify credentials in `.env`
- Ensure Application Password (not login password) is used
- Check MU plugin is installed at `wp-content/mu-plugins/`

### "Skills not loading"
Check installation path:
```bash
ls ~/.claude/skills/seo/
ls ~/.claude/commands/
ls ~/.claude/agents/
```

If empty, re-run `./install.sh`

---

## Uninstall

```bash
./uninstall.sh
```

This removes the installed skills, agents, and commands from `~/.claude/` but does NOT delete your content, reports, or config files.

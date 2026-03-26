# Troubleshooting

## Common Issues

### Skills not running
**Symptom:** `/seo audit` does nothing or gives an error
**Fix:**
```bash
ls ~/.claude/skills/seo/SKILL.md   # Should exist
ls ~/.claude/commands/seo-audit.md # Should exist
```
If missing, re-run `./install.sh`

---

### Content doesn't match brand voice
**Fix:** Update `context/brand-voice.md` with:
- More specific tone descriptions
- Real before/after examples from your content
- Specific words or phrases to use/avoid

---

### Articles are too similar to competitors
**Fix:**
- Add differentiation angles to `context/competitor-analysis.md`
- Update `context/brand-voice.md` with your unique perspective
- Use `/content research <topic>` first to find gaps

---

### WordPress publishing fails with 401
**Fix:** You're using login password instead of Application Password.
- Go to WordPress Admin → Users → Profile → Application Passwords
- Create one specifically for Claude Auto SEO
- Use this (not your login password) in `.env`

---

### PDF report is blank or fails
**Fix:** Install PDF libraries:
```bash
pip install weasyprint
# or
pip install pdfkit
# and install wkhtmltopdf: https://wkhtmltopdf.org/downloads.html
```

---

### DataForSEO returns empty results
**Fix:**
- Verify credentials in `.env`
- Check your DataForSEO account has credits
- Check cache: delete `data/dataforseo-cache/` to force fresh fetch

---

### Python module not found
**Fix:**
```bash
pip install -r requirements.txt --upgrade --break-system-packages
```

---

## Getting Help

1. Check this troubleshooting guide
2. Read `docs/INSTALLATION.md`
3. Open an issue on GitHub with:
   - Your OS and Python version
   - The command you ran
   - The full error message

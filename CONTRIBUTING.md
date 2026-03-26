# Contributing to Claude Auto SEO

We welcome contributions! Here's how to help.

## Ways to Contribute

- 🐛 **Bug reports** — Open an issue with steps to reproduce
- ✨ **New commands** — Add new `.md` command files to `.claude/commands/`
- 🤖 **New agents** — Add specialized agents to `agents/`
- 🐍 **Python modules** — Improve analysis modules in `data_sources/modules/`
- 📖 **Documentation** — Improve guides in `docs/`
- 🌍 **Translations** — Help translate context templates

## Development Setup

```bash
git clone https://github.com/YOUR_USERNAME/claude-auto-seo.git
cd claude-auto-seo
pip install -r requirements.txt
./install.sh
```

## Pull Request Guidelines

1. Fork the repo and create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Test thoroughly
4. Write clear commit messages
5. Open a PR with a description of what it does and why

## Command File Format

New commands in `.claude/commands/` should follow this structure:

```markdown
# /command-name — Short Description

You are the [Agent Name] for Claude Auto SEO. When invoked with `/command-name <args>`, [what it does].

## Process
[Steps]

## Output Format
[What it produces]

## Save Output
[Where files are saved]
```

## Code Style

- Python: Follow PEP 8, add docstrings to all functions
- Markdown: Use consistent heading levels, include examples
- JSON: Indent with 2 spaces, add `_comment` fields for clarity

---

# License

MIT License

Copyright (c) 2026 Claude Auto SEO

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

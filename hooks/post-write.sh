#!/usr/bin/env bash
# Claude Auto SEO — Post-Write Hook
# Automatically triggered after /content write completes a draft
# Runs: content-analyzer, seo-optimizer, meta-creator, internal-linker, keyword-mapper

# Usage: This hook is called by Claude Code after content write commands
# It signals Claude to auto-run all post-write agents

DRAFT_FILE="$1"
TIMESTAMP=$(date +%Y-%m-%d)

if [ -z "$DRAFT_FILE" ]; then
  echo "No draft file specified"
  exit 0
fi

echo "🤖 Claude Auto SEO — Running post-write agents on: $DRAFT_FILE"
echo ""
echo "Agents queued:"
echo "  1. Content Analyzer    — Readability, intent, quality score"
echo "  2. SEO Optimizer       — On-page SEO recommendations"
echo "  3. Meta Creator        — Title + description options"
echo "  4. Internal Linker     — Internal link suggestions"
echo "  5. Keyword Mapper      — Keyword distribution map"
echo ""
echo "All agent reports will be saved to: drafts/reports-$(basename $DRAFT_FILE .md)-$TIMESTAMP.md"

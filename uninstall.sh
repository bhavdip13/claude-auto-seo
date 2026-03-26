#!/usr/bin/env bash
# Claude Auto SEO — Uninstall Script

set -e
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; NC='\033[0m'

echo "Uninstalling Claude Auto SEO..."

SKILL_DIR="${HOME}/.claude/skills"
AGENTS_DIR="${HOME}/.claude/agents"
COMMANDS_DIR="${HOME}/.claude/commands"

# Remove skills
for skill in seo seo-content seo-technical seo-schema seo-geo seo-report; do
  if [ -d "$SKILL_DIR/$skill" ]; then
    rm -rf "$SKILL_DIR/$skill"
    echo -e "  ${GREEN}✓${NC} Removed skill: $skill"
  fi
done

# Remove agents
for agent in seo-auditor content-analyzer meta-linker-keyword-agents schema-geo-editor-rank-agents report-performance-agents; do
  if [ -f "$AGENTS_DIR/$agent.md" ]; then
    rm "$AGENTS_DIR/$agent.md"
    echo -e "  ${GREEN}✓${NC} Removed agent: $agent"
  fi
done

# Remove commands
commands=(seo-audit seo-fix seo-report seo-geo seo-rank-track seo-weekly-digest
  seo-schema seo-sitemap seo-hreflang seo-core-vitals seo-competitor-report
  seo-priorities content-write content-research content-rewrite content-optimize
  content-analyze content-calendar content-bulk-write publish-wordpress)

for cmd in "${commands[@]}"; do
  if [ -f "$COMMANDS_DIR/$cmd.md" ]; then
    rm "$COMMANDS_DIR/$cmd.md"
    echo -e "  ${GREEN}✓${NC} Removed command: $cmd"
  fi
done

echo -e "\n${GREEN}✅ Claude Auto SEO uninstalled.${NC}"
echo -e "${YELLOW}Note: Your content, reports, and config files were NOT deleted.${NC}"

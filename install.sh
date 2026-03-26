#!/usr/bin/env bash
# Claude Auto SEO — Install Script
# Usage: ./install.sh OR curl -fsSL <raw_url>/install.sh | bash

set -e

BOLD='\033[1m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

SKILL_DIR="${HOME}/.claude/skills"
AGENTS_DIR="${HOME}/.claude/agents"
COMMANDS_DIR="${HOME}/.claude/commands"
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "${BOLD}${BLUE}"
echo "  ╔═══════════════════════════════════════╗"
echo "  ║     Claude Auto SEO — Installer       ║"
echo "  ║   Full Automated SEO Platform v1.0    ║"
echo "  ╚═══════════════════════════════════════╝"
echo -e "${NC}"

# Check Claude Code
if ! command -v claude &> /dev/null; then
  echo -e "${RED}✗ Claude Code not found. Install from: https://claude.ai/claude-code${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Claude Code found${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
  echo -e "${RED}✗ Python 3 not found. Please install Python 3.8+${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Python 3 found: $(python3 --version)${NC}"

# Create directories
mkdir -p "$SKILL_DIR" "$AGENTS_DIR" "$COMMANDS_DIR"

echo -e "\n${BOLD}Installing skills...${NC}"

# Install skills
for skill_dir in "$REPO_DIR"/skills/*/; do
  skill_name=$(basename "$skill_dir")
  if [ -d "$skill_dir" ]; then
    cp -r "$skill_dir" "$SKILL_DIR/$skill_name"
    echo -e "  ${GREEN}✓${NC} Installed skill: $skill_name"
  fi
done

echo -e "\n${BOLD}Installing agents...${NC}"

# Install agents
for agent_file in "$REPO_DIR"/agents/*.md; do
  if [ -f "$agent_file" ]; then
    cp "$agent_file" "$AGENTS_DIR/"
    echo -e "  ${GREEN}✓${NC} Installed agent: $(basename "$agent_file")"
  fi
done

echo -e "\n${BOLD}Installing commands...${NC}"

# Install .claude commands
if [ -d "$REPO_DIR/.claude/commands" ]; then
  for cmd_file in "$REPO_DIR"/.claude/commands/*.md; do
    if [ -f "$cmd_file" ]; then
      cp "$cmd_file" "$COMMANDS_DIR/"
      echo -e "  ${GREEN}✓${NC} Installed command: $(basename "$cmd_file")"
    fi
  done
fi

echo -e "\n${BOLD}Installing Python dependencies...${NC}"
if [ -f "$REPO_DIR/requirements.txt" ]; then
  pip3 install -r "$REPO_DIR/requirements.txt" --quiet && \
    echo -e "${GREEN}✓ Python dependencies installed${NC}" || \
    echo -e "${YELLOW}⚠ Could not install some Python packages. Run: pip3 install -r requirements.txt${NC}"
fi

# Copy context templates if not already present
echo -e "\n${BOLD}Setting up context templates...${NC}"
for ctx_file in "$REPO_DIR"/context/*.md; do
  fname=$(basename "$ctx_file")
  dest="$REPO_DIR/context/$fname"
  if [ ! -f "$dest" ]; then
    cp "$ctx_file" "$dest"
    echo -e "  ${GREEN}✓${NC} Created: context/$fname"
  else
    echo -e "  ${YELLOW}→${NC} Skipped (exists): context/$fname"
  fi
done

echo -e "\n${GREEN}${BOLD}✅ Claude Auto SEO installed successfully!${NC}"
echo -e "\n${BOLD}Quick Start:${NC}"
echo -e "  1. ${BLUE}cd claude-auto-seo${NC}"
echo -e "  2. ${BLUE}Edit context/ files with your site info${NC}"
echo -e "  3. ${BLUE}Edit config/site.json with your site URL${NC}"
echo -e "  4. ${BLUE}claude${NC} (start Claude Code)"
echo -e "  5. ${BLUE}/seo audit https://yoursite.com${NC}"
echo ""
echo -e "${BOLD}Available commands:${NC} /seo audit, /seo report, /content write, /seo rank-track, and 40+ more"
echo -e "${BOLD}Docs:${NC} See README.md or docs/"
echo ""

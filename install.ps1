# Claude Auto SEO - Windows Installer
# Usage: .\install.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "  ==========================================" -ForegroundColor Blue
Write-Host "       Claude Auto SEO - Installer          " -ForegroundColor Blue
Write-Host "     Full Automated SEO Platform v1.0       " -ForegroundColor Blue
Write-Host "  ==========================================" -ForegroundColor Blue
Write-Host ""

$SKILL_DIR = "$env:USERPROFILE\.claude\skills"
$AGENTS_DIR = "$env:USERPROFILE\.claude\agents"
$COMMANDS_DIR = "$env:USERPROFILE\.claude\commands"
$REPO_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path

# Check Claude Code
if (-not (Get-Command claude -ErrorAction SilentlyContinue)) {
    Write-Host "X Claude Code not found. Install from: https://claude.ai/claude-code" -ForegroundColor Red
    exit 1
}
Write-Host "OK Claude Code found" -ForegroundColor Green

# Check Python
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "X Python not found. Install from: https://python.org" -ForegroundColor Red
    exit 1
}
Write-Host "OK Python found" -ForegroundColor Green

# Create directories
New-Item -ItemType Directory -Force -Path $SKILL_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $AGENTS_DIR | Out-Null
New-Item -ItemType Directory -Force -Path $COMMANDS_DIR | Out-Null

Write-Host ""
Write-Host "Installing skills..." -ForegroundColor Yellow
Get-ChildItem "$REPO_DIR\skills" -Directory | ForEach-Object {
    Copy-Item $_.FullName "$SKILL_DIR\$($_.Name)" -Recurse -Force
    Write-Host "  OK Installed skill: $($_.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installing agents..." -ForegroundColor Yellow
Get-ChildItem "$REPO_DIR\agents" -Filter "*.md" | ForEach-Object {
    Copy-Item $_.FullName "$AGENTS_DIR\" -Force
    Write-Host "  OK Installed agent: $($_.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installing commands..." -ForegroundColor Yellow
Get-ChildItem "$REPO_DIR\.claude\commands" -Filter "*.md" | ForEach-Object {
    Copy-Item $_.FullName "$COMMANDS_DIR\" -Force
    Write-Host "  OK Installed command: $($_.Name)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Installing Python dependencies..." -ForegroundColor Yellow
if (Test-Path "$REPO_DIR\requirements.txt") {
    pip install -r "$REPO_DIR\requirements.txt" --quiet
    Write-Host "OK Python dependencies installed" -ForegroundColor Green
}

Write-Host ""
Write-Host "Claude Auto SEO installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Quick Start:"
Write-Host "  1. Edit context/ files with your site info"
Write-Host "  2. Edit config/site.json with your site URL"
Write-Host "  3. Run: claude"
Write-Host "  4. Run: /seo audit {your domain name}}"
Write-Host ""
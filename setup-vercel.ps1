param(
    [string]$ProjectName = "enterprise-autopilot-agent",
    [switch]$Prod
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $Root

Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Enterprise AI Autopilot — Vercel Setup " -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# ── 1. Check Vercel CLI ──────────────────────────────────────────────
$vercel = Get-Command "vercel" -ErrorAction SilentlyContinue
if (-not $vercel) {
    Write-Host "[...] Installing Vercel CLI..." -ForegroundColor Yellow
    npm install -g vercel
}
Write-Host "[OK] Vercel CLI found" -ForegroundColor Green

# ── 2. Install frontend deps ─────────────────────────────────────────
Write-Host ""
Write-Host "[...] Installing frontend dependencies..." -ForegroundColor Yellow
Set-Location "$Root/frontend"
npm install
if ($LASTEXITCODE -ne 0) { throw "npm install failed" }
Write-Host "[OK] Frontend dependencies installed" -ForegroundColor Green

# ── 3. Build frontend ────────────────────────────────────────────────
Write-Host ""
Write-Host "[...] Building frontend..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) { throw "Frontend build failed" }
Write-Host "[OK] Frontend built successfully" -ForegroundColor Green

# ── 4. Link or deploy ────────────────────────────────────────────────
Set-Location $Root

if ($Prod) {
    Write-Host ""
    Write-Host "[...] Deploying to Vercel (production)..." -ForegroundColor Yellow
    vercel --prod --yes
} else {
    Write-Host ""
    Write-Host "[...] Deploying to Vercel (preview)..." -ForegroundColor Yellow
    vercel --yes
}

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host " Deployment initiated successfully!      " -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Set these environment variables in your Vercel dashboard:" -ForegroundColor Yellow
    Write-Host "  - DASHSCOPE_API_KEY  : Your Qwen Cloud API key" -ForegroundColor White
    Write-Host "  - SECRET_KEY        : A random secret string" -ForegroundColor White
    Write-Host "  - SENDGRID_API_KEY  : (optional) For email" -ForegroundColor White
    Write-Host "  - SLACK_BOT_TOKEN   : (optional) For Slack" -ForegroundColor White
    Write-Host ""
    Write-Host "Go to: https://vercel.com/dashboard -> your project -> Settings -> Environment Variables"
    Write-Host ""
}

Set-Location $Root

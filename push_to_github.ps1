# Script to push Open Pandas-AI to GitHub
# Usage: .\push_to_github.ps1

Write-Host "🚀 Preparing to push Open Pandas-AI to GitHub..." -ForegroundColor Cyan

# Check if git is initialized
if (-not (Test-Path .git)) {
    Write-Host "❌ Git repository not initialized. Run 'git init' first." -ForegroundColor Red
    exit 1
}

# Check if there are changes
$status = git status --porcelain
if (-not $status) {
    Write-Host "✅ No changes to commit." -ForegroundColor Green
    exit 0
}

Write-Host "`n📋 Current status:" -ForegroundColor Yellow
git status

Write-Host "`n➕ Adding all files..." -ForegroundColor Cyan
git add .

Write-Host "`n📝 Files staged:" -ForegroundColor Yellow
git status --short

Write-Host "`n💾 Committing changes..." -ForegroundColor Cyan
$commitMessage = Read-Host "Enter commit message (or press Enter for default)"
if ([string]::IsNullOrWhiteSpace($commitMessage)) {
    $commitMessage = "Update documentation and add GitHub configuration files"
}

git commit -m $commitMessage

Write-Host "`n📤 Pushing to GitHub..." -ForegroundColor Cyan
$branch = git branch --show-current
Write-Host "Branch: $branch" -ForegroundColor Yellow

$push = Read-Host "Push to GitHub? (y/n)"
if ($push -eq "y" -or $push -eq "Y") {
    git push origin $branch
    Write-Host "`n✅ Successfully pushed to GitHub!" -ForegroundColor Green
} else {
    Write-Host "`n⏸️  Push cancelled. Run 'git push' manually when ready." -ForegroundColor Yellow
}

Write-Host "`n✨ Done!" -ForegroundColor Green

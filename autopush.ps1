# Get commit message from user
$message = Read-Host -Prompt "Enter commit label/message"

# Fallback if no message is provided
if ([string]::IsNullOrWhiteSpace($message)) {
    $message = "Auto-update $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

Write-Host "Staging files..." -ForegroundColor Cyan
git add .

Write-Host "Creating commit..." -ForegroundColor Cyan
git commit -m "$message"

Write-Host "Pushing to GitHub..." -ForegroundColor Cyan
git push

Write-Host "Done! Successfully pushed to remote." -ForegroundColor Green
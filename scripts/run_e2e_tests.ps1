# ============================================================================
# E2E Test Runner for Open Pandas-AI (Windows PowerShell)
# ============================================================================

param(
    [switch]$Headed,
    [switch]$SkipInstall,
    [int]$Port = 8501
)

$ErrorActionPreference = "Stop"

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Open Pandas-AI E2E Test Runner" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Check if Docker is available
$dockerAvailable = $null -ne (Get-Command docker -ErrorAction SilentlyContinue)

if (-not $SkipInstall) {
    Write-Host "`n[1/4] Installing Playwright browsers..." -ForegroundColor Yellow
    python -m playwright install chromium
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to install Playwright browsers" -ForegroundColor Red
        exit 1
    }
}

# Start the application
Write-Host "`n[2/4] Starting application..." -ForegroundColor Yellow

$appProcess = $null
if ($dockerAvailable) {
    Write-Host "Using Docker Compose..." -ForegroundColor Gray
    docker-compose up -d
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Docker Compose failed, falling back to direct Streamlit" -ForegroundColor Yellow
        $appProcess = Start-Process -FilePath "streamlit" -ArgumentList "run", "app.py", "--server.port=$Port", "--server.headless=true" -PassThru -NoNewWindow
    }
} else {
    Write-Host "Starting Streamlit directly..." -ForegroundColor Gray
    $appProcess = Start-Process -FilePath "streamlit" -ArgumentList "run", "app.py", "--server.port=$Port", "--server.headless=true" -PassThru -NoNewWindow
}

# Wait for the application to be ready
Write-Host "`n[3/4] Waiting for application to be ready..." -ForegroundColor Yellow
$maxRetries = 30
$retryCount = 0
$appReady = $false

while (-not $appReady -and $retryCount -lt $maxRetries) {
    Start-Sleep -Seconds 2
    $retryCount++
    
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:$Port" -UseBasicParsing -TimeoutSec 5 -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $appReady = $true
            Write-Host "Application is ready!" -ForegroundColor Green
        }
    } catch {
        Write-Host "Waiting... ($retryCount/$maxRetries)" -ForegroundColor Gray
    }
}

if (-not $appReady) {
    Write-Host "Application failed to start within timeout" -ForegroundColor Red
    if ($appProcess) { Stop-Process -Id $appProcess.Id -Force -ErrorAction SilentlyContinue }
    if ($dockerAvailable) { docker-compose down }
    exit 1
}

# Run E2E tests
Write-Host "`n[4/4] Running E2E tests..." -ForegroundColor Yellow

$env:E2E_BASE_URL = "http://localhost:$Port"

$pytestArgs = @("tests/e2e/", "-v", "-m", "e2e")
if ($Headed) {
    $pytestArgs += "--headed"
}

try {
    pytest @pytestArgs
    $testResult = $LASTEXITCODE
} finally {
    # Cleanup
    Write-Host "`nCleaning up..." -ForegroundColor Yellow
    
    if ($appProcess) {
        Stop-Process -Id $appProcess.Id -Force -ErrorAction SilentlyContinue
    }
    
    if ($dockerAvailable) {
        docker-compose down
    }
}

Write-Host "`n============================================" -ForegroundColor Cyan
if ($testResult -eq 0) {
    Write-Host "E2E Tests PASSED" -ForegroundColor Green
} else {
    Write-Host "E2E Tests FAILED" -ForegroundColor Red
}
Write-Host "============================================" -ForegroundColor Cyan

exit $testResult

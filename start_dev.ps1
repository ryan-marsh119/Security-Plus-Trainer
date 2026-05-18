$root = $PSScriptRoot

Write-Host "Starting database..." -ForegroundColor Cyan
docker compose up -d db

# Poll until PostgreSQL accepts connections (up to 30s)
Write-Host "Waiting for PostgreSQL..." -ForegroundColor Cyan
$ready = $false
for ($i = 0; $i -lt 30; $i++) {
    docker compose exec -T db pg_isready -U secplus_user -d securityplus 2>&1 | Out-Null
    if ($LASTEXITCODE -eq 0) { $ready = $true; break }
    Start-Sleep -Seconds 1
}
if (-not $ready) {
    Write-Host "PostgreSQL did not become ready in 30s — check 'docker compose logs db'" -ForegroundColor Red
    exit 1
}
Write-Host "Database ready." -ForegroundColor Green

# Run any pending migrations
Write-Host "Running migrations..." -ForegroundColor Cyan
& "$root\venv\Scripts\python" "$root\backend\manage.py" migrate
if ($LASTEXITCODE -ne 0) {
    Write-Host "Migrations failed — aborting." -ForegroundColor Red
    exit 1
}

# Open backend and frontend in separate terminal windows
Write-Host "Starting backend  -> http://localhost:8000" -ForegroundColor Cyan
Start-Process powershell.exe `
    -ArgumentList "-NoExit", "-Command", "cd '$root\backend'; ..\venv\Scripts\python manage.py runserver" `
    -WindowStyle Normal

Write-Host "Starting frontend -> http://localhost:5173" -ForegroundColor Cyan
Start-Process powershell.exe `
    -ArgumentList "-NoExit", "-Command", "cd '$root\frontend'; npm run dev" `
    -WindowStyle Normal

Write-Host ""
Write-Host "All services started." -ForegroundColor Green
Write-Host "  Backend  http://localhost:8000" -ForegroundColor White
Write-Host "  Frontend http://localhost:5173" -ForegroundColor White
Write-Host "  Admin    http://localhost:8000/admin  (admin / admin1234)" -ForegroundColor White

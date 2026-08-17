param(
    [int]$WaitSeconds = 240
)

Write-Host "Starting AVIP DB migration helper"

# Prereqs: Docker Desktop and docker compose available in PATH
try {
    docker --version | Out-Null
} catch {
    Write-Error "Docker is not available in PATH. Install Docker Desktop and ensure 'docker' is on PATH."
    exit 1
}

# Start postgres and redis services
Write-Host "Bringing up postgres and redis via docker compose..."
docker compose up -d postgres redis

# Wait for Postgres to accept connections
$tries = [int]([math]::Ceiling($WaitSeconds / 2))
for ($i = 1; $i -le $tries; $i++) {
    if ((Test-NetConnection -ComputerName 'localhost' -Port 5432).TcpTestSucceeded) {
        Write-Host "Postgres reachable on attempt $i"
        break
    }
    Write-Host "Waiting for Postgres... attempt $i of $tries"
    Start-Sleep -Seconds 2
}

if (-not (Test-NetConnection -ComputerName 'localhost' -Port 5432).TcpTestSucceeded) {
    Write-Error "Postgres did not become ready within $WaitSeconds seconds. Check docker compose logs: docker compose logs postgres"
    exit 1
}

# Set DATABASE_URL for this session
$env:DATABASE_URL = 'postgresql+psycopg://avip:avip@localhost:5432/avip'
Write-Host "Using DATABASE_URL=$env:DATABASE_URL"

# Run Alembic upgrade
Write-Host "Applying Alembic migrations (upgrade head)..."
$alembicExit = & alembic -c alembic.ini upgrade head
if ($LASTEXITCODE -ne 0) {
    Write-Error "Alembic upgrade head failed. See output above."
    exit $LASTEXITCODE
}
Write-Host "Alembic migrations applied successfully."

# Create temp python script to list tables
$py = @"
from sqlalchemy import create_engine, text
import os
engine = create_engine(os.environ['DATABASE_URL'])
with engine.connect() as conn:
    res = conn.execute(text("SELECT tablename FROM pg_catalog.pg_tables WHERE schemaname='public';"))
    print('tables:', [r[0] for r in res])
"@

$pyPath = Join-Path $env:TEMP 'avip_list_tables.py'
Set-Content -Path $pyPath -Value $py -Encoding UTF8

Write-Host "Listing DB tables:"
python $pyPath

Remove-Item $pyPath -ErrorAction SilentlyContinue

Write-Host "Migration script completed."

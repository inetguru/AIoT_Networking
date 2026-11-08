# Web_Intro 사전 점검: WSL, Docker, 포트, 실습 이미지
$image = "ghcr.io/inetguru/aiot-lab:node24"
$ok = $true

function Report($pass, $msg, $hint) {
    if ($pass) { Write-Host "[OK]   $msg" -ForegroundColor Green }
    else { Write-Host "[FAIL] $msg" -ForegroundColor Red; if ($hint) { Write-Host "       -> $hint" }; $script:ok = $false }
}

# 1. WSL
$wslOut = (wsl -l -v 2>&1 | Out-String) -replace "`0", ""
Report ($wslOut -match "\s2\s*$" -or $wslOut -match "\s2\r?\n") "WSL 2 배포판 확인" "관리자 PowerShell에서 'wsl --install' 후 재부팅"

# 2. Docker 엔진
docker info *> $null
Report ($LASTEXITCODE -eq 0) "Docker 엔진 실행 중" "Docker Desktop을 실행하고 'Engine running' 이 될 때까지 기다리세요"

# 3. 포트 3000, 4000
foreach ($p in 3000, 4000) {
    $used = Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue
    Report (-not $used) "포트 $p 사용 가능" "포트 $p 를 쓰는 프로그램을 종료하거나 'docker compose down' 실행"
}

# 4. 실습 이미지
if ($ok) {
    Write-Host "실습 이미지를 내려받는 중... (처음 한 번만)"
    docker pull $image
    Report ($LASTEXITCODE -eq 0) "실습 이미지 준비" "네트워크 확인 또는 강사가 준 tar 파일: docker load -i aiot-lab.tar"
}

if ($ok) { Write-Host "`n모든 점검 통과. 수업 준비 완료!" -ForegroundColor Green }
else { Write-Host "`n위 [FAIL] 항목을 해결한 뒤 다시 실행하세요." -ForegroundColor Yellow }

$ErrorActionPreference = 'Stop'
$base = 'C:\Users\admin\DSH\tools\mysql57'
$bin = Join-Path $base 'bin'
$data = Join-Path $base 'data'
$ini = Join-Path $base 'my.ini'

if (-not (Test-Path $data)) {
    New-Item -ItemType Directory -Path $data | Out-Null
    & (Join-Path $bin 'mysqld.exe') --no-defaults --initialize-insecure --basedir=$base --datadir=$data 2>&1 | Out-String
    Write-Output 'initialized'
}

$iniContent = @"
[mysqld]
basedir=$base
datadir=$data
port=3306
bind-address=127.0.0.1
character-set-server=utf8mb4
collation-server=utf8mb4_general_ci
max_connections=300
explicit_defaults_for_timestamp=ON
[client]
port=3306
default-character-set=utf8mb4
"@
Set-Content -Path $ini -Value $iniContent -Encoding ASCII

# try to install/start as a Windows service (needs admin)
$svc = Get-Service -Name MySQLDSH -ErrorAction SilentlyContinue
if (-not $svc) {
    sc.exe create MySQLDSH binPath= "`"$(Join-Path $bin 'mysqld.exe')`" --defaults-file=`"$ini`"" start= auto 2>&1 | Out-String
}
try {
    Start-Service MySQLDSH -ErrorAction Stop
    Write-Output 'service started'
}
catch {
    Write-Output ('service start failed: ' + $_.Exception.Message + ' -> running as background process')
    $proc = Get-Process mysqld -ErrorAction SilentlyContinue
    if (-not $proc) {
        Start-Process -FilePath (Join-Path $bin 'mysqld.exe') -ArgumentList "--defaults-file=`"$ini`"" -WindowStyle Hidden
        Start-Sleep -Seconds 6
    }
}

# wait for port
$ok = $false
for ($i = 0; $i -lt 20; $i++) {
    $conn = Test-NetConnection -ComputerName 127.0.0.1 -Port 3306 -WarningAction SilentlyContinue
    if ($conn.TcpTestSucceeded) { $ok = $true; break }
    Start-Sleep -Seconds 2
}
Write-Output ("port3306: " + $ok)

$mysql = Join-Path $bin 'mysql.exe'
& $mysql -u root --skip-password -e "ALTER USER 'root'@'localhost' IDENTIFIED BY '123456'; FLUSH PRIVILEGES;" 2>&1 | Out-String
& $mysql -u root -p123456 -e "SELECT VERSION();" 2>&1 | Out-String

$ok = 0; $fail = 0
for ($i = 1; $i -le 10; $i++) {
  $sw = [Diagnostics.Stopwatch]::StartNew()
  try {
    $r = Invoke-WebRequest -Uri 'http://127.0.0.1:8090/prod-api/login' -Method Post -ContentType 'application/json' -Body '{"username":"admin","password":"admin123","code":"","uuid":""}' -UseBasicParsing -TimeoutSec 10
    if ($r.StatusCode -eq 200 -and $r.Content -match '"code":200') { $ok++ } else { $fail++; Write-Output "  第 $i 次异常: $($r.Content.Substring(0,60))" }
    Write-Output ("  第 {0} 次: {1}ms" -f $i, $sw.ElapsedMilliseconds)
  } catch { $fail++; Write-Output "  第 $i 次 FAIL: $($_.Exception.Message)" }
}
Write-Output ("压测结果: 成功 {0} / 失败 {1}" -f $ok, $fail)
$reg = Get-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings' -ErrorAction SilentlyContinue
Write-Output ("ProxyEnable={0} ProxyServer={1} AutoConfigURL={2}" -f $reg.ProxyEnable, $reg.ProxyServer, $reg.AutoConfigURL)

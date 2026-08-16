param(
    [Parameter(Mandatory = $true)][string]$SrcDir,
    [Parameter(Mandatory = $true)][string]$OutDir
)
$ErrorActionPreference = 'Continue'
New-Item -ItemType Directory -Force -Path $OutDir | Out-Null
$files = @(Get-ChildItem -LiteralPath $SrcDir -File | Where-Object { $_.Extension -eq '.doc' })
foreach ($f in $files) {
    $out = Join-Path $OutDir ($f.BaseName + '.docx')
    if (Test-Path $out) { Write-Output "skip $($f.Name)"; continue }
    $word = $null
    try {
        $word = New-Object -ComObject Word.Application
        $word.Visible = $false
        $doc = $word.Documents.Open($f.FullName, $false, $true)
        $doc.SaveAs($out, 12)
        $doc.Close($false)
        Write-Output "converted $($f.Name)"
    }
    catch {
        Write-Output ("FAILED " + $f.Name + " : " + $_.Exception.Message)
    }
    finally {
        if ($word) {
            try { $word.Quit() } catch { }
            try { [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null } catch { }
        }
        Start-Sleep -Milliseconds 300
    }
}
Get-Process WINWORD -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

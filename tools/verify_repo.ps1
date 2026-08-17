$ErrorActionPreference = 'SilentlyContinue'
function Get-TreeHash($root) {
  $map = @{}
  Get-ChildItem $root -Recurse -File | ForEach-Object {
    $rel = $_.FullName.Substring($root.Length).TrimStart('\')
    $map[$rel] = (Get-FileHash $_.FullName -Algorithm SHA1).Hash
  }
  return $map
}

# 第一步：沙盒拉取 vs 本地提交源（Huahuagongkao）
$sandbox = 'C:\Users\admin\DSH\verify-clone'
$source = 'C:\Users\admin\DSH\Huahuagongkao'
$a = Get-TreeHash $sandbox
$b = Get-TreeHash $source
$diff = @()
foreach ($k in $a.Keys) {
  if (-not $b.ContainsKey($k)) { $diff += "仅沙盒有: $k" }
  elseif ($a[$k] -ne $b[$k]) { $diff += "内容不同: $k" }
}
foreach ($k in $b.Keys) { if (-not $a.ContainsKey($k)) { $diff += "仅本地提交源有: $k" } }
"【第1步】GitHub拉取 vs 本地提交源: 共 $($a.Count) 文件"
if ($diff.Count) { $diff | Select-Object -First 15 } else { '  ✓ 100% 一致，无任何差异' }

# 第二步：本地提交源 vs 真实运行源码（映射关键目录）
$checks = @(
  @('ruoyi\src', 'C:\Users\admin\DSH\ruoyi\src'),
  @('ruoyi\public\docs', 'C:\Users\admin\DSH\ruoyi\public\docs'),
  @('ruoyi\server.cjs', 'C:\Users\admin\DSH\ruoyi\server.cjs'),
  @('ruoyi\vite.config.js', 'C:\Users\admin\DSH\ruoyi\vite.config.js'),
  @('ruoyi\package.json', 'C:\Users\admin\DSH\ruoyi\package.json'),
  @('ruoyi\index.html', 'C:\Users\admin\DSH\ruoyi\index.html'),
  @('ruoyi\.env.production', 'C:\Users\admin\DSH\ruoyi\.env.production'),
  @('ruoyi-backend\ruoyi-admin\src', 'C:\Users\admin\DSH\ruoyi-backend\ruoyi-admin\src'),
  @('ruoyi-backend\ruoyi-system\src', 'C:\Users\admin\DSH\ruoyi-backend\ruoyi-system\src'),
  @('ruoyi-backend\ruoyi-framework\src', 'C:\Users\admin\DSH\ruoyi-backend\ruoyi-framework\src'),
  @('ruoyi-backend\pom.xml', 'C:\Users\admin\DSH\ruoyi-backend\pom.xml')
)
"【第2步】本地提交源 vs 真实运行代码:"
foreach ($c in $checks) {
  $srcPath = Join-Path $source $c[0]
  if (Test-Path $srcPath -PathType Container) {
    $m1 = Get-TreeHash $srcPath
    $m2 = Get-TreeHash $c[1]
    $bad = @()
    foreach ($k in $m1.Keys) { if (-not $m2.ContainsKey($k) -or $m2[$k] -ne $m1[$k]) { $bad += $k } }
    foreach ($k in $m2.Keys) { if (-not $m1.ContainsKey($k)) { $bad += $k } }
    if ($bad.Count) { "  ✗ $($c[0]): $($bad.Count) 处差异"; $bad | Select-Object -First 3 } else { "  ✓ $($c[0]): 一致 ($($m1.Count) 文件)" }
  } else {
    $h1 = (Get-FileHash $srcPath -Algorithm SHA1).Hash
    $h2 = (Get-FileHash $c[1] -Algorithm SHA1).Hash
    if ($h1 -eq $h2) { "  ✓ $($c[0]): 一致" } else { "  ✗ $($c[0]): 内容不同!" }
  }
}

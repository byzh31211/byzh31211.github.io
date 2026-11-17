# 一键发布: 编译 -> 提交 -> 推送
# 用法:  .\publish.ps1                 或   .\publish.ps1 "自定义提交信息"

param([string]$Message = "")

$ErrorActionPreference = "Stop"
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# git 会把进度信息写到 stderr（不是错误），这里不能按异常处理
$ErrorActionPreference = "Continue"

function Invoke-Git {
    git @args 2>&1 | ForEach-Object { Write-Host "   $_" }
    return $LASTEXITCODE
}

$py = "E:\py_uv_env\py-3-11-5-opencode\.venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

Write-Host "==> 编译" -ForegroundColor Cyan
& $py build.py
if ($LASTEXITCODE -ne 0) { Write-Host "编译失败, 已中止" -ForegroundColor Red; exit 1 }

Write-Host "==> 检查变更" -ForegroundColor Cyan
$changes = git status --porcelain
if (-not $changes) { Write-Host "没有需要提交的内容" -ForegroundColor Yellow; exit 0 }

$null = Invoke-Git add -A

if ([string]::IsNullOrWhiteSpace($Message)) {
    $Message = "post: $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
}

Write-Host "==> 提交: $Message" -ForegroundColor Cyan
$code = Invoke-Git commit -m $Message
if ($code -ne 0) { Write-Host "提交失败, 已中止" -ForegroundColor Red; exit 1 }

Write-Host "==> 推送" -ForegroundColor Cyan
$code = Invoke-Git push
if ($code -ne 0) { Write-Host "推送失败, 检查 SSH 权限" -ForegroundColor Red; exit 1 }

Write-Host "完成 -> https://byzh31211.github.io (约 1 分钟后生效)" -ForegroundColor Green

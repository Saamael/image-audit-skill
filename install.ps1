$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$targetRoot = if ($args.Count -gt 0) { $args[0] } else { Join-Path $HOME ".claude" }

New-Item -ItemType Directory -Force (Join-Path $targetRoot "skills") | Out-Null
New-Item -ItemType Directory -Force (Join-Path $targetRoot "commands") | Out-Null
$destination = Join-Path (Join-Path $targetRoot "skills") "image-audit"

if (Test-Path $destination) {
    Remove-Item -Recurse -Force $destination
}

Copy-Item -Recurse (Join-Path $root ".claude\skills\image-audit") (Join-Path $targetRoot "skills")
Copy-Item (Join-Path $root ".claude\commands\imageaudit.md") (Join-Path $targetRoot "commands\imageaudit.md")
Write-Host "Installed image-audit to $destination"
Write-Host "Run /imageaudit inside a repo. Use /imageaudit fix to apply safe conversions."

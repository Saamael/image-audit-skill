$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$target = if ($args.Count -gt 0) { $args[0] } else { Join-Path $HOME ".claude\skills" }

New-Item -ItemType Directory -Force $target | Out-Null
$destination = Join-Path $target "image-audit"

if (Test-Path $destination) {
    Remove-Item -Recurse -Force $destination
}

Copy-Item -Recurse (Join-Path $root ".claude\skills\image-audit") $target
Write-Host "Installed image-audit to $target"

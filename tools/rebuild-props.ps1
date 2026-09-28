param(
    # Machine-specific. Set REDBREACH_GODOT and REDBREACH_BLENDER once per machine rather than editing this,
    # or pass -GodotPath / -BlenderPath. The desktop defaults are kept as the last resort.
    [string]$GodotPath = $(if ($env:REDBREACH_GODOT) { $env:REDBREACH_GODOT }
                          else { 'D:\SteamLibrary\steamapps\common\Godot Engine\godot.windows.opt.tools.64.exe' }),
    [string]$BlenderPath = $(if ($env:REDBREACH_BLENDER) { $env:REDBREACH_BLENDER }
                            else { 'D:\SteamLibrary\steamapps\common\Blender\blender.exe' }),
    # Only these props (catalogue names); all of them when left out.
    [string[]]$Props = @(),
    [switch]$Validate,
    [switch]$Capture
)
# Rebuild the props from the catalogue (tools/props.py): Blender builds each model (art/props/<name>.blend, exported to
# RedBreach/props/<category>/<name>.glb), tools/write-props.py writes the Godot side, Godot imports, and the checks run.
$ErrorActionPreference = 'Stop'
$root = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$projectDir = Join-Path $root 'RedBreach'
if (-not (Test-Path -LiteralPath $GodotPath)) { throw "Godot not found at '$GodotPath'. Set `$env:REDBREACH_GODOT or pass -GodotPath." }
if (-not (Test-Path -LiteralPath $BlenderPath)) { throw "Blender not found at '$BlenderPath'. Set `$env:REDBREACH_BLENDER or pass -BlenderPath." }

& python (Join-Path $PSScriptRoot 'props.py') | Select-Object -Last 3
if ($LASTEXITCODE -ne 0) { throw "the prop catalogue has problems (python tools/props.py)" }

$blenderArgs = @('--background', '--factory-startup', '--python', (Join-Path $PSScriptRoot 'build-props-blender.py'))
if ($Props.Count -gt 0) { $blenderArgs += @('--') + $Props }
# Blender writes its log to stderr as well: collect it without letting PowerShell treat that as a failure.
$ErrorActionPreference = 'Continue'
$out = & $BlenderPath @blenderArgs 2>&1 | ForEach-Object { "$_" }
$ErrorActionPreference = 'Stop'
$out | Select-String -Pattern '^(PROP|PROPS_BLENDER|Error|Traceback)' | ForEach-Object { $_.Line }
if (-not ($out | Select-String -Pattern '^PROPS_BLENDER: ' -Quiet)) { throw "the Blender build did not finish" }

function Import-Project {
    $import = Start-Process -FilePath $GodotPath -ArgumentList @('--headless', '--path', ('"' + $projectDir + '"'), '--import') -WindowStyle Hidden -PassThru -Wait
    if ($import.ExitCode -ne 0) { throw "import failed with exit code $($import.ExitCode)" }
}
# A new model is imported once so Godot writes its import settings; write-props.py then maps its materials onto the
# level's own, and the models are imported again with that mapping.
Import-Project
& python (Join-Path $PSScriptRoot 'write-props.py')
if ($LASTEXITCODE -ne 0) { throw "write-props.py failed" }
Get-ChildItem -Path (Join-Path $projectDir 'props') -Filter *.glb -Recurse | ForEach-Object {
    Get-ChildItem -Path (Join-Path $projectDir '.godot\imported') -Filter ($_.Name + '-*') -ErrorAction SilentlyContinue | Remove-Item -Force
}
Import-Project

$checks = @()
if ($Validate) { $checks += ,@('res://tools/validate_props.gd', 'props_qa.log', '^PROPS_QA: \d+ checks; 0 failures$') }
if ($Capture) { $checks += ,@('res://tools/capture_props.gd', 'props_capture.log', '^PROPS_CAPTURE: PASS') }
foreach ($entry in $checks) {
    $logPath = Join-Path $projectDir ('.godot\' + $entry[1])
    $runArgs = @('--path', ('"' + $projectDir + '"'), '--log-file', ('"' + $logPath + '"'), '--script', $entry[0])
    if ($entry[0] -notlike '*capture*') { $runArgs = @('--headless') + $runArgs }
    $run = Start-Process -FilePath $GodotPath -ArgumentList $runArgs -WindowStyle Hidden -PassThru -Wait
    Get-Content -LiteralPath $logPath | Select-String -Pattern '^(FAIL|PROPS_QA|PROPS_CAPTURE|SCRIPT ERROR|ERROR)' | ForEach-Object { $_.Line }
    if ($run.ExitCode -ne 0) { throw "$($entry[0]) failed with exit code $($run.ExitCode)" }
    if (Select-String -LiteralPath $logPath -Pattern '^(SCRIPT ERROR:|ERROR:|FAIL:)' -Quiet) { throw "$($entry[0]) reported errors; see $logPath" }
    if (-not (Select-String -LiteralPath $logPath -Pattern $entry[2] -Quiet)) { throw "$($entry[0]) did not finish; see $logPath" }
}
